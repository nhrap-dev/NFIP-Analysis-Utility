def NFIP_PNNL(depth_grids, NFIP_points, out_folder, export_shapefile=False):
    """ Calculates coverage and policies by flood depth
    
        Keyword arguments:
            depth_grids: list<str> -- array of file path names to the depth grid GDAL compatible rasters
            NFIP_points: str -- Fiona compatible file containing the NFIP points. Must contain fields: LOW_FLOOR, LOWADJ_GRA, T_COV_BLDG, T_COV_CONT, POL_NO, STATEFP and NAME
            out_folder: str -- file path name to directory for outputs
            export_shapefile: bool -- export spatial output with depths and coverage
    """
    # imports 
    import geopandas as gpd
    import pandas as pd
    import rasterio as rio
    from rasterio.merge import merge
    # from rasterio.plot import show
    import matplotlib.pyplot as plt
    from shapely.geometry import mapping
    import numpy as np
    from time import time
    import uuid
    import os

    def consolidate_lists(array_of_lists):
        """Consolidates an array of lists sequentially

        Arguments:
            array_of_lists: list<list>

        Return:
            consolidated_lists: list 
        """
        print('Consolidating lists')
        consolidated_lists = []
        for i in range(len(array_of_lists)):
            if i == 0:
                consolidated_lists = array_of_lists[0]
            if i <= len(array_of_lists) - 1:
                new_values = [x if x >=0  else array_of_lists[i+1][index] for index, x in enumerate(consolidated_lists)]
                consolidated_lists = new_values
        return consolidated_lists

    def extract_depths(depth_grids, NFIP_gdf):
        """ Extracts depths from PNNL RIFT rasters or CERA ADCIRC coastal surge polygons to NFIP points

        Arguments:
            depth_grids: path to GDAL raster file || path to Fiona vector file
            NFIP_gdf: Point GeoDataframe

        Returns:
            sjoin: Point GeoDataframe -- adds depth column to NFIP_gdf
            ||
            depths_array: list<list> -- subsequent lists of all depth values for each raster in depth_grids for every NFIP_gdf point
        """
        if depth_grids[0].split('.')[-1] == 'shp':
            print('Extracting depths from polygons')
            # handle NFIP projection
            # TODO reproject to common
            dgPoly = gpd.read_file(depth_grids[0])
            if NFIP_gdf.crs['init'] != dgPoly.crs['init']:
                print('proceeding, but projections do not match between NFIP and CERA data')
            sjoin = gpd.sjoin(NFIP_gdf, dgPoly, how="left", op="intersects")
            return sjoin
        else:
            print('Mapping geometry for processing')
            geoms = list(map(lambda x: mapping(x), NFIP_gdf.geometry.values))
            x = list(map(lambda x: x['coordinates'][0], geoms))
            y = list(map(lambda x: x['coordinates'][1], geoms))
            xy = np.dstack((x, y))
            xys = [tuple(list(x)) for x in xy[0,:,:]]
            print('Extracting depths from rasters')
            depths_array = []
            try:
                for grid in depth_grids:
                    ras = rio.open(grid)
                    depths = []
                    for coord in xys:
                        try:
                            for val in ras.sample([coord]):
                                depths.append(float(val))
                        except:
                            depths.append(float(-1))
                    depths_array.append(depths)
            except:
                print('error extracting depths from rasters')
            print('depths extracted')
            return depths_array

    StateFipsCodes = {
        "01": "Alabama",
        "02": "Alaska",
        "04": "Arizona",
        "05": "Arkansas",
        "06": "California",
        "08": "Colorado",
        "09": "Connecticut",
        "10": "Delaware",
        "11": "District of Columbia",
        "12": "Florida",
        "13": "Geogia",
        "15": "Hawaii",
        "16": "Idaho",
        "17": "Illinois",
        "18": "Indiana",
        "19": "Iowa",
        "20": "Kansas",
        "21": "Kentucky",
        "22": "Louisiana",
        "23": "Maine",
        "24": "Maryland",
        "25": "Massachusetts",
        "26": "Michigan",
        "27": "Minnesota",
        "28": "Mississippi",
        "29": "Missouri",
        "30": "Montana",
        "31": "Nebraska",
        "32": "Nevada",
        "33": "New Hampshire",
        "34": "New Jersey",
        "35": "New Mexico",
        "36": "New York",
        "37": "North Carolina",
        "38": "North Dakota",
        "39": "Ohio",
        "40": "Oklahoma",
        "41": "Oregon",
        "42": "Pennsylvania",
        "44": "Rhode Island",
        "45": "South Carolina",
        "46": "South Dakota",
        "47": "Tennessee",
        "48": "Texas",
        "49": "Utah",
        "50": "Vermont",
        "51": "Virginia",
        "53": "Washington",
        "54": "West Virginia",
        "55": "Wisconsin",
        "56": "Wyoming"
    }

    # formats output string
    if out_folder.endswith('/'):
        out_folder = out_folder[0:-1]

    t0 = time()
    print('Reading shapefile into memory')
    t1 =time()
    shp = gpd.read_file(NFIP_points)
    print(time() - t1)

    t1 = time()
    extract = extract_depths(depth_grids, shp)
    print(time() - t1)

    
    print('Calculating fields')
    t1 = time()
    if type(extract) == list:
        t1 = time()
        print('consolidating depth lists')
        depths = consolidate_lists(extract)
        print(time() - t1)
        gdf = gpd.GeoDataFrame(data=depths,geometry=shp.geometry)
    else:
        gdf = extract[['max_ft', 'geometry']]
    gdf.columns = ['Depth', 'geometry']
    # Calculate first floor height
    gdf['FFH'] = shp['LOW_FLOOR'] - shp['LOWADJ_GRA']
    # Handle null values
    gdf['FFH'][gdf['FFH'] >= 9000] = 1
    gdf['FFH'][gdf['FFH'] < 1] = 1
    gdf['FFH'][gdf['FFH'] > 17] = 17

    # Calculate depth above first floor height
    gdf['Depth_Above_FFH'] = gdf['Depth'] - gdf['FFH']
    # Calcualte exposure
    gdf['Coverage'] = (shp['T_COV_BLDG'] + shp['T_COV_CONT']) * 100
    # Policy numbers
    gdf['Policy_Number'] = shp['POL_NO']
    # Bin depth values
    gdf['Depth_Bins'] = '0'
    # gdf['Depth_Bins'][gdf['Depth'] == 0] = '0'
    gdf['Depth_Bins'][(gdf['Depth_Above_FFH'] > 0) & (gdf['Depth_Above_FFH'] <= 1)] = '0 to 1'
    gdf['Depth_Bins'][(gdf['Depth_Above_FFH'] > 1) & (gdf['Depth_Above_FFH'] <= 3)] = '1 to 3'
    gdf['Depth_Bins'][(gdf['Depth_Above_FFH'] > 3) & (gdf['Depth_Above_FFH'] <= 6)] = '3 to 6'
    gdf['Depth_Bins'][(gdf['Depth_Above_FFH'] > 6) & (gdf['Depth_Above_FFH'] <= 9)] = '6 to 9'
    gdf['Depth_Bins'][gdf['Depth_Above_FFH'] > 9] = '> 9'
    # Sorting columns
    try:
        stateNames = ['STATEFP_1', 'STATEFP']
        for name in stateNames:
            if name in shp.columns:
                gdf['State'] = shp[name]
        gdf = gdf.replace({'State': StateFipsCodes})
    except:
        print('cant find state name')
        
    try:
        countyNames = ['NAMELSAD_1', 'NAME', 'COUNTY_NAM']
        for name in countyNames:
            if name in shp.columns:
                gdf['County'] = shp[name]
    except:
        print('cant find county name')

    # Summarize
    pivot_coverage = pd.pivot_table(gdf, values='Coverage', index=['State', 'County'], columns='Depth_Bins', aggfunc=np.sum, margins=True)
    pivot_policies = pd.pivot_table(gdf, values='Policy_Number', index=['State', 'County'], columns='Depth_Bins', aggfunc=np.count_nonzero, margins=True)
    try:
        pivot_coverage.to_excel(out_folder + '/pivot_coverage.xlsx')
        pivot_policies.to_excel(out_folder + '/pivot_policies.xlsx')
    except:
        pivot_coverage.to_csv(out_folder + '/pivot_coverage.csv')
        pivot_policies.to_csv(out_folder + '/pivot_policies.csv')
    print(time() - t1)
    if export_shapefile:
        print('Exporting spatial output')
        t1 = time()
        gdf.to_file(out_folder + '/' + "output.shp", driver='ESRI Shapefile')
        print(time() - t1)
    print('Total elapsed time: ' + str(time() - t0))

### run ###

## use if pointing to a folder of TIF files rather than a list of strings
## only change tif_folder to your folder path
# import os
# tif_folder = r'C:\projects\Barry\katrisk\bigtifs'
# dir = os.listdir(tif_folder)
# depth_grids = [tif_folder + '/' + x for x in dir if x.endswith('.tif') or x.endswith('.tiff')]

# depth_grids = [x for x in os.listdir if x.endswith('tiff')]
depth_grids = ['C:\projects\Disasters\Dorian\Data\CERA/maxelevProj_0903.shp']
NFIP_points = r'C:\projects\Disasters\Dorian\Data\NFIP\Dorian_NFIP_CERA_elevs_09012019/Dorian_NFIP_CERA_elevs_09012019.shp'
out_folder = r'C:\projects\Disasters\Dorian\outputs\NFIP_20190903'

NFIP_PNNL(depth_grids, NFIP_points, out_folder, export_shapefile=False)


# TODO
"""
get working
add gui
add CERA (ADCIRC)
add katrisk
"""
