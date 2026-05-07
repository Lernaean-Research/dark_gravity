#!/usr/bin/env python3
"""Run and aggregate a deterministic multi-seed sweep for the IRS cluster toy model."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quantile(values: Sequence[float], q: float) -> float:
    sorted_vals = sorted(values)
    if not sorted_vals:
        raise ValueError("empty sequence")
    if q <= 0.0:
        return sorted_vals[0]
    if q >= 1.0:
        return sorted_vals[-1]
    index = q * (len(sorted_vals) - 1)
    low = int(index)
    high = min(low + 1, len(sorted_vals) - 1)
    weight = index - low
    return sorted_vals[low] * (1.0 - weight) + sorted_vals[high] * weight


def build_seed_list(base_seed: int, count: int, step: int) -> List[int]:
    return [base_seed + idx * step for idx in range(count)]


def run_seed(
    python_exe: Path,
    model_script: Path,
    seed: int,
    output_dir: Path,
    satellites: int,
    gas_nodes: int,
    max_order: int,
    radial_points: int,
    shell_directions: int,
    enable_time_memory: bool,
    tau_mem_myr: float,
    assembly_time_myr: float,
    assembly_alpha: float,
    mode_tau_power: float,
    ez_tau_power: float = 0.0,
    ez_ref_z: float = 0.2,
) -> Dict[str, object]:
    seed_dir = output_dir / f"seed_{seed}"
    cmd = [
        str(python_exe),
        str(model_script),
        "--seed",
        str(seed),
        "--satellites",
        str(satellites),
        "--gas-nodes",
        str(gas_nodes),
        "--max-order",
        str(max_order),
        "--radial-points",
        str(radial_points),
        "--shell-directions",
        str(shell_directions),
        "--output-dir",
        str(seed_dir),
    ]
    if enable_time_memory:
        cmd.extend(
            [
                "--enable-time-memory",
                "--tau-mem-myr",
                str(tau_mem_myr),
                "--assembly-time-myr",
                str(assembly_time_myr),
                "--assembly-alpha",
                str(assembly_alpha),
                "--mode-tau-power",
                str(mode_tau_power),
            ]
        )
    if ez_tau_power != 0.0:
        cmd.extend(["--ez-tau-power", str(ez_tau_power), "--ez-ref-z", str(ez_ref_z)])
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    summary_path = seed_dir / "toy_cluster_summary.json"
    if completed.returncode != 0 or not summary_path.exists():
        raise RuntimeError(
            f"Seed {seed} failed: exit={completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )

    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)

    gates = summary["gates"]
    key_r500 = summary["key_rows"]["at_r500"]
    key_half = summary["key_rows"]["at_half_r500"]
    key_outer = summary["key_rows"]["at_outer"]
    failed_gates = sorted(name for name, gate in gates.items() if not gate["pass"])
    return {
        "seed": seed,
        "all_pass": not failed_gates,
        "failed_gate_count": len(failed_gates),
        "failed_gates": "|".join(failed_gates),
        "closure_half_r500": key_half["closure_full"],
        "closure_r500_ground": key_r500["closure_ground"],
        "closure_r500_full": key_r500["closure_full"],
        "closure_outer": key_outer["closure_full"],
        "higher_mode_fraction_r500": key_r500["higher_mode_fraction"],
        "baryon_fraction_r500": key_r500["baryon_fraction_full"],
        "sigma_pred_r500": gates["velocity_dispersion_anchor"]["value"],
        "sigma_anchor": gates["velocity_dispersion_anchor"]["reference"],
        "mean_eta_gas": statistics.mean(
            row["eta_eff"]
            for row in read_sources(seed_dir / "toy_cluster_sources.csv")
            if row["kind"] == "gas"
        ),
        "mean_eta_galaxies": statistics.mean(
            row["eta_eff"]
            for row in read_sources(seed_dir / "toy_cluster_sources.csv")
            if row["kind"] == "galaxy"
        ),
        "summary_json": str(summary_path),
        "summary_sha256": sha256_file(summary_path),
    }


def read_sources(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "name": row["name"],
                    "kind": row["kind"],
                    "eta_eff": float(row["eta_eff"]),
                }
            )
    return rows


def summarize(results: Sequence[Dict[str, object]]) -> Dict[str, object]:
    metrics = [
        "closure_half_r500",
        "closure_r500_ground",
        "closure_r500_full",
        "closure_outer",
        "higher_mode_fraction_r500",
        "baryon_fraction_r500",
        "sigma_pred_r500",
        "mean_eta_gas",
        "mean_eta_galaxies",
    ]
    aggregate: Dict[str, object] = {
        "seed_count": len(results),
        "pass_count": sum(1 for row in results if row["all_pass"]),
        "pass_fraction": sum(1 for row in results if row["all_pass"]) / max(len(results), 1),
        "metrics": {},
        "fragile_gates": {},
        "worst_seeds_by_r500_closure": [],
        "highest_seeds_by_r500_closure": [],
    }

    for metric in metrics:
        values = [float(row[metric]) for row in results]
        aggregate["metrics"][metric] = {
            "min": min(values),
            "p16": quantile(values, 0.16),
            "median": statistics.median(values),
            "mean": statistics.fmean(values),
            "p84": quantile(values, 0.84),
            "max": max(values),
            "stdev": statistics.pstdev(values),
        }

    gate_names = sorted({gate for row in results for gate in str(row["failed_gates"]).split("|") if gate})
    for gate_name in gate_names:
        failures = [int(row["seed"]) for row in results if gate_name in str(row["failed_gates"]).split("|")]
        aggregate["fragile_gates"][gate_name] = {
            "failure_count": len(failures),
            "failure_fraction": len(failures) / max(len(results), 1),
            "seeds": failures,
        }

    sorted_by_closure = sorted(results, key=lambda row: float(row["closure_r500_full"]))
    aggregate["worst_seeds_by_r500_closure"] = [
        {"seed": int(row["seed"]), "closure_r500_full": float(row["closure_r500_full"])}
        for row in sorted_by_closure[:3]
    ]
    aggregate["highest_seeds_by_r500_closure"] = [
        {"seed": int(row["seed"]), "closure_r500_full": float(row["closure_r500_full"])}
        for row in sorted_by_closure[-3:]
    ]
    return aggregate


def write_csv(path: Path, rows: Sequence[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, metadata: Dict[str, object], results: Sequence[Dict[str, object]], aggregate: Dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# IRS Cluster Eigenmode Seed Sweep\n\n")
        handle.write("## Run Metadata\n")
        handle.write(f"- Generated (UTC): {metadata['generated_utc']}\n")
        handle.write(f"- Seed count: {metadata['seed_count']}\n")
        handle.write(f"- Base seed: {metadata['base_seed']}\n")
        handle.write(f"- Seed step: {metadata['seed_step']}\n")
        handle.write(f"- Satellites: {metadata['satellites']}\n")
        handle.write(f"- ICM nodes: {metadata['gas_nodes']}\n")
        handle.write(f"- Max order: {metadata['max_order']}\n")
        handle.write(f"- Radial points: {metadata['radial_points']}\n\n")

        handle.write("## Ensemble Summary\n")
        handle.write(f"- Pass fraction: {aggregate['pass_fraction']:.3f} ({aggregate['pass_count']}/{aggregate['seed_count']})\n")
        for metric_name in [
            "closure_r500_full",
            "higher_mode_fraction_r500",
            "baryon_fraction_r500",
            "sigma_pred_r500",
        ]:
            stats_row = aggregate["metrics"][metric_name]
            handle.write(
                f"- {metric_name}: mean={stats_row['mean']:.4f}, median={stats_row['median']:.4f}, "
                f"p16={stats_row['p16']:.4f}, p84={stats_row['p84']:.4f}, min={stats_row['min']:.4f}, max={stats_row['max']:.4f}\n"
            )

        handle.write("\n## Fragile Gates\n")
        if aggregate["fragile_gates"]:
            for gate_name, gate_info in aggregate["fragile_gates"].items():
                handle.write(
                    f"- {gate_name}: failures={gate_info['failure_count']}/{aggregate['seed_count']} "
                    f"({gate_info['failure_fraction']:.3f}); seeds={','.join(str(seed) for seed in gate_info['seeds'])}\n"
                )
        else:
            handle.write("- None\n")

        handle.write("\n## Extreme Seeds by R500 Closure\n")
        for row in aggregate["worst_seeds_by_r500_closure"]:
            handle.write(f"- low: seed={row['seed']} closure_r500_full={row['closure_r500_full']:.4f}\n")
        for row in aggregate["highest_seeds_by_r500_closure"]:
            handle.write(f"- high: seed={row['seed']} closure_r500_full={row['closure_r500_full']:.4f}\n")

        handle.write("\n## Per-Seed Results\n")
        for row in results:
            status = "PASS" if row["all_pass"] else "FAIL"
            handle.write(
                f"- seed={row['seed']} status={status} closure_r500_full={float(row['closure_r500_full']):.4f} "
                f"higher_mode_fraction_r500={float(row['higher_mode_fraction_r500']):.4f} "
                f"baryon_fraction_r500={float(row['baryon_fraction_r500']):.4f} failed_gates={row['failed_gates'] or 'none'}\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a multi-seed IRS cluster eigenmode sweep")
    parser.add_argument("--base-seed", type=int, default=20260405, help="First seed in the sweep")
    parser.add_argument("--seed-count", type=int, default=12, help="Number of seeds to run")
    parser.add_argument("--seed-step", type=int, default=10, help="Increment between seeds")
    parser.add_argument("--satellites", type=int, default=24, help="Satellite galaxy count")
    parser.add_argument("--gas-nodes", type=int, default=16, help="ICM node count")
    parser.add_argument("--max-order", type=int, default=5, help="Maximum eigenmode order")
    parser.add_argument("--radial-points", type=int, default=36, help="Number of radial profile points")
    parser.add_argument("--shell-directions", type=int, default=48, help="Directional samples per radius shell")
    parser.add_argument("--enable-time-memory", action="store_true", help="Enable first-order temporal memory lag")
    parser.add_argument("--tau-mem-myr", type=float, default=800.0, help="Base memory timescale in Myr")
    parser.add_argument("--assembly-time-myr", type=float, default=3000.0, help="Assembly timescale at R500 in Myr")
    parser.add_argument("--assembly-alpha", type=float, default=0.7, help="Radial assembly scaling exponent")
    parser.add_argument("--mode-tau-power", type=float, default=1.0, help="Mode-order memory scaling exponent")
    parser.add_argument("--ez-tau-power", type=float, default=0.0, help="E(z) exponent for cosmological tau correction: tau_eff = tau_0 * (E(z)/E(z_ref))^(-nu)")
    parser.add_argument("--ez-ref-z", type=float, default=0.2, help="Reference redshift for E(z) normalisation")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "results" / "irs_cluster_eigenmode_seed_sweep"),
        help="Output directory",
    )
    parser.add_argument(
        "--min-pass-fraction",
        type=float,
        default=0.75,
        help="Return non-zero when the ensemble pass fraction falls below this value",
    )
    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parent
    model_script = repo_dir / "irs_cluster_eigenmode_first_principles.py"
    python_exe = Path(sys.executable)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    seeds = build_seed_list(args.base_seed, args.seed_count, args.seed_step)
    results: List[Dict[str, object]] = []
    for seed in seeds:
        print(f"running_seed={seed}")
        results.append(
            run_seed(
                python_exe=python_exe,
                model_script=model_script,
                seed=seed,
                output_dir=output_dir,
                satellites=args.satellites,
                gas_nodes=args.gas_nodes,
                max_order=args.max_order,
                radial_points=args.radial_points,
                shell_directions=args.shell_directions,
                enable_time_memory=args.enable_time_memory,
                tau_mem_myr=args.tau_mem_myr,
                assembly_time_myr=args.assembly_time_myr,
                assembly_alpha=args.assembly_alpha,
                mode_tau_power=args.mode_tau_power,
                ez_tau_power=args.ez_tau_power,
                ez_ref_z=args.ez_ref_z,
            )
        )

    aggregate = summarize(results)
    metadata = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "base_seed": args.base_seed,
        "seed_count": args.seed_count,
        "seed_step": args.seed_step,
        "satellites": args.satellites,
        "gas_nodes": args.gas_nodes,
        "max_order": args.max_order,
        "radial_points": args.radial_points,
        "shell_directions": args.shell_directions,
        "enable_time_memory": args.enable_time_memory,
        "tau_mem_myr": args.tau_mem_myr,
        "assembly_time_myr": args.assembly_time_myr,
        "assembly_alpha": args.assembly_alpha,
        "mode_tau_power": args.mode_tau_power,
        "ez_tau_power": args.ez_tau_power,
        "ez_ref_z": args.ez_ref_z,
        "python_executable": str(python_exe),
        "model_script": str(model_script),
        "model_script_sha256": sha256_file(model_script),
        "seeds": seeds,
    }

    per_seed_csv = output_dir / "seed_sweep_results.csv"
    summary_json = output_dir / "seed_sweep_summary.json"
    report_md = output_dir / "seed_sweep_report.md"

    write_csv(per_seed_csv, results, list(results[0].keys()))
    with summary_json.open("w", encoding="utf-8") as handle:
        json.dump({"metadata": metadata, "aggregate": aggregate}, handle, indent=2)
    write_report(report_md, metadata, results, aggregate)

    summary_payload = {
        "metadata": metadata,
        "aggregate": aggregate,
        "outputs": {
            "seed_sweep_results.csv": sha256_file(per_seed_csv),
            "seed_sweep_summary.json": sha256_file(summary_json),
            "seed_sweep_report.md": sha256_file(report_md),
        },
    }
    with summary_json.open("w", encoding="utf-8") as handle:
        json.dump(summary_payload, handle, indent=2)

    print(f"pass_fraction={aggregate['pass_fraction']:.4f}")
    print(f"closure_r500_full_mean={aggregate['metrics']['closure_r500_full']['mean']:.4f}")
    print(f"closure_r500_full_p16={aggregate['metrics']['closure_r500_full']['p16']:.4f}")
    print(f"closure_r500_full_p84={aggregate['metrics']['closure_r500_full']['p84']:.4f}")
    print(f"report={report_md}")

    return 0 if aggregate["pass_fraction"] >= args.min_pass_fraction else 1


if __name__ == "__main__":
    raise SystemExit(main())