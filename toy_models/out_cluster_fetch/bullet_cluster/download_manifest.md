# HEASARC download manifest: 1E 0657-56
Resolved target: ra=104.612000 deg, dec=-55.972500 deg
Search radius: 12.00 arcmin
## chanmaster

- Chandra observation log
- Rows: 10
| index | id | access_url | aws | sciserver | bytes |
|---:|---|---|---|---|---:|
| 0 | ivo://nasa.heasarc/chanmaster?2487 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/4//554/ | s3://nasa-heasarc/chandra/data/byobsid/4/554/ | /FTP/chandra/data/byobsid/4/554/ | 138024287 |
| 1 | ivo://nasa.heasarc/chanmaster?2488 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/4//4984/ | s3://nasa-heasarc/chandra/data/byobsid/4/4984/ | /FTP/chandra/data/byobsid/4/4984/ | 364780909 |
| 2 | ivo://nasa.heasarc/chanmaster?2489 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/5//4985/ | s3://nasa-heasarc/chandra/data/byobsid/5/4985/ | /FTP/chandra/data/byobsid/5/4985/ | 136272345 |
| 3 | ivo://nasa.heasarc/chanmaster?2490 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/6//4986/ | s3://nasa-heasarc/chandra/data/byobsid/6/4986/ | /FTP/chandra/data/byobsid/6/4986/ | 201758818 |
| 4 | ivo://nasa.heasarc/chanmaster?2491 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/5//5355/ | s3://nasa-heasarc/chandra/data/byobsid/5/5355/ | /FTP/chandra/data/byobsid/5/5355/ | 135634906 |
| 5 | ivo://nasa.heasarc/chanmaster?2492 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/6//5356/ | s3://nasa-heasarc/chandra/data/byobsid/6/5356/ | /FTP/chandra/data/byobsid/6/5356/ | 457380667 |
| 6 | ivo://nasa.heasarc/chanmaster?2493 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/7//5357/ | s3://nasa-heasarc/chandra/data/byobsid/7/5357/ | /FTP/chandra/data/byobsid/7/5357/ | 379493986 |
| 7 | ivo://nasa.heasarc/chanmaster?2494 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/8//5358/ | s3://nasa-heasarc/chandra/data/byobsid/8/5358/ | /FTP/chandra/data/byobsid/8/5358/ | 155691356 |
| 8 | ivo://nasa.heasarc/chanmaster?2495 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/1//5361/ | s3://nasa-heasarc/chandra/data/byobsid/1/5361/ | /FTP/chandra/data/byobsid/1/5361/ | 389487295 |
| 9 | ivo://nasa.heasarc/chanmaster?2496 | https://heasarc.gsfc.nasa.gov/FTP/chandra/data/byobsid/4//3184/ | s3://nasa-heasarc/chandra/data/byobsid/4/3184/ | /FTP/chandra/data/byobsid/4/3184/ | 392443058 |

**Suggested download approaches**

- If you have AWS CLI configured: `aws s3 sync <aws_path> <local_dir>`
- If you have wget (Git-Bash/WSL): `wget -r -np -nH --cut-dirs=3 <access_url>`
  (Adjust `--cut-dirs` depending on the URL depth.)


## xmmmaster

- XMM-Newton observation log
- Rows: 1
| index | id | access_url | aws | sciserver | bytes |
|---:|---|---|---|---|---:|
| 0 | ivo://nasa.heasarc/xmmmaster?2108 | https://heasarc.gsfc.nasa.gov/FTP/xmm/data/rev0//0112980201/ | s3://nasa-heasarc/xmm/data/rev0/0112980201/ | /FTP/xmm/data/rev0/0112980201/ | 597299883 |

**Suggested download approaches**

- If you have AWS CLI configured: `aws s3 sync <aws_path> <local_dir>`
- If you have wget (Git-Bash/WSL): `wget -r -np -nH --cut-dirs=3 <access_url>`
  (Adjust `--cut-dirs` depending on the URL depth.)


