# NFIP-Analysis-Utility

This script takes NFIP policy points and analyzes coverage and counts of inland flooding and coastal surge.

It requires NFIP policy points with the following valid fields:
LOW_FLOOR, LOWADJ_GRA, T_COV_BLDG, T_COV_CONT, POL_NO

It can use a GDAL supported raster file as a depth grid or a Fiona supported polygon file.

<h3>Use</h3>

* Install all libraries in NFIP-Analysis-Utility.py
* run ```python __main__.py```

<h3>Caveats</h3>

* Projection: The CERA ADCIRC data is distributed in GCS WGS84 (EPSG 4326), whereas the NFIP data is distributed PCS NAD83 (EPSG 4269). The script does not (yet) handle projections. The projections do change the numbers slightly.
* Elevation: The CERA ADCIRC data are generally distributed with elevations at mean sea level (MSL), but are sometimes distributed with elevations relative to NAVD88. The NFIP elevations are relative to USGS NED 10m. The script does not (yet) handle differences between MSL, NAVD88, and NED. These do provide differences in the results and must be corrected prior to running.


<h3>Other notes</h3>
<h4>Katrisk support: Check if you have the bigtiff driver</h4>
Note: 

* working with bigtiff files requires gdal=4+; libtiff=4+; and vs2015_runtime=14.x
* bigtiff driver works running a Python console not an IPython console

```
from osgeo import gdal
md = gdal.GetDriverByName('GTiff').GetMetadata()
md['DMD_CREATIONOPTIONLIST'].find('BigTIFF')
```
