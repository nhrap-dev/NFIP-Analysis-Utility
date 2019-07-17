def NFIP_PNNL(depth_grids, NFIP_points, out_folder):
    """ Calculates coverage and policies by flood depth
    
        Keyword arguments:
            depth_grids: list<str> -- array of file path names to the depth grid rasters
            NFIP_points: str -- Shapefile containing the NFIP points. Must contain fields: LOW_FLOOR, LOWADJ_GRA, T_COV_BLDG, T_COV_CONT, POL_NO, STATEFP and NAME
            out_folder: str -- file path name to directory for outputs
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

    if out_folder.endswith('/'):
        out_folder = out_folder[0:-1]

    t0 = time()
    print('Reading shapefile into memory')
    t1 =time()
    shp = gpd.read_file(NFIP_points)
    print(time() - t1)

    print('mosaicking rasters')
    t1 = time()
    raster_files = depth_grids

    src_files_to_mosaic = []
    for file in raster_files:
        src = rio.open(file)
        src_files_to_mosaic.append(src)

    mosaic, transformation_info = merge(src_files_to_mosaic)
    # show(mosaic, cmap='terrain')

    # Copy the metadata
    out_meta = src.meta.copy()
    out_mosiac_fp = out_folder + '/' + str(uuid.uuid1()) + '.tif'
    # Update the metadata
    out_meta.update({"driver": "GTiff",
                    "height": mosaic.shape[1],
                    "width": mosaic.shape[2],
                    "transform": transformation_info,
                    "crs": shp.crs
                    }
                    )
    with rio.open(out_mosiac_fp, "w", **out_meta) as dest:
        dest.write(mosaic)
    print(time() - t1)

    print('Reading mosiacked raster into memory')
    t1 = time()
    ras = rio.open(out_mosiac_fp)
    print(time() - t1)

    print('Mapping geometry for processing')
    t1 = time()
    geoms = list(map(lambda x: mapping(x), shp.geometry.values))
    x = list(map(lambda x: x['coordinates'][0], geoms))
    y = list(map(lambda x: x['coordinates'][1], geoms))
    print(time() - t1)

    print('Extracting depths from raster to points')
    t1 = time()
    depths = []
    for val in ras.sample(zip(x, y)):
        depths.append(val)
    print(time() - t1)

    print('Calcualting fields')
    t1 = time()
    gdf = gpd.GeoDataFrame(data=depths,geometry=shp.geometry)
    gdf.columns = ['Depth', gdf.columns[1]]
    # Calculate first floor height
    gdf['FFH'] = shp['LOW_FLOOR'] = shp['LOWADJ_GRA']
    # Handle null values
    gdf['FFH'][gdf['FFH'] > 9000] = 1
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
    print('Total elapsed time: ' + str(time() - t0))


depth_grids = [r'C:\projects\Barry\RIFT20190712rasters\RIFT20190712rasters/0808peak_flood_depthft_bin.tiff',
    r'C:\projects\Barry\RIFT20190712rasters\RIFT20190712rasters/0809peak_flood_depthft_bin.tiff']
NFIP_points = r'C:\projects\Barry/NFIP.shp'
out_folder = r'C:\projects\Barry/output'

NFIP_PNNL(depth_grids, NFIP_points, out_folder)