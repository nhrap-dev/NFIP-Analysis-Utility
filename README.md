# NFIP-PNNL-Analysis-Utility

<h3>Use cases</h3>
<h4>NFIP-PNNL-Analysis-Utility.py</h4>

* Default, use this for all NFIP-PNNL analysis.
* Slower than the NFIP-PNNL-Analysis-Mosaic-Utility.py, but resolves the affine differences between rasters.

<h4>NFIP-PNNL-Analysis-Mosaic-Utility.py</h4>

* Only use if you have multiple rasters with the affines on the same grid (their cells can be perfectly snapped together).
* Not preferable to use on a single raster
* Faster than the default tool.


<h3>Other notes</h3>
<h4>Check if you have the bigtiff driver</h4>
Note: 

* working with bigtiff files requires gdal=4+; libtiff=4+; and vs2015_runtime=14.x
* bigtiff driver works running a Python console not an IPython console

```
from osgeo import gdal
md = gdal.GetDriverByName('GTiff').GetMetadata()
md['DMD_CREATIONOPTIONLIST'].find('BigTIFF')
```