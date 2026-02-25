# HEASARC download manifest: MACS J0416.1-2403
Resolved target: ra=64.034917 deg, dec=-24.072444 deg
Search radius: 12.00 arcmin
## chanmaster

- Chandra observation log
- Rows: 5
| index | id | access_url | aws | sciserver | bytes |
|---:|---|---|---|---|---:|
| 0 | ivo://nasa.heasarc/chanmaster?8106 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/6//16236/ | s3://nasa-heasarc/chandra/data/byobsid/6/16236/ | /FTP/chandra/data/byobsid/6/16236/ | 171312992 |
| 1 | ivo://nasa.heasarc/chanmaster?8107 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/7//16237/ | s3://nasa-heasarc/chandra/data/byobsid/7/16237/ | /FTP/chandra/data/byobsid/7/16237/ | 139326329 |
| 2 | ivo://nasa.heasarc/chanmaster?8108 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/3//16523/ | s3://nasa-heasarc/chandra/data/byobsid/3/16523/ | /FTP/chandra/data/byobsid/3/16523/ | 308230947 |
| 3 | ivo://nasa.heasarc/chanmaster?8109 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/3//17313/ | s3://nasa-heasarc/chandra/data/byobsid/3/17313/ | /FTP/chandra/data/byobsid/3/17313/ | 268871441 |
| 4 | ivo://nasa.heasarc/chanmaster?8111 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/4//16304/ | s3://nasa-heasarc/chandra/data/byobsid/4/16304/ | /FTP/chandra/data/byobsid/4/16304/ | 400254723 |

**Suggested download approaches**

- If you have AWS CLI configured: `aws s3 sync <aws_path> <local_dir>`
- If you have wget (Git-Bash/WSL): `wget -r -np -nH --cut-dirs=3 <access_url>`
  (Adjust `--cut-dirs` depending on the URL depth.)


## xmmmaster

- XMM-Newton observation log
- Rows: 0

