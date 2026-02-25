# HEASARC download manifest: Abell 2744
Resolved target: ra=3.583458 deg, dec=-30.388278 deg
Search radius: 12.00 arcmin
## chanmaster

- Chandra observation log
- Rows: 5
| index | id | access_url | aws | sciserver | bytes |
|---:|---|---|---|---|---:|
| 0 | ivo://nasa.heasarc/chanmaster?5776 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/7//25907/ | s3://nasa-heasarc/chandra/data/byobsid/7/25907/ | /FTP/chandra/data/byobsid/7/25907/ | 147099469 |
| 1 | ivo://nasa.heasarc/chanmaster?5786 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/7//25917/ | s3://nasa-heasarc/chandra/data/byobsid/7/25917/ | /FTP/chandra/data/byobsid/7/25917/ | 133015636 |
| 2 | ivo://nasa.heasarc/chanmaster?5791 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/2//25922/ | s3://nasa-heasarc/chandra/data/byobsid/2/25922/ | /FTP/chandra/data/byobsid/2/25922/ | 137708445 |
| 3 | ivo://nasa.heasarc/chanmaster?5795 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/6//25926/ | s3://nasa-heasarc/chandra/data/byobsid/6/25926/ | /FTP/chandra/data/byobsid/6/25926/ | 220102435 |
| 4 | ivo://nasa.heasarc/chanmaster?5824 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/5//25955/ | s3://nasa-heasarc/chandra/data/byobsid/5/25955/ | /FTP/chandra/data/byobsid/5/25955/ | 168386430 |

**Suggested download approaches**

- If you have AWS CLI configured: `aws s3 sync <aws_path> <local_dir>`
- If you have wget (Git-Bash/WSL): `wget -r -np -nH --cut-dirs=3 <access_url>`
  (Adjust `--cut-dirs` depending on the URL depth.)


## xmmmaster

- XMM-Newton observation log
- Rows: 0

