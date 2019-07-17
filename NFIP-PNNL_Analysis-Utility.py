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
        print('Consolidating lists')
        consolidated_lists = []
        for i in range(len(array_of_lists)-1):
            if i == 0:
                consolidated_lists = array_of_lists[0]
            if i <= len(array_of_lists) - 2:
                new_values = [x if x >=0  else array_of_lists[i+1][index] for index, x in enumerate(consolidated_lists)]
                consolidated_lists = new_values
        return consolidated_lists

    def extract_depths(list_of_rasters, point_geodataframe):
        print('Mapping geometry for processing')
        geoms = list(map(lambda x: mapping(x), point_geodataframe.geometry.values))
        x = list(map(lambda x: x['coordinates'][0], geoms))
        y = list(map(lambda x: x['coordinates'][1], geoms))
        print('Extracting depths from rasters')
        depths_array = []
        for grid in list_of_rasters:
            ras = rio.open(grid)
            depths = []
            for val in ras.sample(zip(x, y)):
                depths.append(float(val))
            depths_array.append(depths)
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
    depths_array = extract_depths(depth_grids, shp)
    print(time() - t1)


    t1 = time()
    depths = consolidate_lists(depths_array)
    print(time() - t1)
    
    print('Calculating fields')
    t1 = time()
    gdf = gpd.GeoDataFrame(data=depths,geometry=shp.geometry)
    gdf.columns = ['Depth', gdf.columns[1]]
    # Calculate first floor height
    gdf['FFH'] = shp['LOW_FLOOR'] = shp['LOWADJ_GRA']
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
    gdf['Depth_Bins'][(gdf['Depth'] > 0) & (gdf['Depth'] <= 1)] = '0 to 1'
    gdf['Depth_Bins'][(gdf['Depth'] > 1) & (gdf['Depth'] <= 3)] = '1 to 3'
    gdf['Depth_Bins'][(gdf['Depth'] > 3) & (gdf['Depth'] <= 6)] = '3 to 6'
    gdf['Depth_Bins'][(gdf['Depth'] > 6) & (gdf['Depth'] <= 9)] = '6 to 9'
    gdf['Depth_Bins'][gdf['Depth'] > 9] = 'greater than 9'
    # Sorting columns
    try:
        gdf['State'] = shp['STATEFP_1']
    except:
        gdf['State'] = shp['STATEFP']
    gdf = gdf.replace({'State': StateFipsCodes})
    try: 
        gdf['County'] = shp['NAMELSAD_1']
    except:
        gdf['County'] = shp['NAME']

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
    # print('Cleaning')
    # t1 = time()
    # os.remove(out_mosiac_fp) #unable to bc of file lock
    # print(time() - t1)
    if export_shapefile:
        print('Exporting spatial output')
        t1 = time()
        gdf.to_file(out_folder + '/' + "output.shp", driver='ESRI Shapefile')
        print(t1 - time())
    print('Total elapsed time: ' + str(time() - t0))


depth_grids = [r'C:\projects\Barry\07142019\RIFT20190714rasters/0808peak_flood_depthft_bin.tiff',
    r'C:\projects\Barry\07142019\RIFT20190714rasters/0809peak_flood_depthft_bin.tiff']
NFIP_points = r'C:\projects\Barry/NFIP.shp'
out_folder = r'C:\projects\Barry/07142019/new_outputs'

NFIP_PNNL(depth_grids, NFIP_points, out_folder, True)