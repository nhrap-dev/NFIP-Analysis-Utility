# NFIP-Analysis-Utility

This script takes NFIP policy points and analyzes coverage and counts of inland flooding and coastal surge.

<h3>Requirements</h3>

- Must have Python 3.X installed
- Must have all the Python packages installed listed in the requirements.txt
- It requires NFIP policy points with the following valid fields: LOW_FLOOR, LOWADJ_GRA, T_COV_BLDG, T_COV_CONT, POL_NO
- The tool can take any GDAL supported raster file as a depth grid or a Fiona supported polygon file.

<h3>Setup</h3>

- Install all Python packages in requirements.txt. Double click on setup.py.
  - This must be a Python 3.X environment. If setup.py doesn't work, you can open a terminal in the tool directory, you can run `pip install -r requirements.txt`.

<h3>To Use</h3>

- Project all data to the same projected coordinate system.
- Double click on NFIP-Analysis-Tool.pyw to run.
  - Alternatly, in a terminal, run `python NFIP-Analysis-Tool.pyw` in the repository directory

<h3>Caveats</h3>

- Projection: The CERA ADCIRC data is distributed in GCS WGS84 (EPSG 4326), whereas the NFIP data is distributed PCS NAD83 (EPSG 4269). The script does not (yet) handle projections. The projections do change the numbers slightly.
- Elevation: The CERA ADCIRC data are generally distributed with elevations at mean sea level (MSL), but are sometimes distributed with elevations relative to NAVD88. The NFIP elevations are relative to USGS NED 10m. The script does not (yet) handle differences between MSL, NAVD88, and NED. These do provide differences in the results and must be corrected prior to running.

<h3>Other notes</h3>
<h4>Katrisk support: Check if you have the bigtiff driver</h4>
Note:

- working with bigtiff files requires gdal=4+; libtiff=4+; and vs2015_runtime=14.x
- bigtiff driver works running a Python console not an IPython console

```
from osgeo import gdal
md = gdal.GetDriverByName('GTiff').GetMetadata()
md['DMD_CREATIONOPTIONLIST'].find('BigTIFF')
```
