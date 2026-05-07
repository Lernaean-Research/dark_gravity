"""
SPARC-175 Analysis: BIC comparison and 5-fold CV for IRS vs halo models
=========================================================================
Paper : Kitcey (2026) v5.1  "Intrinsic Response Sector as Dark Gravity:
         A GR-Compatible Candidate Identity for the Cold Dark Matter Role
         (SPARC-175)"
DOI   : 10.5281/zenodo.18799081

PURPOSE
-------
End-to-end analysis pipeline comparing nine rotation-curve models on 171
SPARC galaxies (Lelli et al. 2016 AJ 152, 157) via Bayesian Information
Criterion (BIC) and 5-fold cross-validation (CV-RMSE).

DATA SOURCE
-----------
SPARC Rotmod_LTG/ directory (*_rotmod.dat files, 8-column format):
  Col 0: R       [kpc]       — galactocentric radius
  Col 1: Vobs    [km/s]      — observed circular velocity
  Col 2: errV    [km/s]      — observational error on Vobs
  Col 3: Vgas    [km/s]      — gas contribution to rotation (√(Σ_gas term))
  Col 4: Vdisk   [km/s]      — stellar disk at Υ_disk = 1
  Col 5: Vbul    [km/s]      — stellar bulge at Υ_bul  = 1
  Col 6: SBdisk  [L_⊙/pc²]  — disk surface brightness (imaging, from Spitzer)
  Col 7: SBbul   [L_⊙/pc²]  — bulge surface brightness

Standard mass-to-light ratios (Schombert, McGaugh & Lelli 2019):
  Υ_disk = 0.5  M_⊙/L_⊙ (3.6 μm band)
  Υ_bul  = 0.7  M_⊙/L_⊙

MODELS FITTED  (k = number of free parameters per galaxy)
-----------------------------------------------------------
  resp   (k=1)  IRS Response model, free: Q (amplitude)
  nfw    (k=2)  NFW dark halo, free: M_vir, c
  bur    (k=2)  Burkert dark halo, free: r_0, ρ_0
  rsig   (k=2)  IRS + free Gaussian σ, free: Q, σ
  rydk   (k=2)  IRS + free Υ_disk, free: Q, Υ_disk
  nydk   (k=3)  NFW + free Υ_disk, free: M_vir, c, Υ_disk
  rsyd   (k=3)  IRS + free σ + free Υ_disk, free: Q, σ, Υ_disk
  fsgd   (k=2)  IRS prescribed-σ (σ = α·R_t), free: Q, Υ_disk
                  α = ALPHA_SIGMA = 1.0 (dimensionless; theory-derived)
  disk   (k=2)  IRS disk-kernel Option B (σ removed entirely), free: Q, Υ_disk
                  Kernel source: S(R) ∝ Υ_disk·SBdisk + Υ_bul·SBbul (imaging)

PRIMARY OUTPUTS
---------------
  sparc_bic_results.csv   — per-galaxy table; all BIC, ΔBIC, χ², σ_fit, Υ values
  sparc_summary.json      — aggregate statistics: medians, pass-rates, CV-RMSE
  bic_comparison_figure.png
  bic_scatter_figure.png

REPRODUCIBILITY NOTES
---------------------
  • Random seed: np.random.seed(i) per galaxy i in the CV loop — results are
    fully deterministic for a fixed SPARC dataset and Python/NumPy version.
  • Optimizer: scipy.optimize.minimize with Nelder-Mead (maxiter=600 default,
    600 for fsig/disk models); multi-start grid covers the plausible parameter
    space to reduce local-minimum sensitivity.
  • MC uncertainty: 50 Monte Carlo draws of (Υ_disk, distance_scale) with
    LogNormal priors; seed set per sample index for reproducibility.
  • Expected CV-RMSE reference values (Python 3.11, NumPy 2.x, SciPy 1.13):
      IRS resp   k=1: ~13.6 ± 10.3 km/s
      NFW        k=2:  ~8.3 ±  6.5 km/s
      IRS fsgd   k=2: ~23.3 ± 17.3 km/s  (α=1, prescribed-σ)
      IRS disk   k=2:  ~TBD (disk-kernel Option B)
  • BIC reference: IRS resp vs baryons-only, median ΔBIC ≈ −1370 (pass rate ~95%)

CITATION
--------
If you use this script or the SPARC data, please cite:
  Kitcey R.D. (2026). Intrinsic Response Sector as Dark Gravity.
    Zenodo. https://doi.org/10.5281/zenodo.18799081  (IRS-II v5.1)
  Lelli F., McGaugh S.S., Schombert J.M. (2016).
    AJ 152, 157.  https://doi.org/10.3847/0004-6256/152/6/157
  Schombert J., McGaugh S., Lelli F. (2019).
    MNRAS 483, 1496.  https://doi.org/10.1093/mnras/sty3223
"""

import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar, minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import json

# Ensure Unicode characters (e.g. Δ, σ) survive on Windows cp1252 consoles.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────────────────
# 0. PATHS
# ─────────────────────────────────────────────────────────────────────────────

# Locate Rotmod_LTG relative to this script (repro_package/ -> ../../Rotmod_LTG)
_SCRIPT_DIR = Path(__file__).resolve().parent
_ROTMOD_CANDIDATES = [
    _SCRIPT_DIR / ".." / ".." / "Rotmod_LTG",          # arxiv_robust/../Rotmod_LTG
    _SCRIPT_DIR / ".." / ".." / ".." / "Rotmod_LTG",   # one level higher
    Path("Rotmod_LTG"),                                  # cwd fallback
]
ROTMOD_DIR = None
for _p in _ROTMOD_CANDIDATES:
    _p = _p.resolve()
    if _p.is_dir() and list(_p.glob("*_rotmod.dat")):
        ROTMOD_DIR = _p
        break
if ROTMOD_DIR is None:
    raise FileNotFoundError(
        "Cannot find Rotmod_LTG directory with *_rotmod.dat files. "
        "Run from the Spacetime_Mechanics workspace root or set ROTMOD_DIR."
    )
print(f"Using SPARC data from: {ROTMOD_DIR}")

OUT_DIR = _SCRIPT_DIR
OUT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD SPARC DATA
# ─────────────────────────────────────────────────────────────────────────────

# Physical constants
A0_SI = 1.2e-10                        # m/s^2 (MOND/IRS transition acceleration)
KPC_IN_M = 3.085677581491367e19        # m per kpc
A0_KMS2_KPC = A0_SI / (1e6 / KPC_IN_M)  # a0 in (km/s)^2/kpc ≈ 3.857

UPS_DISK = 0.5   # stellar mass-to-light, disk  (Schombert+2019)
UPS_BUL  = 0.7   # stellar mass-to-light, bulge

# Physical ansatz: σ = ALPHA_SIGMA × R_t  (derived coherence scale prescription)
# Derivation: the IRS field equation has exactly one natural length, R_t.  No
# independent coherence scale exists in the theory; dimensional uniqueness
# therefore demands σ = α·R_t.  Empirically, the free-σ fits give median
# σ/R_t ≈ 0.75 (k=2) and ≈1.09 (k=3), bracketing α = 1 as the theoretically
# clean prediction.  α = 1 is the primary test; 0.5 and 2.0 bracket it.
ALPHA_SIGMA = 1.0   # dimensionless coherence-scale ratio σ/R_t

def read_rotmod(path: Path):
    """Read a SPARC *_rotmod.dat file.

    Returns dict with arrays (R, Vobs, errV, Vbar, V_bar_sq) or None on failure.
    Column order: R Vobs errV Vgas Vdisk Vbul SBdisk SBbul

    Also stores:
      - distance_mpc: parsed from '# Distance = X.XX Mpc' header
      - Vgas_sq, Vdisk_sq_raw (Vdisk²/Υ_disk), Vbul_sq_raw (Vbul²/Υ_bul)
        for Monte Carlo resampling of Υ_disk and distance.
    """
    # Parse distance from header
    distance_mpc = float("nan")
    try:
        with open(path) as fh:
            for line in fh:
                if not line.startswith("#"):
                    break
                if "Distance" in line:
                    distance_mpc = float(line.split("=")[1].strip().split()[0])
    except Exception:
        pass

    data = np.genfromtxt(path, comments="#", invalid_raise=False)
    if data.ndim != 2 or data.shape[1] < 6:
        return None
    R     = data[:, 0]
    Vobs  = data[:, 1]
    errV  = data[:, 2]
    Vgas  = data[:, 3]
    Vdisk = data[:, 4]
    Vbul  = data[:, 5]
    # Surface brightness profiles (cols 6-7; present in all SPARC rotmod files)
    SBdisk = data[:, 6] if data.shape[1] > 6 else np.zeros_like(R)
    SBbul  = data[:, 7] if data.shape[1] > 7 else np.zeros_like(R)
    SBdisk = np.maximum(SBdisk, 0.0)
    SBbul  = np.maximum(SBbul,  0.0)

    Vbar_sq = Vgas**2 + UPS_DISK * Vdisk**2 + UPS_BUL * Vbul**2
    Vbar_sq = np.maximum(Vbar_sq, 0.0)
    Vbar    = np.sqrt(Vbar_sq)

    mask = (
        np.isfinite(R) & np.isfinite(Vobs) & np.isfinite(errV) & np.isfinite(Vbar)
        & (R > 0) & (Vobs > 0) & (errV > 0)
    )
    if mask.sum() < 5:
        return None

    order = np.argsort(R[mask])
    return {
        "name":          path.stem.replace("_rotmod", ""),
        "distance_mpc":  distance_mpc,
        "R":             R[mask][order],
        "V_obs":         Vobs[mask][order],
        "errV":          errV[mask][order],
        "V_bar":         Vbar[mask][order],
        "V_bar_sq":      Vbar_sq[mask][order],
        # Raw (Υ-free) component squares for MC resampling:
        #   V_bar_sq_mc = d_scale * (Vgas_sq + Y_new * Vdisk_sq_raw + UPS_BUL * Vbul_sq_raw)
        # Photometric surface brightness profiles (from imaging, orthogonal to kinematics)
        "SBdisk":        SBdisk[mask][order],
        "SBbul":         SBbul[mask][order],
        "Vgas_sq":       (Vgas[mask][order])**2,
        "Vdisk_sq_raw":  (Vdisk[mask][order])**2 / UPS_DISK,   # at Υ_disk = 1
        "Vbul_sq_raw":   (Vbul[mask][order])**2 / UPS_BUL,     # at Υ_bul = 1
        # sigma alias used by model functions
        "sigma":         errV[mask][order],
    }


def load_all_galaxies():
    files = sorted(ROTMOD_DIR.glob("*_rotmod.dat"))
    galaxies = []
    skipped = []
    for f in files:
        gal = read_rotmod(f)
        if gal is None:
            skipped.append(f.name)
        else:
            galaxies.append(gal)
    print(f"Loaded {len(galaxies)} galaxies ({len(skipped)} skipped).")
    if skipped:
        print(f"  Skipped: {skipped}")
    return galaxies

# ─────────────────────────────────────────────────────────────────────────────
# 2. MODEL DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

# ---- IRS: transition radius ----
def find_rt(R: np.ndarray, gbar: np.ndarray, a0: float) -> float:
    """Find R_t where gbar(R_t) ≈ a0 by log-linear interpolation."""
    if len(R) < 2:
        return float(R[-1]) if len(R) else float("nan")
    log_ratio = np.log(np.maximum(gbar, 1e-30) / a0)
    for i in range(1, len(R)):
        if log_ratio[i - 1] >= 0 >= log_ratio[i]:
            x0, x1 = math.log(R[i - 1]), math.log(R[i])
            y0, y1 = log_ratio[i - 1], log_ratio[i]
            if y1 == y0:
                return float(R[i])
            t = -y0 / (y1 - y0)
            return float(math.exp(x0 + t * (x1 - x0)))
    idx = int(np.argmin(np.abs(log_ratio)))
    return float(R[idx])


def chi_prime_unit(R: np.ndarray, r_t: float, sigma_kpc: float = 2.0) -> np.ndarray:
    """Radial 2D Poisson solution with Gaussian source at r_t.

    Returns χ'_unit(R) — the normalised auxiliary-field profile used in the
    IRS response model.  This is the physically derived kernel, NOT a simple
    1/R heuristic.
    """
    s0 = np.exp(-0.5 * ((R - r_t) / max(sigma_kpc, 1e-12)) ** 2)
    integrand = R * s0
    norm = float(np.trapezoid(integrand, R))
    if norm <= 0:
        return np.zeros_like(R)
    S = s0 / norm
    u = np.zeros_like(R)
    for i in range(1, len(R)):
        u[i] = (u[i - 1]
                + 0.5 * (R[i] - R[i - 1])
                * (R[i] * S[i] + R[i - 1] * S[i - 1]))
    return u / np.maximum(R, 1e-30)


def chi_prime_disk_kernel(R: np.ndarray, SBdisk: np.ndarray,
                          SBbul: np.ndarray) -> np.ndarray:
    """IRS kernel sourced by the observed baryonic surface brightness (Option B).

    Physical derivation:
    ───────────────────────────────────────────────────────────────────────────
    The IRS auxiliary field χ obeys ∇²χ = −S(R), where S(R) is the baryonic
    surface-density source.  For a stellar disk+bulge:

        S(R) ∝ Υ_disk · SBdisk(R) + Υ_bul · SBbul(R)

    Since χ' = χ'_unit × Q (with Q the single free amplitude), and since the
    Poisson equation is linear, the kernel shape is determined by S(R) alone.
    Normalisation absorbs Q, so the kernel depends only on the ratio
    Υ_bul/Υ_disk (fixed at UPS_BUL/UPS_DISK ≈ 1.4) — not on their individual
    magnitudes.  This removes σ entirely: the coherence scale of the field is
    set by wherever the stellar mass is concentrated, i.e. the disk scale
    length h_d implicit in SBdisk(R) ∝ exp(−R/h_d).

    Advantages vs Gaussian approximation:
    • No free shape parameter (k reduction of 1 vs free-σ models)
    • Kernel derived from photometry (orthogonal to kinematic CV folds)
    • Physically correct: mass traces the source field
    • No boundary saturation (σ → ∞ pathology is impossible)

    Returns the normalised χ'(R) profile.
    """
    # Effective mass surface density proxy (shape only; normalisation cancels)
    s0 = UPS_DISK * SBdisk + UPS_BUL * SBbul
    s0 = np.maximum(s0, 0.0)
    integrand = R * s0
    norm = float(np.trapezoid(integrand, R))
    if norm <= 0:
        # Fallback: uniform source (degenerate galaxy with no photometry)
        s0 = np.ones_like(R)
        norm = float(np.trapezoid(R * s0, R))
        if norm <= 0:
            return np.zeros_like(R)
    S = s0 / norm
    u = np.zeros_like(R)
    for i in range(1, len(R)):
        u[i] = (u[i - 1]
                + 0.5 * (R[i] - R[i - 1])
                * (R[i] * S[i] + R[i - 1] * S[i - 1]))
    return u / np.maximum(R, 1e-30)


def response_model_curve(R, V_bar_sq, chi_unit, Q):
    """IRS velocity model: V^2 = V_bar^2 + Q * χ'_unit * R."""
    V_model_sq = V_bar_sq + Q * chi_unit * R
    return np.sqrt(np.maximum(V_model_sq, 0))


def nfw_model(R, V_bar_sq, M_vir, c):
    """NFW halo profile: V^2_NFW(R) added to baryonic.

    Parameterised by M_vir (10^10 M_sun) and concentration c.
    c is physically constrained to [3, 40] to prevent overfitting.
    """
    # r_vir from M_vir: M_vir = (4/3)*pi*r_vir^3 * 200 * rho_crit
    G = 4.302e-3  # pc M_sun^-1 (km/s)^2 → need kpc units
    G_kpc = 4.302e-6  # kpc M_sun^-1 (km/s)^2
    
    M_vir_msun = M_vir * 1e10
    # r_vir from M_vir: M_vir = (4/3)*pi*r_vir^3 * 200 * rho_crit
    rho_crit = 1.36e11 * 1e-9  # M_sun/kpc^3 (for H_0=70)
    r_vir = (3 * M_vir_msun / (4 * np.pi * 200 * rho_crit))**(1/3)
    r_s = r_vir / c
    
    rho_s = M_vir_msun / (4 * np.pi * r_s**3 * (np.log(1 + c) - c/(1+c)))
    
    x = R / r_s
    x = np.maximum(x, 1e-6)
    V_nfw_sq = 4 * np.pi * G_kpc * rho_s * r_s**3 / R * (np.log(1 + x) - x/(1+x))
    V_nfw_sq = np.maximum(V_nfw_sq, 0)
    
    V_total_sq = V_bar_sq + V_nfw_sq
    return np.sqrt(np.maximum(V_total_sq, 0))

def burkert_model(R, V_bar_sq, rho0, r_c):
    """Burkert halo profile."""
    # rho(r) = rho0 / [(1 + r/r_c)(1 + (r/r_c)^2)]
    # M(R) = pi*rho0*r_c^3 * [ln(1+(R/r_c)^2) + 2*ln(1+R/r_c) - 2*arctan(R/r_c)]
    G_kpc = 4.302e-6
    x = R / r_c
    x = np.maximum(x, 1e-6)
    M_enc = np.pi * rho0 * r_c**3 * (np.log(1 + x**2) + 2*np.log(1 + x) - 2*np.arctan(x))
    V_burkert_sq = G_kpc * M_enc / R
    V_burkert_sq = np.maximum(V_burkert_sq, 0)
    
    V_total_sq = V_bar_sq + V_burkert_sq
    return np.sqrt(np.maximum(V_total_sq, 0))

# ─────────────────────────────────────────────────────────────────────────────
# 3. FITTING FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def fit_response(gal, sigma_kpc: float = 2.0):
    """Fit IRS response model to a real SPARC galaxy.  1 free parameter: Q."""
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]

    gbar      = np.maximum(V_bar_sq, 0) / R
    r_t       = find_rt(R, gbar, A0_KMS2_KPC)
    chi_unit  = chi_prime_unit(R, r_t, sigma_kpc)

    def chi2_fn(Q):
        if Q < 0:
            return 1e10
        V_model = response_model_curve(R, V_bar_sq, chi_unit, Q)
        return float(np.sum(((V_model - V_obs) / errV) ** 2))

    Q_hi = max(10.0, 2.0 * float(np.max(V_obs)) ** 2)
    res  = minimize_scalar(chi2_fn, bounds=(0.0, Q_hi), method="bounded",
                           options={"xatol": 1e-3})
    Q_best    = float(res.x)
    chi2_best = float(res.fun)
    n = len(R)
    k = 1
    return {"Q": Q_best, "chi2": chi2_best, "bic": chi2_best + k * math.log(n),
            "n": n, "k": k, "r_t": r_t}


def fit_baryons_only(gal):
    """Baryons-only: 0 free parameters (Upsilon fixed)."""
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]

    V_model = np.sqrt(np.maximum(V_bar_sq, 0))
    chi2    = float(np.sum(((V_obs - V_model) / errV) ** 2))
    n = len(R)
    bic = float(chi2)   # k=0, so BIC = chi2
    return {"chi2": chi2, "bic": bic, "n": n, "k": 0}


def fit_nfw(gal):
    """Fit NFW halo to real SPARC data.  2 free parameters (M_vir, c).

    Concentration c is bounded to [3, 40] — physically motivated range for
    SPARC galaxy halos.  Prevents the runaway c → 0 or c → 100 overfitting
    seen when bounds are absent.
    """
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]

    # log10(M_vir/1e10 Msun) search range: 0.0..3.0 covers 10^10–10^13 Msun
    # c in [3, 40]: log10 range [0.477, 1.602]
    def chi2_fn(params):
        log_Mvir, log_c = params
        M_vir = 10.0 ** log_Mvir
        c     = 10.0 ** log_c
        # Hard bounds via penalty
        if M_vir <= 0 or c < 3.0 or c > 40.0:
            return 1e10
        try:
            V_model = nfw_model(R, V_bar_sq, M_vir, c)
            return float(np.sum(((V_model - V_obs) / errV) ** 2))
        except Exception:
            return 1e10

    best_chi2   = 1e10
    best_params = [1.0, math.log10(10.0)]
    for log_Mvir0 in [0.5, 1.0, 1.5, 2.0, 2.5]:
        for log_c0 in [math.log10(5), math.log10(10), math.log10(20)]:
            try:
                res = minimize(chi2_fn, [log_Mvir0, log_c0], method="Nelder-Mead",
                               options={"xatol": 0.01, "fatol": 0.1, "maxiter": 1000})
                if res.fun < best_chi2:
                    best_chi2   = res.fun
                    best_params = res.x
            except Exception:
                pass

    n   = len(R)
    k   = 2
    bic = best_chi2 + k * math.log(n)
    return {"chi2": best_chi2, "bic": bic, "n": n, "k": k,
            "M_vir": 10.0 ** best_params[0], "c": 10.0 ** best_params[1]}


def fit_burkert(gal):
    """Fit Burkert halo to real SPARC data.  2 free parameters (rho0, r_c)."""
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]

    def chi2_fn(params):
        log_rho0, log_rc = params
        rho0 = 10.0 ** log_rho0
        r_c  = 10.0 ** log_rc
        if rho0 <= 0 or r_c <= 0:
            return 1e10
        try:
            V_model = burkert_model(R, V_bar_sq, rho0, r_c)
            return float(np.sum(((V_model - V_obs) / errV) ** 2))
        except Exception:
            return 1e10

    best_chi2   = 1e10
    best_params = [7.0, 0.5]
    for log_rho0 in [6.5, 7.0, 7.5, 8.0]:
        for log_rc in [0.0, 0.5, 1.0]:
            try:
                res = minimize(chi2_fn, [log_rho0, log_rc], method="Nelder-Mead",
                               options={"xatol": 0.01, "fatol": 0.1, "maxiter": 1000})
                if res.fun < best_chi2:
                    best_chi2   = res.fun
                    best_params = res.x
            except Exception:
                pass

    n   = len(R)
    k   = 2
    bic = best_chi2 + k * math.log(n)
    return {"chi2": best_chi2, "bic": bic, "n": n, "k": k,
            "rho0": 10.0 ** best_params[0], "r_c": 10.0 ** best_params[1]}


def fit_response_sigma(gal):
    """IRS with 2 free parameters: Q (amplitude) and sigma_kpc (kernel scale).

    BIC penalty k=2, same as NFW/Burkert.  Tests whether a per-galaxy
    coherence length is physically needed and whether it closes the BIC gap.
    sigma bounded to [0.3, 10] kpc — sub-disk-scale to super-disk-scale.
    """
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]
    gbar     = np.maximum(V_bar_sq, 0) / R

    def chi2_fn(params):
        log_Q, log_sigma = params
        Q     = 10.0 ** log_Q
        sigma = 10.0 ** log_sigma
        if Q < 0 or sigma < 0.3 or sigma > 10.0:
            return 1e10
        try:
            r_t      = find_rt(R, gbar, A0_KMS2_KPC)
            chi_unit = chi_prime_unit(R, r_t, sigma)
            V_model  = response_model_curve(R, V_bar_sq, chi_unit, Q)
            return float(np.sum(((V_model - V_obs) / errV) ** 2))
        except Exception:
            return 1e10

    best_chi2   = 1e10
    best_params = [1.0, math.log10(2.0)]
    Q_hi_log = math.log10(max(10.0, 2.0 * float(np.max(V_obs)) ** 2))
    for log_Q0 in [0.0, 1.0, Q_hi_log * 0.5, Q_hi_log]:
        for log_sig0 in [math.log10(0.5), math.log10(2.0), math.log10(5.0)]:
            try:
                res = minimize(chi2_fn, [log_Q0, log_sig0], method="Nelder-Mead",
                               options={"xatol": 0.01, "fatol": 0.1, "maxiter": 1000})
                if res.fun < best_chi2:
                    best_chi2   = res.fun
                    best_params = res.x
            except Exception:
                pass

    n   = len(R)
    k   = 2
    bic = best_chi2 + k * math.log(n)
    Q_fit     = 10.0 ** best_params[0]
    sigma_fit = 10.0 ** best_params[1]
    return {"chi2": best_chi2, "bic": bic, "n": n, "k": k,
            "Q": Q_fit, "sigma_kpc": sigma_fit}


def fit_response_ydisk(gal):
    """IRS with 2 free parameters: Q and Upsilon_disk (per-galaxy mass-to-light).

    BIC penalty k=2.  Tests whether baryonic uncertainty is the dominant
    source of residuals.  Upsilon_disk bounded to [0.1, 1.5].
    """
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    # raw V_bar_sq at UPS_DISK=0.5; we reconstruct for other Y values
    # by scaling: all-disk approximation (conservative — same as marginalization panel)
    V_bar_sq_base = gal["V_bar_sq"]

    def chi2_fn(params):
        log_Q, Y = params
        Q = 10.0 ** log_Q
        if Q < 0 or Y < 0.1 or Y > 1.5:
            return 1e10
        try:
            scale    = Y / UPS_DISK
            Vbsq     = V_bar_sq_base * scale
            gbar     = np.maximum(Vbsq, 0) / R
            r_t      = find_rt(R, gbar, A0_KMS2_KPC)
            chi_unit = chi_prime_unit(R, r_t, sigma_kpc=2.0)
            V_model  = response_model_curve(R, Vbsq, chi_unit, Q)
            return float(np.sum(((V_model - V_obs) / errV) ** 2))
        except Exception:
            return 1e10

    best_chi2   = 1e10
    best_params = [1.0, 0.5]
    Q_hi_log = math.log10(max(10.0, 2.0 * float(np.max(V_obs)) ** 2))
    for log_Q0 in [0.0, 1.0, Q_hi_log * 0.5]:
        for Y0 in [0.3, 0.5, 0.7, 1.0]:
            try:
                res = minimize(chi2_fn, [log_Q0, Y0], method="Nelder-Mead",
                               options={"xatol": 0.01, "fatol": 0.1, "maxiter": 1000})
                if res.fun < best_chi2:
                    best_chi2   = res.fun
                    best_params = res.x
            except Exception:
                pass

    n   = len(R)
    k   = 2
    bic = best_chi2 + k * math.log(n)
    Q_fit = 10.0 ** best_params[0]
    Y_fit = float(best_params[1])
    return {"chi2": best_chi2, "bic": bic, "n": n, "k": k,
            "Q": Q_fit, "Y_disk": Y_fit}


def fit_nfw_ydisk(gal):
    """NFW with 3 free parameters: log10(M_vir), log10(c), and Upsilon_disk.

    k=3.  This is the fair head-to-head counterpart to fit_response_ydisk (k=2):
    when both models have a free Upsilon_disk, IRS still uses one fewer parameter.
    Upsilon_disk bounded to [0.1, 1.5]; c bounded to [3, 40].
    """
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq_base = gal["V_bar_sq"]

    def chi2_fn(params):
        log_Mvir, log_c, Y = params
        M_vir = 10.0 ** log_Mvir
        c     = 10.0 ** log_c
        if c < 3.0 or c > 40.0 or Y < 0.1 or Y > 1.5:
            return 1e10
        try:
            scale    = Y / UPS_DISK
            Vbsq     = V_bar_sq_base * scale
            V_model  = nfw_model(R, Vbsq, M_vir, c)
            return float(np.sum(((V_model - V_obs) / errV) ** 2))
        except Exception:
            return 1e10

    best_chi2   = 1e10
    best_params = [1.0, math.log10(10.0), 0.5]
    for log_Mvir0 in [0.5, 1.0, 1.5, 2.0]:
        for log_c0 in [math.log10(5), math.log10(10), math.log10(20)]:
            for Y0 in [0.5, 0.8, 1.0]:
                try:
                    res = minimize(chi2_fn, [log_Mvir0, log_c0, Y0], method="Nelder-Mead",
                                   options={"xatol": 0.01, "fatol": 0.1, "maxiter": 1000})
                    if res.fun < best_chi2:
                        best_chi2   = res.fun
                        best_params = res.x
                except Exception:
                    pass

    n   = len(R)
    k   = 3
    bic = best_chi2 + k * math.log(n)
    return {"chi2": best_chi2, "bic": bic, "n": n, "k": k,
            "M_vir": 10.0 ** best_params[0], "c": 10.0 ** best_params[1],
            "Y_disk": float(best_params[2])}


def fit_response_sigma_ydisk(gal):
    """IRS with 3 free parameters: Q, sigma_kpc, and Upsilon_disk.

    k=3 — equal BIC budget to NFW+Υ_disk.  This is the fair physics comparison:
    IRS's physical degrees of freedom (amplitude, coherence scale, baryonic mass)
    against NFW's (halo mass, concentration, baryonic mass).
    Bounds: sigma ∈ [0.3, 10] kpc, Υ_disk ∈ [0.1, 1.5].
    """
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq_base = gal["V_bar_sq"]

    def chi2_fn(params):
        log_Q, log_sigma, Y = params
        Q     = 10.0 ** log_Q
        sigma = 10.0 ** log_sigma
        if Q < 0 or sigma < 0.3 or sigma > 10.0 or Y < 0.1 or Y > 1.5:
            return 1e10
        try:
            scale    = Y / UPS_DISK
            Vbsq     = V_bar_sq_base * scale
            gbar     = np.maximum(Vbsq, 0) / R
            r_t      = find_rt(R, gbar, A0_KMS2_KPC)
            chi_unit = chi_prime_unit(R, r_t, sigma)
            V_model  = response_model_curve(R, Vbsq, chi_unit, Q)
            return float(np.sum(((V_model - V_obs) / errV) ** 2))
        except Exception:
            return 1e10

    best_chi2   = 1e10
    best_params = [1.0, math.log10(2.0), 0.5]
    Q_hi_log = math.log10(max(10.0, 2.0 * float(np.max(V_obs)) ** 2))
    for log_Q0 in [0.0, 1.0, Q_hi_log * 0.5]:
        for log_sig0 in [math.log10(0.5), math.log10(2.0), math.log10(5.0)]:
            for Y0 in [0.5, 0.8, 1.0]:
                try:
                    res = minimize(chi2_fn, [log_Q0, log_sig0, Y0], method="Nelder-Mead",
                                   options={"xatol": 0.01, "fatol": 0.1, "maxiter": 1500})
                    if res.fun < best_chi2:
                        best_chi2   = res.fun
                        best_params = res.x
                except Exception:
                    pass

    n   = len(R)
    k   = 3
    bic = best_chi2 + k * math.log(n)
    return {"chi2": best_chi2, "bic": bic, "n": n, "k": k,
            "Q": 10.0 ** best_params[0],
            "sigma_kpc": 10.0 ** best_params[1],
            "Y_disk": float(best_params[2])}


def fit_response_disk_ydisk(gal):
    """IRS with disk-kernel (Option B): kernel sourced by SBdisk+SBbul photometry.

    Free parameters: Q (IRS amplitude), Υ_disk (baryonic mass-to-light).
    k = 2 — same BIC budget as NFW(M_vir, c) or IRS+Υ(k=2).

    The kernel χ'_disk is computed once from the photometric SBdisk/SBbul
    profiles at canonical Υ values.  Υ_disk only rescales V_bar_sq (kinematics),
    NOT the kernel shape — so the kernel is entirely fixed by photometry and
    carries zero degrees of freedom.
    """
    R             = gal["R"]
    V_obs         = gal["V_obs"]
    errV          = gal["errV"]
    V_bar_sq_base = gal["V_bar_sq"]
    SBdisk        = gal["SBdisk"]
    SBbul         = gal["SBbul"]

    # Kernel fixed from photometry — computed once for the full galaxy
    chi_unit = chi_prime_disk_kernel(R, SBdisk, SBbul)

    def chi2_fn(params):
        log_Q, Y = params
        Q = 10.0 ** log_Q
        if Q < 0 or Y < 0.1 or Y > 1.5:
            return 1e10
        try:
            scale   = Y / UPS_DISK
            Vbsq    = V_bar_sq_base * scale
            V_model = response_model_curve(R, Vbsq, chi_unit, Q)
            return float(np.sum(((V_model - V_obs) / errV) ** 2))
        except Exception:
            return 1e10

    best_chi2   = 1e10
    best_params = [1.0, 0.6]
    Q_hi_log = math.log10(max(10.0, 2.0 * float(np.max(V_obs)) ** 2))
    for log_Q0 in [0.0, 1.0, Q_hi_log * 0.5]:
        for Y0 in [0.3, 0.5, 0.7, 1.0, 1.2]:
            try:
                res = minimize(chi2_fn, [log_Q0, Y0], method="Nelder-Mead",
                               options={"xatol": 0.01, "fatol": 0.1, "maxiter": 1000})
                if res.fun < best_chi2:
                    best_chi2   = res.fun
                    best_params = res.x
            except Exception:
                pass

    n   = len(R)
    k   = 2
    bic = best_chi2 + k * math.log(n)
    return {"chi2": best_chi2, "bic": bic, "n": n, "k": k,
            "Q": 10.0 ** best_params[0], "Y_disk": float(best_params[1])}


def fit_response_fsig_ydisk(gal, alpha=None):
    """IRS with PRESCRIBED coherence scale σ = α·R_t — 2 free parameters (Q, Υ_disk).

    Physical derivation (α = ALPHA_SIGMA = 1):
    ────────────────────────────────────────────────────────────────────────────
    The IRS auxiliary field χ satisfies a 2-D Poisson equation sourced by the
    baryonic surface-density distribution, which is Gaussian-regularised at
    scale σ.  The field equation contains exactly one dimensional scale: the
    MOND transition radius R_t where g_bar = a₀.  Introducing σ as an
    independent free parameter breaks this self-similarity and adds a degree of
    freedom with no first-principles grounding.  The minimal prescription that
    preserves dimensional uniqueness is σ = α·R_t.

    Empirical consistency: free-σ fits to 171 SPARC galaxies give median
    σ/R_t ≈ 0.75 (k=2) and ≈ 1.09 (k=3), bracketing α = 1.  The primary test
    uses α = ALPHA_SIGMA = 1.0; α = 0.5 and 2.0 bracket it.

    With σ prescribed, this model has k = 2 (Q and Υ_disk are the only free
    parameters), making it directly comparable to any k=2 model while carrying
    less overfitting risk than the free-σ k=3 version.
    """
    if alpha is None:
        alpha = ALPHA_SIGMA
    R             = gal["R"]
    V_obs         = gal["V_obs"]
    errV          = gal["errV"]
    V_bar_sq_base = gal["V_bar_sq"]

    def chi2_fn(params):
        log_Q, Y = params
        Q = 10.0 ** log_Q
        if Q < 0 or Y < 0.1 or Y > 1.5:
            return 1e10
        try:
            scale    = Y / UPS_DISK
            Vbsq     = V_bar_sq_base * scale
            gbar     = np.maximum(Vbsq, 0) / R
            r_t      = find_rt(R, gbar, A0_KMS2_KPC)
            sigma    = alpha * r_t               # prescribed coherence scale
            chi_unit = chi_prime_unit(R, r_t, sigma)
            V_model  = response_model_curve(R, Vbsq, chi_unit, Q)
            return float(np.sum(((V_model - V_obs) / errV) ** 2))
        except Exception:
            return 1e10

    best_chi2   = 1e10
    best_params = [1.0, 0.6]
    Q_hi_log = math.log10(max(10.0, 2.0 * float(np.max(V_obs)) ** 2))
    for log_Q0 in [0.0, 1.0, Q_hi_log * 0.5]:
        for Y0 in [0.3, 0.5, 0.7, 1.0, 1.2]:
            try:
                res = minimize(chi2_fn, [log_Q0, Y0], method="Nelder-Mead",
                               options={"xatol": 0.01, "fatol": 0.1, "maxiter": 1000})
                if res.fun < best_chi2:
                    best_chi2   = res.fun
                    best_params = res.x
            except Exception:
                pass

    n   = len(R)
    k   = 2
    bic = best_chi2 + k * math.log(n)
    Q_fit = 10.0 ** best_params[0]
    Y_fit = float(best_params[1])
    # Recover the prescribed sigma at the best-fit parameters
    scale_best = Y_fit / UPS_DISK
    Vbsq_best  = V_bar_sq_base * scale_best
    gbar_best  = np.maximum(Vbsq_best, 0) / R
    r_t_best   = find_rt(R, gbar_best, A0_KMS2_KPC)
    sigma_best = alpha * r_t_best
    return {"chi2": best_chi2, "bic": bic, "n": n, "k": k,
            "Q": Q_fit, "Y_disk": Y_fit,
            "sigma_prescribed_kpc": sigma_best, "alpha": alpha}


# ─────────────────────────────────────────────────────────────────────────────
# BARYONIC UNCERTAINTY MONTE CARLO
# ─────────────────────────────────────────────────────────────────────────────

def bic_mc_uncertainty(galaxies, results_df, n_samples=50, seed=42):
    """Propagate baryonic systematic uncertainties through the BIC comparison.

    Two independent uncertainty axes:
    ─────────────────────────────────────────────────────────────────────────
    1. Υ_disk (stellar mass-to-light ratio at 3.6μm)
       Source: Schombert, McGaugh & Lelli (2019) SPS calibration.
       Quoted systematic: σ(log₁₀ Υ) = 0.10 dex  → 1σ range [0.40, 0.63]
       Sampled as: log₁₀(Y) ~ N(log₁₀(0.5), 0.10)

    2. Distance
       SPARC distances use a mix of methods:
         • Cepheid / TRGB (high-quality):  σ_D/D ≈ 5%   (~25 galaxies)
         • SBF, TULLY-FISHER, group:       σ_D/D ≈ 12%
         • Hubble flow (majority):          σ_D/D ≈ 18%  (H₀ + peculiar v)
       Effective ensemble σ_D/D ≈ 0.12 (conservative).
       Since V_bar ∝ √(L/D) ∝ √(D × Υ), V_bar_sq ∝ D × Υ.
       Sampled as: d_scale ~ N(1.0, 0.12) clipped to [0.70, 1.35]

    MC propagation:
       V_bar_sq_mc = d_scale × (Vgas² + Y × Vdisk_raw² + Υ_bul × Vbul_raw²)
    where Vdisk_raw² = Vdisk²/Υ_disk (velocities at Υ=1) — stored in gal dict.

    Returns dict with per-model ΔBIC distributions (171 galaxies × n_samples).
    """
    rng = np.random.default_rng(seed)
    # Υ_disk: log-normal with σ=0.10 dex
    Y_samples = 10.0 ** rng.normal(np.log10(UPS_DISK), 0.10, n_samples)
    # Distance scale: normal, clipped positive
    d_samples = np.clip(rng.normal(1.0, 0.12, n_samples), 0.70, 1.35)

    # Build index map galaxy name → row in results_df for warm-starting NFW
    nfw_init = {}
    for _, row in results_df.iterrows():
        m = row.get("M_vir_nfw", 1.0)
        c = row.get("c_nfw",     10.0)
        if np.isfinite(m) and np.isfinite(c) and m > 0 and c > 0:
            nfw_init[row["galaxy"]] = [math.log10(m), math.log10(c)]

    all_dbic_resp = []   # shape (n_galaxies × n_samples,)
    all_dbic_nfw  = []

    print(f"\nRunning baryonic uncertainty MC: {n_samples} samples × {len(galaxies)} galaxies...")
    for i_s in range(n_samples):
        Y, d = float(Y_samples[i_s]), float(d_samples[i_s])
        dbic_resp_s, dbic_nfw_s = [], []

        for gal in galaxies:
            # Recompute V_bar_sq under this (Y, d) sample
            Vbsq_mc = np.maximum(
                d * (gal["Vgas_sq"] + Y * gal["Vdisk_sq_raw"]
                     + UPS_BUL * gal["Vbul_sq_raw"]),
                0.0
            )
            gal_mc = dict(gal, V_bar_sq=Vbsq_mc)

            try:
                r_bar  = fit_baryons_only(gal_mc)
                r_resp = fit_response(gal_mc)

                # NFW: warm-start from original best-fit params, 3 starts only
                R, V_obs, errV = gal_mc["R"], gal_mc["V_obs"], gal_mc["errV"]
                init_p = nfw_init.get(gal["name"], [1.0, math.log10(10.0)])
                best_c2, best_p = 1e10, init_p[:]
                for dp_lm, dp_lc in [(0, 0), (-0.3, 0), (0.3, 0)]:
                    p0 = [init_p[0] + dp_lm, init_p[1] + dp_lc]
                    def chi2_nfw(params, _R=R, _V=V_obs, _e=errV, _Vb=Vbsq_mc):
                        lm, lc = params
                        c_ = 10.0 ** lc
                        if c_ < 3.0 or c_ > 40.0:
                            return 1e10
                        try:
                            return float(np.sum(
                                ((nfw_model(_R, _Vb, 10.0**lm, c_) - _V) / _e) ** 2))
                        except Exception:
                            return 1e10
                    try:
                        res = minimize(chi2_nfw, p0, method="Nelder-Mead",
                                       options={"maxiter": 600, "xatol": 0.02, "fatol": 0.5})
                        if res.fun < best_c2:
                            best_c2 = res.fun
                            best_p  = res.x
                    except Exception:
                        pass

                n = len(R)
                bic_nfw = best_c2 + 2 * math.log(n)
                dbic_resp_s.append(r_resp["bic"] - r_bar["bic"])
                dbic_nfw_s.append(bic_nfw        - r_bar["bic"])
            except Exception:
                dbic_resp_s.append(float("nan"))
                dbic_nfw_s.append(float("nan"))

        all_dbic_resp.append(dbic_resp_s)
        all_dbic_nfw.append(dbic_nfw_s)
        if (i_s + 1) % 10 == 0:
            print(f"  MC sample {i_s+1}/{n_samples} (Y={Y:.3f}, d={d:.3f})")

    # Aggregate: axis 0 = samples, axis 1 = galaxies
    resp_arr = np.array(all_dbic_resp)   # (n_samples, n_galaxies)
    nfw_arr  = np.array(all_dbic_nfw)

    # Per-sample galaxy medians
    resp_med_per_sample = np.nanmedian(resp_arr, axis=1)
    nfw_med_per_sample  = np.nanmedian(nfw_arr,  axis=1)
    prate_per_sample    = np.nanmean(resp_arr < -10, axis=1)

    def pct(arr, p):
        return float(np.nanpercentile(arr, p))

    return {
        "n_samples":    n_samples,
        "Y_disk": {
            "mean": float(Y_samples.mean()),
            "std":  float(Y_samples.std()),
            "p16":  pct(Y_samples, 16),
            "p84":  pct(Y_samples, 84),
        },
        "distance_scale": {
            "mean": float(d_samples.mean()),
            "std":  float(d_samples.std()),
            "p16":  pct(d_samples, 16),
            "p84":  pct(d_samples, 84),
        },
        "response_dbic_vs_bar": {
            "nominal":      float(np.nanmedian(resp_arr)),
            "p16":          pct(resp_med_per_sample, 16),
            "p50":          pct(resp_med_per_sample, 50),
            "p84":          pct(resp_med_per_sample, 84),
            "pass_rate_p16": pct(prate_per_sample, 16),
            "pass_rate_p50": pct(prate_per_sample, 50),
            "pass_rate_p84": pct(prate_per_sample, 84),
        },
        "nfw_dbic_vs_bar": {
            "nominal": float(np.nanmedian(nfw_arr)),
            "p16":     pct(nfw_med_per_sample, 16),
            "p50":     pct(nfw_med_per_sample, 50),
            "p84":     pct(nfw_med_per_sample, 84),
        },
        "pairwise_resp_vs_nfw": {
            "per_sample_medians": list(
                np.nanmedian(resp_arr - nfw_arr, axis=1).tolist()),
            "p16": pct(np.nanmedian(resp_arr - nfw_arr, axis=1), 16),
            "p50": pct(np.nanmedian(resp_arr - nfw_arr, axis=1), 50),
            "p84": pct(np.nanmedian(resp_arr - nfw_arr, axis=1), 84),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────

def fit_response_with_Ydisk(gal, Y_disk_new, sigma_kpc: float = 2.0):
    """Re-fit response model with a different Upsilon_disk value."""
    R     = gal["R"]
    V_obs = gal["V_obs"]
    errV  = gal["errV"]
    # raw component velocities aren't stored in gal by default; reconstruct
    # via stored V_bar_sq at UPS_DISK=0.5 is not easy to decompose without
    # Vdisk separately.  Load the file again — but we don't keep the path.
    # Workaround: scale the disk-component fraction.  We store Vgas/Vdisk/Vbul
    # in an extended loader.  For the sensitivity panel we'll use the baseline.
    # NOTE: this panel is a robustness check; if decomposition columns aren't
    # available we fall back to rescaling the whole V_bar_sq (approximate).
    scale = Y_disk_new / UPS_DISK
    # This is approximate: treats all baryons as disk-dominated.
    V_bar_sq_scaled = gal["V_bar_sq"] * scale
    gbar     = np.maximum(V_bar_sq_scaled, 0) / R
    r_t      = find_rt(R, gbar, A0_KMS2_KPC)
    chi_unit = chi_prime_unit(R, r_t, sigma_kpc)

    def chi2_fn(Q):
        if Q < 0:
            return 1e10
        V_model = response_model_curve(R, V_bar_sq_scaled, chi_unit, Q)
        return float(np.sum(((V_model - V_obs) / errV) ** 2))

    Q_hi = max(10.0, 2.0 * float(np.max(V_obs)) ** 2)
    res  = minimize_scalar(chi2_fn, bounds=(0.0, Q_hi), method="bounded",
                           options={"xatol": 1e-3})
    chi2_best = float(res.fun)
    n = len(R)
    k = 1
    return {"chi2": chi2_best, "bic": chi2_best + k * math.log(n), "n": n, "k": k}
    
    # Recompute V_bar_sq with this Y_disk
    from scipy.special import i0, i1, k0, k1
    x = R / (2 * R_disk)
    x = np.maximum(x, 1e-6)
    V_disk_sq = (V_flat**2 * (1 - f_gas)) * x**2 * (i0(x)*k0(x) - i1(x)*k1(x))
    V_disk_sq = np.maximum(V_disk_sq, 0) * (Y_disk / 0.5)  # scale by Y_disk ratio
    
    V_gas_sq = V_flat**2 * f_gas * (1 - np.exp(-R/R_disk)) * np.exp(-R/(4*R_disk))
    V_gas_sq = np.maximum(V_gas_sq, 0)
    
    V_bar_sq_new = V_disk_sq + V_gas_sq
    
    def old_chi2(Q):
        pass  # replaced body — kept as dead stub to allow diff tracing

# ─────────────────────────────────────────────────────────────────────────────
# 5. K-FOLD CROSS-VALIDATION  (on real SPARC data)
# ─────────────────────────────────────────────────────────────────────────────

def kfold_cv_response(gal, k_folds=5, sigma_kpc=2.0):
    """K-fold CV for IRS response model on a single real SPARC galaxy."""
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]
    n        = len(R)
    if n < k_folds * 2:
        return None

    # Pre-compute chi_unit on the full radial grid (r_t uses baryonic gbar)
    gbar     = np.maximum(V_bar_sq, 0) / R
    r_t      = find_rt(R, gbar, A0_KMS2_KPC)
    chi_unit = chi_prime_unit(R, r_t, sigma_kpc)

    indices   = np.random.permutation(n)
    fold_size = n // k_folds
    cv_errors = []

    for fold in range(k_folds):
        test_idx  = indices[fold * fold_size:(fold + 1) * fold_size]
        train_idx = np.concatenate([indices[:fold * fold_size],
                                    indices[(fold + 1) * fold_size:]])
        if len(train_idx) < 3:
            continue

        R_tr, V_tr, Vbsq_tr, e_tr, cu_tr = (
            R[train_idx], V_obs[train_idx], V_bar_sq[train_idx],
            errV[train_idx], chi_unit[train_idx])

        def chi2_tr(Q):
            if Q < 0:
                return 1e10
            return float(np.sum(((response_model_curve(R_tr, Vbsq_tr, cu_tr, Q) - V_tr) / e_tr) ** 2))

        Q_hi = max(10.0, 2.0 * float(np.max(V_obs)) ** 2)
        res  = minimize_scalar(chi2_tr, bounds=(0.0, Q_hi), method="bounded",
                               options={"xatol": 1e-3})
        Q_cv = float(res.x)

        R_te, V_te, Vbsq_te, cu_te = (
            R[test_idx], V_obs[test_idx], V_bar_sq[test_idx], chi_unit[test_idx])
        V_pred = response_model_curve(R_te, Vbsq_te, cu_te, Q_cv)
        cv_errors.append(float(np.sqrt(np.mean((V_te - V_pred) ** 2))))

    return float(np.mean(cv_errors)) if cv_errors else None


def kfold_cv_nfw(gal, k_folds=5):
    """K-fold CV for NFW model on a single real SPARC galaxy."""
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]
    n        = len(R)
    if n < k_folds * 2:
        return None

    indices   = np.random.permutation(n)
    fold_size = n // k_folds
    cv_errors = []

    for fold in range(k_folds):
        test_idx  = indices[fold * fold_size:(fold + 1) * fold_size]
        train_idx = np.concatenate([indices[:fold * fold_size],
                                    indices[(fold + 1) * fold_size:]])
        if len(train_idx) < 4:
            continue

        R_tr, V_tr, Vbsq_tr, e_tr = (
            R[train_idx], V_obs[train_idx], V_bar_sq[train_idx], errV[train_idx])

        def chi2_tr(params):
            lm, lc = params
            c = 10.0 ** lc
            if c < 3.0 or c > 40.0:
                return 1e10
            try:
                return float(np.sum(((nfw_model(R_tr, Vbsq_tr, 10.0**lm, c) - V_tr) / e_tr) ** 2))
            except Exception:
                return 1e10

        best_chi2, best_p = 1e10, [1.0, math.log10(10.0)]
        for lm in [0.5, 1.0, 1.5, 2.0]:
            for lc in [math.log10(5), math.log10(10), math.log10(20)]:
                try:
                    res = minimize(chi2_tr, [lm, lc], method="Nelder-Mead",
                                   options={"maxiter": 300})
                    if res.fun < best_chi2:
                        best_chi2 = res.fun
                        best_p    = res.x
                except Exception:
                    pass

        R_te, V_te, Vbsq_te = R[test_idx], V_obs[test_idx], V_bar_sq[test_idx]
        try:
            V_pred = nfw_model(R_te, Vbsq_te, 10.0 ** best_p[0], 10.0 ** best_p[1])
            cv_errors.append(float(np.sqrt(np.mean((V_te - V_pred) ** 2))))
        except Exception:
            pass

    return float(np.mean(cv_errors)) if cv_errors else None


def kfold_cv_rsyd(gal, k_folds=5):
    """K-fold CV for IRS+sigma+Ydisk (k=3) on a single galaxy."""
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]
    n        = len(R)
    if n < k_folds * 3:
        return None

    indices   = np.random.permutation(n)
    fold_size = n // k_folds
    cv_errors = []

    for fold in range(k_folds):
        test_idx  = indices[fold * fold_size:(fold + 1) * fold_size]
        train_idx = np.concatenate([indices[:fold * fold_size],
                                    indices[(fold + 1) * fold_size:]])
        if len(train_idx) < 5:
            continue

        R_tr, V_tr, Vbsq_tr, e_tr = (
            R[train_idx], V_obs[train_idx], V_bar_sq[train_idx], errV[train_idx])

        def chi2_tr(params):
            log_Q, log_sig, Y = params
            Q = 10.0 ** log_Q;  sigma = 10.0 ** log_sig
            if Q < 0 or sigma < 0.3 or sigma > 10.0 or Y < 0.1 or Y > 1.5:
                return 1e10
            try:
                scale    = Y / UPS_DISK
                Vbsq_sc  = Vbsq_tr * scale
                gbar     = np.maximum(Vbsq_sc, 0) / R_tr
                r_t      = find_rt(R_tr, gbar, A0_KMS2_KPC)
                cu       = chi_prime_unit(R_tr, r_t, sigma)
                return float(np.sum(((response_model_curve(R_tr, Vbsq_sc, cu, Q) - V_tr) / e_tr) ** 2))
            except Exception:
                return 1e10

        Q_hi_log = math.log10(max(10.0, 2.0 * float(np.max(V_obs)) ** 2))
        best_chi2, best_p = 1e10, [1.0, math.log10(2.0), 0.6]
        for lq in [0.0, Q_hi_log * 0.5]:
            for ls in [math.log10(1.0), math.log10(3.0)]:
                for Y0 in [0.5, 0.8]:
                    try:
                        res = minimize(chi2_tr, [lq, ls, Y0], method="Nelder-Mead",
                                       options={"maxiter": 600})
                        if res.fun < best_chi2:
                            best_chi2 = res.fun;  best_p = res.x
                    except Exception:
                        pass

        R_te, V_te, Vbsq_te, e_te = (
            R[test_idx], V_obs[test_idx], V_bar_sq[test_idx], errV[test_idx])
        try:
            scale    = float(best_p[2]) / UPS_DISK
            Vbsq_sc  = Vbsq_te * scale
            gbar     = np.maximum(Vbsq_sc, 0) / R_te
            r_t      = find_rt(R_te, gbar, A0_KMS2_KPC)
            cu       = chi_prime_unit(R_te, r_t, 10.0 ** best_p[1])
            V_pred   = response_model_curve(R_te, Vbsq_sc, cu, 10.0 ** best_p[0])
            cv_errors.append(float(np.sqrt(np.mean((V_te - V_pred) ** 2))))
        except Exception:
            pass

    return float(np.mean(cv_errors)) if cv_errors else None


def kfold_cv_nydk(gal, k_folds=5):
    """K-fold CV for NFW+Ydisk (k=3) on a single galaxy."""
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]
    n        = len(R)
    if n < k_folds * 3:
        return None

    indices   = np.random.permutation(n)
    fold_size = n // k_folds
    cv_errors = []

    for fold in range(k_folds):
        test_idx  = indices[fold * fold_size:(fold + 1) * fold_size]
        train_idx = np.concatenate([indices[:fold * fold_size],
                                    indices[(fold + 1) * fold_size:]])
        if len(train_idx) < 5:
            continue

        R_tr, V_tr, Vbsq_tr, e_tr = (
            R[train_idx], V_obs[train_idx], V_bar_sq[train_idx], errV[train_idx])

        def chi2_tr(params):
            lm, lc, Y = params
            c = 10.0 ** lc
            if c < 3.0 or c > 40.0 or Y < 0.1 or Y > 1.5:
                return 1e10
            try:
                Vbsq_sc = Vbsq_tr * (Y / UPS_DISK)
                return float(np.sum(((nfw_model(R_tr, Vbsq_sc, 10.0**lm, c) - V_tr) / e_tr) ** 2))
            except Exception:
                return 1e10

        best_chi2, best_p = 1e10, [1.0, math.log10(10.0), 0.5]
        for lm in [0.5, 1.5]:
            for lc in [math.log10(5), math.log10(15)]:
                for Y0 in [0.5, 0.8]:
                    try:
                        res = minimize(chi2_tr, [lm, lc, Y0], method="Nelder-Mead",
                                       options={"maxiter": 600})
                        if res.fun < best_chi2:
                            best_chi2 = res.fun;  best_p = res.x
                    except Exception:
                        pass

        R_te, V_te, Vbsq_te = R[test_idx], V_obs[test_idx], V_bar_sq[test_idx]
        try:
            Vbsq_sc = Vbsq_te * (float(best_p[2]) / UPS_DISK)
            V_pred  = nfw_model(R_te, Vbsq_sc, 10.0 ** best_p[0], 10.0 ** best_p[1])
            cv_errors.append(float(np.sqrt(np.mean((V_te - V_pred) ** 2))))
        except Exception:
            pass

    return float(np.mean(cv_errors)) if cv_errors else None


def kfold_cv_disk_ydisk(gal, k_folds=5):
    """K-fold CV for IRS with disk-kernel sourced by SBdisk/SBbul (k=2: Q, Υ_disk).

    Key property: the chi_unit kernel is computed from the photometric
    SBdisk/SBbul profile of the FULL galaxy (not refitted per fold).  This is
    legitimate because SBdisk comes from imaging, which is independent of the
    kinematic rotation-curve data being cross-validated.  There is zero leakage.

    The only fold-specific quantities are Q and Υ_disk (fitted on training fold,
    evaluated on test fold).
    """
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]
    SBdisk   = gal["SBdisk"]
    SBbul    = gal["SBbul"]
    # Disk-kernel: IRS(Q+Υ, k=2, σ from SBdisk photometry) — Option B
    dbic_disk          = r_disk["bic"] - r_bar["bic"]
    dbic_disk_vs_nfw   = r_disk["bic"] - r_nfw["bic"]
    dbic_disk_vs_nydk  = r_disk["bic"] - r_nydk["bic"]
    n        = len(R)
    if n < k_folds * 2:
        return None

    # Kernel computed once from full photometric profile — NOT refitted per fold
    chi_unit = chi_prime_disk_kernel(R, SBdisk, SBbul)
    if np.all(chi_unit == 0):
        return None

    indices   = np.random.permutation(n)
    fold_size = n // k_folds
    cv_errors = []

    for fold in range(k_folds):
        test_idx  = indices[fold * fold_size:(fold + 1) * fold_size]
        train_idx = np.concatenate([indices[:fold * fold_size],
                                    indices[(fold + 1) * fold_size:]])
        if len(train_idx) < 4:
            continue

        R_tr, V_tr, Vbsq_tr, e_tr, cu_tr = (
            R[train_idx], V_obs[train_idx], V_bar_sq[train_idx],
            errV[train_idx], chi_unit[train_idx])

        def chi2_tr(params):
            log_Q, Y = params
            Q = 10.0 ** log_Q
            if Q < 0 or Y < 0.1 or Y > 1.5:
                return 1e10
            try:
                scale   = Y / UPS_DISK
                Vbsq_sc = Vbsq_tr * scale
                return float(np.sum(((response_model_curve(R_tr, Vbsq_sc, cu_tr, Q) - V_tr) / e_tr) ** 2))
            except Exception:
                return 1e10

        Q_hi_log = math.log10(max(10.0, 2.0 * float(np.max(V_obs)) ** 2))
        best_chi2, best_p = 1e10, [1.0, 0.6]
        for lq in [0.0, Q_hi_log * 0.5]:
            for Y0 in [0.4, 0.7, 1.0]:
                try:
                    res = minimize(chi2_tr, [lq, Y0], method="Nelder-Mead",
                                   options={"maxiter": 600})
                    if res.fun < best_chi2:
                        best_chi2 = res.fun;  best_p = res.x
                except Exception:
                    pass

        # Evaluate on test fold — kernel already computed, no refitting needed
        R_te  = R[test_idx];    V_te  = V_obs[test_idx]
        Vbsq_te = V_bar_sq[test_idx] * (float(best_p[1]) / UPS_DISK)
        cu_te = chi_unit[test_idx]
        try:
            V_pred = response_model_curve(R_te, Vbsq_te, cu_te, 10.0 ** float(best_p[0]))
            cv_errors.append(float(np.sqrt(np.mean((V_te - V_pred) ** 2))))
        except Exception:
            pass

    return float(np.mean(cv_errors)) if cv_errors else None


def kfold_cv_fsig(gal, alpha=None, k_folds=5):
    """K-fold CV for IRS with prescribed σ = α·R_t (k=2: Q and Υ_disk free)."""
    if alpha is None:
        alpha = ALPHA_SIGMA
    R        = gal["R"]
    V_obs    = gal["V_obs"]
    errV     = gal["errV"]
    V_bar_sq = gal["V_bar_sq"]
    n        = len(R)
    if n < k_folds * 2:
        return None

    indices   = np.random.permutation(n)
    fold_size = n // k_folds
    cv_errors = []

    for fold in range(k_folds):
        test_idx  = indices[fold * fold_size:(fold + 1) * fold_size]
        train_idx = np.concatenate([indices[:fold * fold_size],
                                    indices[(fold + 1) * fold_size:]])
        if len(train_idx) < 4:
            continue

        R_tr, V_tr, Vbsq_tr, e_tr = (
            R[train_idx], V_obs[train_idx], V_bar_sq[train_idx], errV[train_idx])

        def chi2_tr(params):
            log_Q, Y = params
            Q = 10.0 ** log_Q
            if Q < 0 or Y < 0.1 or Y > 1.5:
                return 1e10
            try:
                scale   = Y / UPS_DISK
                Vbsq_sc = Vbsq_tr * scale
                gbar    = np.maximum(Vbsq_sc, 0) / R_tr
                r_t     = find_rt(R_tr, gbar, A0_KMS2_KPC)
                sigma   = alpha * r_t             # prescribed σ
                cu      = chi_prime_unit(R_tr, r_t, sigma)
                return float(np.sum(((response_model_curve(R_tr, Vbsq_sc, cu, Q) - V_tr) / e_tr) ** 2))
            except Exception:
                return 1e10

        Q_hi_log = math.log10(max(10.0, 2.0 * float(np.max(V_obs)) ** 2))
        best_chi2, best_p = 1e10, [1.0, 0.6]
        for lq in [0.0, Q_hi_log * 0.5]:
            for Y0 in [0.4, 0.7, 1.0]:
                try:
                    res = minimize(chi2_tr, [lq, Y0], method="Nelder-Mead",
                                   options={"maxiter": 600})
                    if res.fun < best_chi2:
                        best_chi2 = res.fun;  best_p = res.x
                except Exception:
                    pass

        # Evaluate on test fold using FULL galaxy R_t at best-fit Υ_disk
        Y_cv = float(best_p[1])
        Q_cv = 10.0 ** float(best_p[0])
        try:
            scale_full   = Y_cv / UPS_DISK
            Vbsq_full    = V_bar_sq * scale_full
            gbar_full    = np.maximum(Vbsq_full, 0) / R
            r_t_full     = find_rt(R, gbar_full, A0_KMS2_KPC)
            sigma_full   = alpha * r_t_full
            cu_full      = chi_prime_unit(R, r_t_full, sigma_full)
            R_te   = R[test_idx];  V_te = V_obs[test_idx]
            Vbsq_te = Vbsq_full[test_idx];  cu_te = cu_full[test_idx]
            V_pred = response_model_curve(R_te, Vbsq_te, cu_te, Q_cv)
            cv_errors.append(float(np.sqrt(np.mean((V_te - V_pred) ** 2))))
        except Exception:
            pass

    return float(np.mean(cv_errors)) if cv_errors else None


# ─────────────────────────────────────────────────────────────────────────────
# 6. MAIN ANALYSIS  — real SPARC data
# ─────────────────────────────────────────────────────────────────────────────

print("Loading real SPARC rotmod files...")
galaxies = load_all_galaxies()
print(f"Fitting {len(galaxies)} galaxies with all models...")

results = []
for i, gal in enumerate(galaxies):
    if i % 25 == 0:
        print(f"  Galaxy {i+1}/{len(galaxies)}: {gal['name']}")
    try:
        r_resp  = fit_response(gal)
        r_bar   = fit_baryons_only(gal)
        r_nfw   = fit_nfw(gal)
        r_bur   = fit_burkert(gal)
        r_rsig  = fit_response_sigma(gal)
        r_rydk  = fit_response_ydisk(gal)
        r_nydk  = fit_nfw_ydisk(gal)
        r_rsyd  = fit_response_sigma_ydisk(gal)
        r_fsgd  = fit_response_fsig_ydisk(gal)   # prescribed σ = α·R_t, k=2
        r_disk  = fit_response_disk_ydisk(gal)    # disk-kernel, k=2 (Option B)
    except Exception as exc:
        print(f"    SKIP {gal['name']}: {exc}")
        continue

    dbic_resp          = r_resp["bic"] - r_bar["bic"]
    dbic_nfw           = r_nfw["bic"]  - r_bar["bic"]
    dbic_bur           = r_bur["bic"]  - r_bar["bic"]
    dbic_resp_vs_nfw   = r_resp["bic"] - r_nfw["bic"]
    dbic_resp_vs_bur   = r_resp["bic"] - r_bur["bic"]
    dbic_rsig          = r_rsig["bic"] - r_bar["bic"]
    dbic_rydk          = r_rydk["bic"] - r_bar["bic"]
    dbic_nydk          = r_nydk["bic"] - r_bar["bic"]
    dbic_rsyd          = r_rsyd["bic"] - r_bar["bic"]
    dbic_rsig_vs_nfw   = r_rsig["bic"] - r_nfw["bic"]
    dbic_rydk_vs_nfw   = r_rydk["bic"] - r_nfw["bic"]
    dbic_rydk_vs_nydk  = r_rydk["bic"] - r_nydk["bic"]
    # Equal budget: IRS(Q+σ+Υ, k=3) vs NFW(M_vir+c+Υ, k=3)
    dbic_rsyd_vs_nydk  = r_rsyd["bic"] - r_nydk["bic"]
    # Prescribed-σ: IRS(Q+Υ, k=2, σ=α·R_t) vs NFW+Υ (k=3) — IRS has one fewer parameter
    dbic_fsgd          = r_fsgd["bic"] - r_bar["bic"]
    dbic_fsgd_vs_nfw   = r_fsgd["bic"] - r_nfw["bic"]
    dbic_fsgd_vs_nydk  = r_fsgd["bic"] - r_nydk["bic"]
    # Disk-kernel: IRS(Q+Υ, k=2, σ from SBdisk photometry) — Option B
    dbic_disk          = r_disk["bic"] - r_bar["bic"]
    dbic_disk_vs_nfw   = r_disk["bic"] - r_nfw["bic"]
    dbic_disk_vs_nydk  = r_disk["bic"] - r_nydk["bic"]

    results.append({
        "galaxy":              gal["name"],
        "n_pts":               r_resp["n"],
        "Q_best":              r_resp["Q"],
        "r_t_kpc":             r_resp.get("r_t", float("nan")),
        "chi2_resp":           r_resp["chi2"],
        "chi2_bar":            r_bar["chi2"],
        "chi2_nfw":            r_nfw["chi2"],
        "chi2_bur":            r_bur["chi2"],
        "chi2_rsig":           r_rsig["chi2"],
        "chi2_rydk":           r_rydk["chi2"],
        "chi2_nydk":           r_nydk["chi2"],
        "chi2_rsyd":           r_rsyd["chi2"],
        "bic_resp":            r_resp["bic"],
        "bic_bar":             r_bar["bic"],
        "bic_nfw":             r_nfw["bic"],
        "bic_bur":             r_bur["bic"],
        "bic_rsig":            r_rsig["bic"],
        "bic_rydk":            r_rydk["bic"],
        "bic_nydk":            r_nydk["bic"],
        "bic_rsyd":            r_rsyd["bic"],
        "dbic_resp":           dbic_resp,
        "dbic_nfw":            dbic_nfw,
        "dbic_bur":            dbic_bur,
        "dbic_resp_vs_nfw":    dbic_resp_vs_nfw,
        "dbic_resp_vs_bur":    dbic_resp_vs_bur,
        "dbic_rsig":           dbic_rsig,
        "dbic_rydk":           dbic_rydk,
        "dbic_nydk":           dbic_nydk,
        "dbic_rsyd":           dbic_rsyd,
        "dbic_rsig_vs_nfw":    dbic_rsig_vs_nfw,
        "dbic_rydk_vs_nfw":    dbic_rydk_vs_nfw,
        "dbic_rydk_vs_nydk":   dbic_rydk_vs_nydk,
        "dbic_rsyd_vs_nydk":   dbic_rsyd_vs_nydk,
        "sigma_fit_kpc":       r_rsig.get("sigma_kpc", float("nan")),
        "sigma_fit_k3_kpc":    r_rsyd.get("sigma_kpc", float("nan")),
        "Y_disk_fit":          r_rydk.get("Y_disk",    float("nan")),
        "Y_disk_k3_fit":       r_rsyd.get("Y_disk",    float("nan")),
        "Y_disk_nfw_fit":      r_nydk.get("Y_disk",    float("nan")),
        "M_vir_nfw":           r_nfw.get("M_vir",      float("nan")),
        "c_nfw":               r_nfw.get("c",           float("nan")),
        "distance_mpc":        gal.get("distance_mpc",  float("nan")),
        # Prescribed-σ model (k=2, σ = ALPHA_SIGMA × R_t)
        "bic_fsgd":            r_fsgd["bic"],
        "chi2_fsgd":           r_fsgd["chi2"],
        "dbic_fsgd":           dbic_fsgd,
        "dbic_fsgd_vs_nfw":    dbic_fsgd_vs_nfw,
        "dbic_fsgd_vs_nydk":   dbic_fsgd_vs_nydk,
        "sigma_prescribed_kpc": r_fsgd.get("sigma_prescribed_kpc", float("nan")),
        "Y_disk_fsgd_fit":     r_fsgd.get("Y_disk", float("nan")),
        # Disk-kernel model (Option B: σ from SBdisk photometry)
        "bic_disk":            r_disk["bic"],
        "chi2_disk":           r_disk["chi2"],
        "dbic_disk":           dbic_disk,
        "dbic_disk_vs_nfw":    dbic_disk_vs_nfw,
        "dbic_disk_vs_nydk":   dbic_disk_vs_nydk,
        "Y_disk_disk_fit":     r_disk.get("Y_disk", float("nan")),
    })

df = pd.DataFrame(results)

# ─────────────────────────────────────────────────────────────────────────────
# 7. K-FOLD CV  (real data)
# ─────────────────────────────────────────────────────────────────────────────
print(f"\nRunning 5-fold cross-validation on {len(galaxies)} galaxies (6 models)...")
cv_resp_list, cv_nfw_list, cv_rsyd_list, cv_nydk_list, cv_fsgd_list, cv_disk_list = [], [], [], [], [], []
for i, gal in enumerate(galaxies):
    if i % 50 == 0:
        print(f"  CV galaxy {i+1}/{len(galaxies)}...")
    np.random.seed(i)
    cv_resp_list.append(kfold_cv_response(gal))
    cv_nfw_list.append(kfold_cv_nfw(gal))
    cv_rsyd_list.append(kfold_cv_rsyd(gal))
    cv_nydk_list.append(kfold_cv_nydk(gal))
    cv_fsgd_list.append(kfold_cv_fsig(gal))          # prescribed σ = α·R_t
    cv_disk_list.append(kfold_cv_disk_ydisk(gal))     # disk-kernel from SBdisk

cv_resp = np.array([x for x in cv_resp_list if x is not None])
cv_nfw  = np.array([x for x in cv_nfw_list  if x is not None])
cv_rsyd = np.array([x for x in cv_rsyd_list if x is not None])
cv_nydk = np.array([x for x in cv_nydk_list if x is not None])
cv_fsgd = np.array([x for x in cv_fsgd_list if x is not None])
cv_disk = np.array([x for x in cv_disk_list if x is not None])

# ─────────────────────────────────────────────────────────────────────────────
# 7.5  PRIOR-PENALIZED BIC  (Bayesian evidence with physical Υ_disk prior)
# ─────────────────────────────────────────────────────────────────────────────
# For models with a free Υ_disk parameter, the BIC implicitly assumes a flat
# prior over [0.1, 1.5].  A physically motivated prior from stellar population
# synthesis concentrates mass in [0.4, 1.0].  We apply a LogNormal(μ=0.6,
# σ=0.15 dex) prior correction:  BIC_prior = BIC − 2·log π(Υ_best).
# For σ_kpc we apply LogNormal(μ=2.0 kpc, σ=0.5 dex).  Models without those
# free parameters are unchanged.
_LN_NORM_UPS = math.log(2 * math.pi * (0.15 ** 2)) / 2          # log-normalisation
_MU_UPS      = math.log(0.6)                                      # log-mean for Υ prior
_SIG_UPS     = 0.15                                               # dex std
_LN_NORM_SIG = math.log(2 * math.pi * (0.50 ** 2)) / 2
_MU_SIG      = math.log(2.0)                                      # log-mean for σ prior (kpc)
_SIG_SIG     = 0.50

def log_prior_upsilon(Y):
    """LogNormal(μ=0.6, σ=0.15 dex) prior on Υ_disk."""
    if Y <= 0:
        return -1e10
    lny  = math.log(Y)
    return -(lny - _MU_UPS) ** 2 / (2 * _SIG_UPS ** 2) - math.log(Y) - _LN_NORM_UPS

def log_prior_sigma(s):
    """LogNormal(μ=2.0 kpc, σ=0.5 dex) weakly informative prior on σ_kpc."""
    if s <= 0:
        return -1e10
    lns  = math.log(s)
    return -(lns - _MU_SIG) ** 2 / (2 * _SIG_SIG ** 2) - math.log(s) - _LN_NORM_SIG

# Apply prior correction to per-galaxy BIC columns
_rydk_Y   = df["Y_disk_fit"].values
_nydk_Y   = df["Y_disk_nfw_fit"].values
_rsyd_Y   = df["Y_disk_k3_fit"].values
_rsyd_sig = df["sigma_fit_k3_kpc"].values
_rsig_sig = df["sigma_fit_kpc"].values

df["bic_prior_rydk"]  = df["bic_rydk"]  - 2 * np.array([log_prior_upsilon(y) for y in _rydk_Y])
df["bic_prior_nydk"]  = df["bic_nydk"]  - 2 * np.array([log_prior_upsilon(y) for y in _nydk_Y])
df["bic_prior_rsyd"]  = df["bic_rsyd"]  \
    - 2 * np.array([log_prior_upsilon(y) for y in _rsyd_Y]) \
    - 2 * np.array([log_prior_sigma(s)   for s in _rsyd_sig])
df["bic_prior_rsig"]  = df["bic_rsig"]  - 2 * np.array([log_prior_sigma(s)  for s in _rsig_sig])

# Pairwise prior-corrected comparisons (lower = model preferred)
df["dbic_prior_rydk_vs_nydk"]  = df["bic_prior_rydk"] - df["bic_prior_nydk"]
df["dbic_prior_rsyd_vs_nydk"]  = df["bic_prior_rsyd"] - df["bic_prior_nydk"]
df["dbic_prior_rydk_vs_bar"]   = df["bic_prior_rydk"] - df["bic_bar"]
df["dbic_prior_nydk_vs_bar"]   = df["bic_prior_nydk"] - df["bic_bar"]

# ─────────────────────────────────────────────────────────────────────────────
# 8. Y_DISK MARGINALIZATION  (real data, approximate)
# ─────────────────────────────────────────────────────────────────────────────
print("\nRunning Upsilon_disk marginalization sensitivity...")
Y_disk_values  = [0.3, 0.4, 0.5, 0.6, 0.7]
ydisk_bic_summary = {}

for Y in Y_disk_values:
    bics_y    = []
    bics_bar  = []
    for gal in galaxies:
        try:
            r_y   = fit_response_with_Ydisk(gal, Y)
            r_bar = fit_baryons_only(gal)
            bics_y.append(r_y["bic"])
            bics_bar.append(r_bar["bic"])
        except Exception:
            pass
    dbic_arr = np.array(bics_y) - np.array(bics_bar)
    ydisk_bic_summary[str(Y)] = {
        "median_dbic": float(np.median(dbic_arr)),
        "pass_rate":   float(np.mean(dbic_arr < -10)),
    }

# ─────────────────────────────────────────────────────────────────────────────
# 8.5 BARYONIC UNCERTAINTY MONTE CARLO
# ─────────────────────────────────────────────────────────────────────────────
mc_results = bic_mc_uncertainty(galaxies, df, n_samples=50, seed=42)


print("\n--- BIC vs Baryons-Only ---")
print(f"Response (k=1):         median ΔBIC = {df['dbic_resp'].median():.1f}, pass rate (<-10) = {(df['dbic_resp']<-10).mean()*100:.1f}%")
print(f"NFW (k=2):              median ΔBIC = {df['dbic_nfw'].median():.1f}, pass rate (<-10) = {(df['dbic_nfw']<-10).mean()*100:.1f}%")
print(f"Burkert (k=2):          median ΔBIC = {df['dbic_bur'].median():.1f}, pass rate (<-10) = {(df['dbic_bur']<-10).mean()*100:.1f}%")
print(f"Resp+sigma (k=2):       median ΔBIC = {df['dbic_rsig'].median():.1f}, pass rate (<-10) = {(df['dbic_rsig']<-10).mean()*100:.1f}%")
print(f"Resp+Ydisk (k=2):       median ΔBIC = {df['dbic_rydk'].median():.1f}, pass rate (<-10) = {(df['dbic_rydk']<-10).mean()*100:.1f}%")
print(f"NFW+Ydisk  (k=3):       median ΔBIC = {df['dbic_nydk'].median():.1f}, pass rate (<-10) = {(df['dbic_nydk']<-10).mean()*100:.1f}%")
print(f"Resp+sigma+Ydisk (k=3): median ΔBIC = {df['dbic_rsyd'].median():.1f}, pass rate (<-10) = {(df['dbic_rsyd']<-10).mean()*100:.1f}%")

print("\n--- Response vs Halo Models (ΔBIC = BIC_resp - BIC_halo) ---")
print(f"Response(k=1) vs NFW(k=2):     median ΔBIC = {df['dbic_resp_vs_nfw'].median():.1f}")
print(f"  Response favored (ΔBIC<0): {(df['dbic_resp_vs_nfw']<0).mean()*100:.1f}%")
print(f"  Response strongly favored (ΔBIC<-2): {(df['dbic_resp_vs_nfw']<-2).mean()*100:.1f}%")
print(f"  NFW strongly favored (ΔBIC>+2): {(df['dbic_resp_vs_nfw']>2).mean()*100:.1f}%")
print(f"Response vs Burkert: median ΔBIC = {df['dbic_resp_vs_bur'].median():.1f}")
print(f"  Response favored (ΔBIC<0): {(df['dbic_resp_vs_bur']<0).mean()*100:.1f}%")

print("\n--- Option A: Resp+sigma(k=2) vs NFW(k=2) ---")
print(f"  Resp+sigma vs NFW:  median ΔBIC = {df['dbic_rsig_vs_nfw'].median():.1f}")
print(f"  Resp+sigma favored (ΔBIC<0): {(df['dbic_rsig_vs_nfw']<0).mean()*100:.1f}%")
print(f"  Resp+sigma strongly favored (ΔBIC<-2): {(df['dbic_rsig_vs_nfw']<-2).mean()*100:.1f}%")
sig_vals = df['sigma_fit_kpc'].dropna()
print(f"  Fitted sigma: median={sig_vals.median():.2f} kpc, mean={sig_vals.mean():.2f} kpc, "
      f"range=[{sig_vals.min():.2f}, {sig_vals.max():.2f}]")

print("\n--- Option B: Resp+Ydisk(k=2) vs NFW(k=2) ---")
print(f"  Resp+Ydisk vs NFW(k=2):  median ΔBIC = {df['dbic_rydk_vs_nfw'].median():.1f}")
print(f"  Resp+Ydisk favored (ΔBIC<0): {(df['dbic_rydk_vs_nfw']<0).mean()*100:.1f}%")
print(f"  Resp+Ydisk strongly favored (ΔBIC<-2): {(df['dbic_rydk_vs_nfw']<-2).mean()*100:.1f}%")
ydk_vals = df['Y_disk_fit'].dropna()
print(f"  Fitted Ydisk (IRS): median={ydk_vals.median():.3f}, mean={ydk_vals.mean():.3f}, "
      f"range=[{ydk_vals.min():.3f}, {ydk_vals.max():.3f}]")

print("\n--- FAIR TEST A: Resp+Ydisk(k=2) vs NFW+Ydisk(k=3) ---")
print(f"  IRS+Υ(k=2) vs NFW+Υ(k=3):  median ΔBIC = {df['dbic_rydk_vs_nydk'].median():.1f}")
print(f"  IRS+Υ favored (ΔBIC<0): {(df['dbic_rydk_vs_nydk']<0).mean()*100:.1f}%")
print(f"  IRS+Υ strongly favored (ΔBIC<-2): {(df['dbic_rydk_vs_nydk']<-2).mean()*100:.1f}%")
print(f"  NFW+Υ strongly favored (ΔBIC>+2): {(df['dbic_rydk_vs_nydk']>2).mean()*100:.1f}%")
nydk_vals = df['Y_disk_nfw_fit'].dropna()
print(f"  Fitted Ydisk (NFW): median={nydk_vals.median():.3f}, mean={nydk_vals.mean():.3f}, "
      f"range=[{nydk_vals.min():.3f}, {nydk_vals.max():.3f}]")

print("\n--- EQUAL BUDGET TEST: IRS(Q+σ+Υ, k=3) vs NFW(M+c+Υ, k=3) ---")
rsyd_vals_sig = df['sigma_fit_k3_kpc'].dropna()
rsyd_vals_ydk = df['Y_disk_k3_fit'].dropna()
print(f"  IRS(k=3) vs NFW+Υ(k=3):  median ΔBIC = {df['dbic_rsyd_vs_nydk'].median():.1f}")
print(f"  IRS(k=3) favored (ΔBIC<0): {(df['dbic_rsyd_vs_nydk']<0).mean()*100:.1f}%")
print(f"  IRS(k=3) strongly favored (ΔBIC<-2): {(df['dbic_rsyd_vs_nydk']<-2).mean()*100:.1f}%")
print(f"  NFW(k=3) strongly favored (ΔBIC>+2): {(df['dbic_rsyd_vs_nydk']>2).mean()*100:.1f}%")
print(f"  Fitted sigma (k=3): median={rsyd_vals_sig.median():.2f} kpc, mean={rsyd_vals_sig.mean():.2f} kpc")
print(f"  Fitted Ydisk (k=3): median={rsyd_vals_ydk.median():.3f}, mean={rsyd_vals_ydk.mean():.3f}")

print("\n--- 5-Fold Cross-Validation ---")
print(f"Response k=1:                   mean CV-RMSE = {cv_resp.mean():.2f} ± {cv_resp.std():.2f} km/s")
print(f"NFW k=2:                        mean CV-RMSE = {cv_nfw.mean():.2f} ± {cv_nfw.std():.2f} km/s")
print(f"IRS+disk-kernel k=2 (Opt.B):    mean CV-RMSE = {cv_disk.mean():.2f} ± {cv_disk.std():.2f} km/s  [SBdisk source]")
print(f"IRS+σ(prescribed) k=2:          mean CV-RMSE = {cv_fsgd.mean():.2f} ± {cv_fsgd.std():.2f} km/s  [α={ALPHA_SIGMA}]")
print(f"IRS+sigma+Υ k=3:                mean CV-RMSE = {cv_rsyd.mean():.2f} ± {cv_rsyd.std():.2f} km/s")
print(f"NFW+Υ k=3:                      mean CV-RMSE = {cv_nydk.mean():.2f} ± {cv_nydk.std():.2f} km/s")
n_p12  = min(len(cv_resp), len(cv_nfw))
n_p34  = min(len(cv_rsyd), len(cv_nydk))
n_pf2  = min(len(cv_fsgd), len(cv_nfw))
n_pfn  = min(len(cv_fsgd), len(cv_nydk))
n_pd2  = min(len(cv_disk), len(cv_nfw))
n_pdn  = min(len(cv_disk), len(cv_nydk))
print(f"Unequal k=1 IRS vs k=2 NFW (paired):                     Δ = {(cv_nfw[:n_p12] - cv_resp[:n_p12]).mean():.2f} km/s")
print(f"Disk-kernel k=2 IRS vs k=2 NFW (paired):                  Δ = {(cv_nfw[:n_pd2] - cv_disk[:n_pd2]).mean():.2f} km/s  ← KEY")
print(f"Disk-kernel k=2 IRS vs k=3 NFW+Υ (paired, IRS cheaper):  Δ = {(cv_nydk[:n_pdn] - cv_disk[:n_pdn]).mean():.2f} km/s")
print(f"Prescribed-σ k=2 IRS vs k=2 NFW (paired):                 Δ = {(cv_nfw[:n_pf2] - cv_fsgd[:n_pf2]).mean():.2f} km/s")
print(f"Prescribed-σ k=2 IRS vs k=3 NFW+Υ (paired, IRS cheaper):  Δ = {(cv_nydk[:n_pfn] - cv_fsgd[:n_pfn]).mean():.2f} km/s")
print(f"Equal budget k=3 IRS vs k=3 NFW (paired):                 Δ = {(cv_nydk[:n_p34] - cv_rsyd[:n_p34]).mean():.2f} km/s")

print("\n--- Disk-Kernel IRS BIC (Option B: σ from SBdisk photometry, k=2) ---")
disk_vals_Y = df['Y_disk_disk_fit'].dropna()
print(f"  IRS+disk-kernel(k=2) vs bar:      median ΔBIC = {df['dbic_disk'].median():.1f}, pass rate = {(df['dbic_disk']<-10).mean()*100:.1f}%")
print(f"  IRS+disk-kernel(k=2) vs NFW(k=2): median ΔBIC = {df['dbic_disk_vs_nfw'].median():.1f}")
print(f"    IRS disk favored (ΔBIC<0): {(df['dbic_disk_vs_nfw']<0).mean()*100:.1f}%")
print(f"  IRS+disk-kernel(k=2) vs NFW+Υ(k=3): median ΔBIC = {df['dbic_disk_vs_nydk'].median():.1f}")
print(f"    IRS disk favored (ΔBIC<0): {(df['dbic_disk_vs_nydk']<0).mean()*100:.1f}%")
print(f"    IRS disk strongly favored (ΔBIC<-2): {(df['dbic_disk_vs_nydk']<-2).mean()*100:.1f}%")
print(f"    NFW+Υ strongly favored (ΔBIC>+2): {(df['dbic_disk_vs_nydk']>2).mean()*100:.1f}%")
print(f"  Fitted Υ_disk: median={disk_vals_Y.median():.3f}, mean={disk_vals_Y.mean():.3f}")

print("\n--- Prescribed-σ BIC (σ = α·R_t, α={:.2f}) ---".format(ALPHA_SIGMA))
fsgd_vals_Y   = df['Y_disk_fsgd_fit'].dropna()
fsgd_vals_sig = df['sigma_prescribed_kpc'].dropna()
print(f"  IRS+Υ(k=2, σ=α·R_t) vs bar:      median ΔBIC = {df['dbic_fsgd'].median():.1f}, pass rate = {(df['dbic_fsgd']<-10).mean()*100:.1f}%")
print(f"  IRS+Υ(k=2, σ=α·R_t) vs NFW(k=2): median ΔBIC = {df['dbic_fsgd_vs_nfw'].median():.1f}")
print(f"  IRS+Υ(k=2, σ=α·R_t) vs NFW+Υ(k=3): median ΔBIC = {df['dbic_fsgd_vs_nydk'].median():.1f}")
print(f"    IRS prescribed favored (ΔBIC<0): {(df['dbic_fsgd_vs_nydk']<0).mean()*100:.1f}%")
print(f"    IRS prescribed strongly favored (ΔBIC<-2): {(df['dbic_fsgd_vs_nydk']<-2).mean()*100:.1f}%")
print(f"    NFW+Υ strongly favored (ΔBIC>+2): {(df['dbic_fsgd_vs_nydk']>2).mean()*100:.1f}%")
print(f"  Prescribed σ: median={fsgd_vals_sig.median():.2f} kpc, mean={fsgd_vals_sig.mean():.2f} kpc")
print(f"  Fitted Υ_disk: median={fsgd_vals_Y.median():.3f}, mean={fsgd_vals_Y.mean():.3f}")

print("\n--- Prior-Penalized BIC (Υ_disk ~ LogNormal(0.6, 0.15 dex), σ ~ LogNormal(2 kpc, 0.5 dex)) ---")
print(f"  IRS+Υ(k=2)  prior-BIC vs bar:  median ΔBIC = {df['dbic_prior_rydk_vs_bar'].median():.1f}")
print(f"  NFW+Υ(k=3)  prior-BIC vs bar:  median ΔBIC = {df['dbic_prior_nydk_vs_bar'].median():.1f}")
print(f"  IRS+Υ(k=2)  prior vs NFW+Υ(k=3) prior:  median ΔBIC = {df['dbic_prior_rydk_vs_nydk'].median():.1f}")
print(f"    IRS prior-favored (ΔBIC<0): {(df['dbic_prior_rydk_vs_nydk']<0).mean()*100:.1f}%")
print(f"  IRS(k=3)    prior vs NFW+Υ(k=3) prior:  median ΔBIC = {df['dbic_prior_rsyd_vs_nydk'].median():.1f}")
print(f"    IRS(k=3) prior-favored (ΔBIC<0): {(df['dbic_prior_rsyd_vs_nydk']<0).mean()*100:.1f}%")

print("\n--- Upsilon_disk Marginalization ---")
print(f"{'Ups_disk':>8} {'Median ΔBIC':>12} {'Pass Rate':>10}")
for Y in Y_disk_values:
    key = str(Y)
    print(f"{Y:>8.1f} {ydisk_bic_summary[key]['median_dbic']:>12.1f} "
          f"{ydisk_bic_summary[key]['pass_rate']*100:>9.1f}%")

r_mc = mc_results
print("\n--- Baryonic Uncertainty MC (Υ_disk + Distance, 50 samples × 171 galaxies) ---")
print(f"  Uncertainty inputs sampled:")
print(f"    Υ_disk:   1σ range [{r_mc['Y_disk']['p16']:.3f}, {r_mc['Y_disk']['p84']:.3f}] "
      f"(σ=0.10 dex log-normal around 0.5)")
print(f"    Distance: 1σ range [{r_mc['distance_scale']['p16']:.3f}, {r_mc['distance_scale']['p84']:.3f}]×D "
      f"(σ=12% normal)")
print(f"  Response ΔBIC vs bar:  {r_mc['response_dbic_vs_bar']['p50']:.0f}  "
      f"[{r_mc['response_dbic_vs_bar']['p16']:.0f}, {r_mc['response_dbic_vs_bar']['p84']:.0f}] (16–84th pct)")
print(f"  NFW ΔBIC vs bar:       {r_mc['nfw_dbic_vs_bar']['p50']:.0f}  "
      f"[{r_mc['nfw_dbic_vs_bar']['p16']:.0f}, {r_mc['nfw_dbic_vs_bar']['p84']:.0f}]")
print(f"  Response pass rate:    {r_mc['response_dbic_vs_bar']['pass_rate_p50']*100:.1f}%  "
      f"[{r_mc['response_dbic_vs_bar']['pass_rate_p16']*100:.1f}%, "
      f"{r_mc['response_dbic_vs_bar']['pass_rate_p84']*100:.1f}%]")
print(f"  Pairwise Resp−NFW ΔBIC: {r_mc['pairwise_resp_vs_nfw']['p50']:.1f}  "
      f"[{r_mc['pairwise_resp_vs_nfw']['p16']:.1f}, {r_mc['pairwise_resp_vs_nfw']['p84']:.1f}]")

# ─────────────────────────────────────────────────────────────────────────────
# Save results next to this script (repro_package/)
# ─────────────────────────────────────────────────────────────────────────────
csv_path  = OUT_DIR / "sparc_bic_results.csv"
json_path = OUT_DIR / "sparc_summary.json"

df.to_csv(csv_path, index=False)
print(f"\nPer-galaxy results saved to: {csv_path}")

summary = {
    "data_source":  str(ROTMOD_DIR),
    "n_galaxies":   len(df),
    "bic_vs_bar": {
        "response": {
            "median_dbic": float(df["dbic_resp"].median()),
            "pass_rate":   float((df["dbic_resp"] < -10).mean()),
        },
        "nfw": {
            "median_dbic": float(df["dbic_nfw"].median()),
            "pass_rate":   float((df["dbic_nfw"] < -10).mean()),
        },
        "burkert": {
            "median_dbic": float(df["dbic_bur"].median()),
            "pass_rate":   float((df["dbic_bur"] < -10).mean()),
        },
        "response_sigma_k2": {
            "median_dbic":      float(df["dbic_rsig"].median()),
            "pass_rate":        float((df["dbic_rsig"] < -10).mean()),
            "sigma_median_kpc": float(df["sigma_fit_kpc"].median()),
            "sigma_mean_kpc":   float(df["sigma_fit_kpc"].mean()),
        },
        "response_ydisk_k2": {
            "median_dbic":    float(df["dbic_rydk"].median()),
            "pass_rate":      float((df["dbic_rydk"] < -10).mean()),
            "ydisk_median":   float(df["Y_disk_fit"].median()),
            "ydisk_mean":     float(df["Y_disk_fit"].mean()),
        },
        "nfw_ydisk_k3": {
            "median_dbic":    float(df["dbic_nydk"].median()),
            "pass_rate":      float((df["dbic_nydk"] < -10).mean()),
            "ydisk_median":   float(df["Y_disk_nfw_fit"].median()),
            "ydisk_mean":     float(df["Y_disk_nfw_fit"].mean()),
        },
        "response_sigma_ydisk_k3": {
            "median_dbic":      float(df["dbic_rsyd"].median()),
            "pass_rate":        float((df["dbic_rsyd"] < -10).mean()),
            "sigma_median_kpc": float(df["sigma_fit_k3_kpc"].median()),
            "ydisk_median":     float(df["Y_disk_k3_fit"].median()),
        },
    },
    "response_vs_halos": {
        "vs_nfw": {
            "median_dbic":       float(df["dbic_resp_vs_nfw"].median()),
            "resp_favored_frac": float((df["dbic_resp_vs_nfw"] < 0).mean()),
            "resp_strong_frac":  float((df["dbic_resp_vs_nfw"] < -2).mean()),
            "nfw_strong_frac":   float((df["dbic_resp_vs_nfw"] > 2).mean()),
        },
        "vs_burkert": {
            "median_dbic":       float(df["dbic_resp_vs_bur"].median()),
            "resp_favored_frac": float((df["dbic_resp_vs_bur"] < 0).mean()),
        },
        "sigma_k2_vs_nfw": {
            "median_dbic":       float(df["dbic_rsig_vs_nfw"].median()),
            "resp_favored_frac": float((df["dbic_rsig_vs_nfw"] < 0).mean()),
            "resp_strong_frac":  float((df["dbic_rsig_vs_nfw"] < -2).mean()),
        },
        "ydisk_k2_vs_nfw": {
            "median_dbic":       float(df["dbic_rydk_vs_nfw"].median()),
            "resp_favored_frac": float((df["dbic_rydk_vs_nfw"] < 0).mean()),
            "resp_strong_frac":  float((df["dbic_rydk_vs_nfw"] < -2).mean()),
        },
        "fair_test_irs_ydisk_k2_vs_nfw_ydisk_k3": {
            "median_dbic":       float(df["dbic_rydk_vs_nydk"].median()),
            "irs_favored_frac":  float((df["dbic_rydk_vs_nydk"] < 0).mean()),
            "irs_strong_frac":   float((df["dbic_rydk_vs_nydk"] < -2).mean()),
            "nfw_strong_frac":   float((df["dbic_rydk_vs_nydk"] > 2).mean()),
        },
        "equal_budget_irs_k3_vs_nfw_k3": {
            "median_dbic":       float(df["dbic_rsyd_vs_nydk"].median()),
            "irs_favored_frac":  float((df["dbic_rsyd_vs_nydk"] < 0).mean()),
            "irs_strong_frac":   float((df["dbic_rsyd_vs_nydk"] < -2).mean()),
            "nfw_strong_frac":   float((df["dbic_rsyd_vs_nydk"] > 2).mean()),
            "sigma_median_kpc":  float(df["sigma_fit_k3_kpc"].median()),
            "ydisk_median":      float(df["Y_disk_k3_fit"].median()),
        },
    },
    "cv": {
        "response_k1_mean_rmse":   float(cv_resp.mean()),
        "response_k1_std_rmse":    float(cv_resp.std()),
        "nfw_k2_mean_rmse":        float(cv_nfw.mean()),
        "nfw_k2_std_rmse":         float(cv_nfw.std()),
        "irs_k3_mean_rmse":        float(cv_rsyd.mean()),
        "irs_k3_std_rmse":         float(cv_rsyd.std()),
        "nfw_k3_mean_rmse":        float(cv_nydk.mean()),
        "nfw_k3_std_rmse":         float(cv_nydk.std()),
        "unequal_k1_vs_k2_delta":  float((cv_nfw[:min(len(cv_resp),len(cv_nfw))] - cv_resp[:min(len(cv_resp),len(cv_nfw))]).mean()),
        "equal_k3_irs_vs_nfw_delta": float((cv_nydk[:min(len(cv_rsyd),len(cv_nydk))] - cv_rsyd[:min(len(cv_rsyd),len(cv_nydk))]).mean()),
        "irs_fsig_k2_mean_rmse":    float(cv_fsgd.mean()),
        "irs_fsig_k2_std_rmse":     float(cv_fsgd.std()),
        "fsig_k2_vs_nfw_k2_delta":  float((cv_nfw[:min(len(cv_fsgd),len(cv_nfw))] - cv_fsgd[:min(len(cv_fsgd),len(cv_nfw))]).mean()),
        "fsig_k2_vs_nfw_k3_delta":  float((cv_nydk[:min(len(cv_fsgd),len(cv_nydk))] - cv_fsgd[:min(len(cv_fsgd),len(cv_nydk))]).mean()),
        "alpha_sigma":              ALPHA_SIGMA,
        "disk_k2_mean_rmse":        float(cv_disk.mean()),
        "disk_k2_std_rmse":         float(cv_disk.std()),
        "disk_k2_vs_nfw_k2_delta":  float((cv_nfw[:min(len(cv_disk),len(cv_nfw))] - cv_disk[:min(len(cv_disk),len(cv_nfw))]).mean()),
        "disk_k2_vs_nfw_k3_delta":  float((cv_nydk[:min(len(cv_disk),len(cv_nydk))] - cv_disk[:min(len(cv_disk),len(cv_nydk))]).mean()),
    },
    "disk_kernel_bic": {
        "description": "IRS with kernel sourced by SBdisk+SBbul photometry (Option B, k=2)",
        "median_dbic_vs_bar":     float(df["dbic_disk"].median()),
        "pass_rate_vs_bar":       float((df["dbic_disk"] < -10).mean()),
        "median_dbic_vs_nfw_k2": float(df["dbic_disk_vs_nfw"].median()),
        "irs_disk_favored_vs_nfw_k2_frac": float((df["dbic_disk_vs_nfw"] < 0).mean()),
        "median_dbic_vs_nfw_k3": float(df["dbic_disk_vs_nydk"].median()),
        "irs_disk_favored_vs_nfw_k3_frac": float((df["dbic_disk_vs_nydk"] < 0).mean()),
        "irs_disk_strong_vs_nfw_k3_frac":  float((df["dbic_disk_vs_nydk"] < -2).mean()),
        "nfw_strong_vs_disk_irs_frac":     float((df["dbic_disk_vs_nydk"] > 2).mean()),
        "ydisk_median": float(df["Y_disk_disk_fit"].median()),
        "cv_mean_rmse": float(cv_disk.mean()),
        "cv_std_rmse":  float(cv_disk.std()),
    },
    "prior_penalized_bic": {
        "upsilon_prior":       "LogNormal(mu=0.6, sigma=0.15 dex)",
        "sigma_prior":         "LogNormal(mu=2.0 kpc, sigma=0.5 dex)",
        "irs_ydisk_k2_vs_bar": float(df["dbic_prior_rydk_vs_bar"].median()),
        "nfw_ydisk_k3_vs_bar": float(df["dbic_prior_nydk_vs_bar"].median()),
        "irs_k2_vs_nfw_k3":    float(df["dbic_prior_rydk_vs_nydk"].median()),
        "irs_k2_vs_nfw_k3_irs_favored_frac": float((df["dbic_prior_rydk_vs_nydk"] < 0).mean()),
        "irs_k3_vs_nfw_k3":    float(df["dbic_prior_rsyd_vs_nydk"].median()),
        "irs_k3_vs_nfw_k3_irs_favored_frac": float((df["dbic_prior_rsyd_vs_nydk"] < 0).mean()),
    },
    "prescribed_sigma_bic": {
        "alpha": ALPHA_SIGMA,
        "description": "IRS with sigma=alpha*R_t (k=2: Q and Y_disk free)",
        "median_dbic_vs_bar":   float(df["dbic_fsgd"].median()),
        "pass_rate_vs_bar":     float((df["dbic_fsgd"] < -10).mean()),
        "median_dbic_vs_nfw_k2": float(df["dbic_fsgd_vs_nfw"].median()),
        "median_dbic_vs_nfw_k3": float(df["dbic_fsgd_vs_nydk"].median()),
        "irs_favored_vs_nfw_k3_frac": float((df["dbic_fsgd_vs_nydk"] < 0).mean()),
        "irs_strong_vs_nfw_k3_frac":  float((df["dbic_fsgd_vs_nydk"] < -2).mean()),
        "nfw_strong_vs_irs_frac":     float((df["dbic_fsgd_vs_nydk"] > 2).mean()),
        "sigma_prescribed_median_kpc": float(df["sigma_prescribed_kpc"].median()),
        "ydisk_median": float(df["Y_disk_fsgd_fit"].median()),
        "cv_mean_rmse": float(cv_fsgd.mean()),
        "cv_std_rmse":  float(cv_fsgd.std()),
    },
    "ydisk_marginalization": ydisk_bic_summary,
    "baryonic_uncertainty_mc": mc_results,
}
with open(json_path, "w") as fh:
    json.dump(summary, fh, indent=2)
print(f"Summary statistics saved to: {json_path}")

# ─────────────────────────────────────────────────────────────────────────────
# 10. FIGURES
# ─────────────────────────────────────────────────────────────────────────────
print("\nGenerating figures...")

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle(
    "Kitcey (2026) v5.1 — BIC Model Comparison & Cross-Validation\n"
    "Real SPARC-175 rotmod data  (Lelli et al. 2016)",
    fontsize=14, fontweight="bold")

# Dynamic x-range based on actual data
d_lo = min(df["dbic_resp"].min(), df["dbic_nfw"].min(), df["dbic_bur"].min())
d_hi = max(df["dbic_resp"].max(), df["dbic_nfw"].max(), df["dbic_bur"].max())
bins = np.linspace(max(d_lo, -400), min(d_hi, 50), 50)

# Panel (a): ΔBIC vs baryons-only
ax = axes[0, 0]
ax.hist(df["dbic_resp"], bins=bins, alpha=0.7, color="#2196F3", label="Response (k=1)", density=True)
ax.hist(df["dbic_nfw"],  bins=bins, alpha=0.7, color="#FF5722", label="NFW (k=2)",      density=True)
ax.hist(df["dbic_bur"],  bins=bins, alpha=0.7, color="#4CAF50", label="Burkert (k=2)",  density=True)
ax.axvline(-10, color="k", linestyle="--", linewidth=1.5, label="ΔBIC = −10 threshold")
ax.axvline(0,   color="gray", linestyle=":", linewidth=1)
ax.set_xlabel("ΔBIC vs. Baryons-Only", fontsize=11)
ax.set_ylabel("Density", fontsize=11)
ax.set_title("(a) Model Improvement vs. Baryons-Only", fontsize=11)
ax.legend(fontsize=9)

# Panel (b): Response vs NFW pairwise
ax = axes[0, 1]
p_lo = df["dbic_resp_vs_nfw"].quantile(0.01)
p_hi = df["dbic_resp_vs_nfw"].quantile(0.99)
bins2 = np.linspace(p_lo, p_hi, 40)
ax.hist(df["dbic_resp_vs_nfw"], bins=bins2, alpha=0.8, color="#9C27B0", density=True)
ax.axvline(0,  color="k",    linestyle="--", linewidth=1.5, label="Equal BIC")
ax.axvline(-2, color="blue", linestyle=":",  linewidth=1.5, label="Response preferred (ΔBIC<−2)")
ax.axvline( 2, color="red",  linestyle=":",  linewidth=1.5, label="NFW preferred (ΔBIC>+2)")
ax.set_xlabel("ΔBIC (Response − NFW)", fontsize=11)
ax.set_ylabel("Density", fontsize=11)
ax.set_title("(b) Response vs. NFW Pairwise", fontsize=11)
ax.legend(fontsize=8)

# Panel (c): Response vs Burkert pairwise
ax = axes[0, 2]
p_lo = df["dbic_resp_vs_bur"].quantile(0.01)
p_hi = df["dbic_resp_vs_bur"].quantile(0.99)
bins3 = np.linspace(p_lo, p_hi, 40)
ax.hist(df["dbic_resp_vs_bur"], bins=bins3, alpha=0.8, color="#FF9800", density=True)
ax.axvline(0, color="k", linestyle="--", linewidth=1.5, label="Equal BIC")
ax.set_xlabel("ΔBIC (Response − Burkert)", fontsize=11)
ax.set_ylabel("Density", fontsize=11)
ax.set_title("(c) Response vs. Burkert Pairwise", fontsize=11)
ax.legend(fontsize=9)

# Panel (d): K-fold CV
ax = axes[1, 0]
n_cv = min(len(cv_resp), len(cv_nfw))
cv_data = [cv_resp[:n_cv], cv_nfw[:n_cv]]
bp = ax.boxplot(cv_data, labels=["Response\n(k=1)", "NFW\n(k=2)"], patch_artist=True,
                medianprops={"color": "black", "linewidth": 2})
bp["boxes"][0].set_facecolor("#2196F3")
bp["boxes"][1].set_facecolor("#FF5722")
ax.set_ylabel("CV-RMSE (km/s)", fontsize=11)
ax.set_title("(d) 5-Fold Cross-Validation RMSE", fontsize=11)
ax.text(0.05, 0.95,
        f"Response: {cv_resp.mean():.1f}±{cv_resp.std():.1f}\n"
        f"NFW:      {cv_nfw.mean():.1f}±{cv_nfw.std():.1f}",
        transform=ax.transAxes, fontsize=9, va="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

# Panel (e): Upsilon_disk sensitivity
ax = axes[1, 1]
y_keys   = [str(y) for y in Y_disk_values]
med_dbic = [ydisk_bic_summary[k]["median_dbic"] for k in y_keys]
prates   = [ydisk_bic_summary[k]["pass_rate"] * 100 for k in y_keys]
ax2 = ax.twinx()
ax.bar(y_keys, med_dbic, color="#2196F3", alpha=0.7, label="Median ΔBIC")
ax2.plot(y_keys, prates, "ro-", linewidth=2, markersize=8, label="Pass Rate (%)")
ax.set_xlabel("Υ_disk (M☉/L☉)", fontsize=11)
ax.set_ylabel("Median ΔBIC vs. Baryons-Only", fontsize=11, color="#2196F3")
ax2.set_ylabel("BIC Pass Rate (%)", fontsize=11, color="red")
ax.set_title("(e) Υ_disk Marginalization Sensitivity", fontsize=11)
ax.axhline(-10, color="k", linestyle="--", linewidth=1, alpha=0.5)

# Panel (f): Summary table
ax = axes[1, 2]
ax.axis("off")
table_data = [
    ["Model", "k", "Med. ΔBIC\nvs. Bar.", "Pass\nRate", "CV-RMSE\n(km/s)"],
    ["Response", "1",
     f"{df['dbic_resp'].median():.1f}",
     f"{(df['dbic_resp']<-10).mean()*100:.0f}%",
     f"{cv_resp.mean():.1f}"],
    ["NFW", "2",
     f"{df['dbic_nfw'].median():.1f}",
     f"{(df['dbic_nfw']<-10).mean()*100:.0f}%",
     f"{cv_nfw.mean():.1f}"],
    ["Burkert", "2",
     f"{df['dbic_bur'].median():.1f}",
     f"{(df['dbic_bur']<-10).mean()*100:.0f}%",
     "N/A"],
    ["Baryons-only", "0", "0.0 (ref)", "—", "—"],
]
tbl = ax.table(cellText=table_data[1:], colLabels=table_data[0],
               loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(9)
tbl.scale(1.2, 1.8)
for j in range(5):
    tbl[0, j].set_facecolor("#1565C0")
    tbl[0, j].set_text_props(color="white", fontweight="bold")
for j in range(5):
    tbl[1, j].set_facecolor("#E3F2FD")
ax.set_title("(f) Summary Comparison Table", fontsize=11, pad=20)

plt.tight_layout()
fig_path = OUT_DIR / "bic_comparison_figure.png"
plt.savefig(fig_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Figure saved: {fig_path}")

# Additional scatter figure
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
fig2.suptitle("BIC Comparison: Response Sector vs. Standard Halo Models\n(real SPARC data)",
              fontsize=13, fontweight="bold")

for ax, xcol, xlabel, title in [
    (axes2[0], "bic_nfw",  "BIC (NFW, k=2)",    "Response vs. NFW"),
    (axes2[1], "bic_bur",  "BIC (Burkert, k=2)", "Response vs. Burkert"),
]:
    x  = df[xcol]
    y  = df["bic_resp"]
    ax.scatter(x, y, alpha=0.5, s=20, c=df["n_pts"], cmap="viridis")
    lo = min(x.min(), y.min())
    hi = max(x.max(), y.max())
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1.5, label="Equal BIC")
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("BIC (Response, k=1)", fontsize=12)
    ax.set_title(f"{title}\n(below diagonal: Response preferred)", fontsize=11)
    ax.legend()
    frac = (y < x).mean()
    ax.text(0.05, 0.95, f"Response preferred: {frac*100:.0f}%",
            transform=ax.transAxes, fontsize=10, va="top",
            bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.7))

plt.tight_layout()
scatter_path = OUT_DIR / "bic_scatter_figure.png"
plt.savefig(scatter_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Figure saved: {scatter_path}")

print("\nAnalysis complete.")
