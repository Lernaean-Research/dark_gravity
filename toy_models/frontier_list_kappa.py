"""List available Frontier Fields kappa FITS URLs for a given HFF cluster.

This is a lightweight HTML-index scraper for the STScI HLSP directory listings:
  https://archive.stsci.edu/missions/hlsp/frontier/<cluster>/models/

It:
- enumerates team directories
- enumerates version subdirectories (e.g., v4.1)
- picks the highest version it can parse per team
- finds the *_kappa.fits file in that version directory

Outputs one JSON object per line (NDJSON) for easy piping/selection.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin


try:
    import requests  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("This script requires 'requests' (pip install requests)") from e


_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


def _fetch(url: str) -> str:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def _list_dirs(index_html: str) -> list[str]:
    hrefs = _HREF_RE.findall(index_html)
    out: list[str] = []
    for h in hrefs:
        if h in ("../", "./"):
            continue
        if h.endswith("/") and not h.startswith("?") and not h.startswith("#"):
            out.append(h)
    return sorted(set(out))


def _list_files(index_html: str) -> list[str]:
    hrefs = _HREF_RE.findall(index_html)
    out: list[str] = []
    for h in hrefs:
        if h in ("../", "./"):
            continue
        if not h.endswith("/") and not h.startswith("?") and not h.startswith("#"):
            out.append(h)
    return sorted(set(out))


def _parse_version(name: str) -> tuple[int, ...] | None:
    # Accept v4, v4.1, v4.1.2
    m = re.match(r"^v(\d+(?:\.\d+)*)/?$", name.strip(), flags=re.IGNORECASE)
    if not m:
        return None
    parts = tuple(int(p) for p in m.group(1).split("."))
    return parts


def _pick_best_version(dirs: Iterable[str]) -> str | None:
    best: tuple[tuple[int, ...], str] | None = None
    for d in dirs:
        v = _parse_version(d)
        if v is None:
            continue
        cand = (v, d)
        if best is None or cand[0] > best[0]:
            best = cand
    return None if best is None else best[1]


@dataclass(frozen=True)
class KappaEntry:
    cluster: str
    team: str
    version_dir: str
    kappa_url: str
    readme_url: str | None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cluster", required=True, help="HFF cluster directory name (e.g., macs0416, abell2744)")
    args = ap.parse_args()

    base = f"https://archive.stsci.edu/missions/hlsp/frontier/{args.cluster}/models/"
    root_html = _fetch(base)
    team_dirs = [d.rstrip("/") for d in _list_dirs(root_html)]

    entries: list[KappaEntry] = []

    for team in team_dirs:
        team_url = urljoin(base, team + "/")
        try:
            team_html = _fetch(team_url)
        except Exception:
            continue

        vers_dirs = _list_dirs(team_html)
        best = _pick_best_version(vers_dirs)
        if best is None:
            # Some teams might store files directly under team/.
            best_url = team_url
            best_dir = ""
            files_html = team_html
        else:
            best_url = urljoin(team_url, best)
            best_dir = best.rstrip("/")
            try:
                files_html = _fetch(best_url)
            except Exception:
                continue

        files = _list_files(files_html)
        kappa = next((f for f in files if f.lower().endswith("_kappa.fits")), None)
        if not kappa:
            continue

        readme = next((f for f in files if "readme" in f.lower() and f.lower().endswith(".txt")), None)
        entries.append(
            KappaEntry(
                cluster=args.cluster,
                team=team,
                version_dir=best_dir,
                kappa_url=urljoin(best_url, kappa),
                readme_url=None if readme is None else urljoin(best_url, readme),
            )
        )

    for e in sorted(entries, key=lambda x: (x.team.lower(), x.version_dir)):
        print(json.dumps(e.__dict__, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
