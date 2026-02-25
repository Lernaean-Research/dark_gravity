"""Quick FITS WCS/header inspector.

Examples
--------
./.venv/Scripts/python.exe toy_models/inspect_fits_wcs.py \
  toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/best_fit_maps/bulletclu-kappa-best-50mas.fits \
  toy_models/data/bullet_cluster/external_lensing/canucs_rihtarsic_2026/best_fit_model/xray_kappa_dsdls1.fits
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args()

    from astropy.io import fits
    from astropy.wcs import WCS
    from astropy.wcs.utils import proj_plane_pixel_scales

    for p in args.paths:
        p = p.resolve()
        print(f"\n== {p}")
        if not p.exists():
            print("MISSING")
            continue
        with fits.open(p) as hdul:
            h = hdul[0].header
            d = hdul[0].data
            w = WCS(h)
            print("shape", getattr(d, "shape", None), "dtype", getattr(d, "dtype", None))
            print("BUNIT", h.get("BUNIT"))
            print("CTYPE", h.get("CTYPE1"), h.get("CTYPE2"))
            print("CRVAL", h.get("CRVAL1"), h.get("CRVAL2"))
            print("CRPIX", h.get("CRPIX1"), h.get("CRPIX2"))
            print("CDELT", h.get("CDELT1"), h.get("CDELT2"))
            try:
                sc = proj_plane_pixel_scales(w)  # degrees/pixel
                print("pixel_scales_arcsec", [float(s * 3600) for s in sc])
            except Exception as e:
                print("pixel scale failed", type(e).__name__, str(e))

            # Minimal WCS sanity.
            try:
                ra_dec = w.pixel_to_world(0, 0)
                print("pixel(0,0)->world", getattr(ra_dec, "ra", ra_dec)[0] if hasattr(ra_dec, "ra") else ra_dec)
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
