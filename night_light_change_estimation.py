
import ee
import geemap
import os
import pandas as pd
import numpy as np
try:
        ee.Initialize()
except Exception as e:
        ee.Authenticate()
        ee.Initialize()
dmsp= ee.ImageCollection('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS')\
                        .select('stable_lights')

## filtering to the annual images using the satalite+year combination                        
dmsp_10 = ee.Image("NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182010")

dmsp_20 =  ee.Image("NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F142000")

## caliberating using the given formula

dmsp10_calib = dmsp_10.expression('2.3430 + (0.5102*X)+ (0.0065*X*X)',\
     {'X':dmsp_10.select('stable_lights')})

dmsp10_calib = dmsp10_calib\
    .where(dmsp10_calib.gt(63),63)\
        .where(dmsp10_calib.lte(6),0)

dmsp20_calib = dmsp_20.expression('1.0988 + (1.3155*X)+ (-0.0053*X*X)',\
     {'X':dmsp_20.select('stable_lights')})

dmsp20_calib = dmsp20_calib\
    .where(dmsp20_calib.gt(63),63)\
        .where(dmsp20_calib.lte(6),0)



avg_nl = []
district_list = []
taluk_list = []
in_dir = os.path.join(os.path.expanduser('~'), 'work/internships/anusthub/shapefiles/tehsil_all')
path = './shapefiles/tehsil_all/'
for root, dirs, files in os.walk(path):
    for file in files:
        filename, extension = os.path.splitext(file)
        if extension == '.shp':
            filename = os.path.join(in_dir, file)
            taluk_ee= geemap.shp_to_ee(f'{filename}')
            years = [dmsp20_calib,dmsp10_calib]
            for year in years:
                arr = geemap.ee_to_numpy(year, region = taluk_ee)
                avg = arr.flatten().mean( )
                avg_nl.append(avg)

                #file names

                file_split = (file.split('.', 1)[0])
                district = file_split.split('_')[0]
                district_list.append(district)
                taluk = (file_split.split('_')[1])
                taluk_list.append(taluk)
                print(str(taluk) + " finished")

df =  pd.DataFrame({'year':[2000,2010]*int(len(taluk_list)/2),
                   'district': district_list,
                   'taluk':taluk_list,
                   'avg_nl':avg_nl})
df_wide = df.pivot( index = ['district','taluk'],columns ='year', values = ['avg_nl'])\
    .reset_index().droplevel(0, axis=1)
df_wide.columns= ['district', 'taluk', 'avg_nl_2000', 'avg_nl_2010']

df_wide.to_csv('./tehsil_all_nl_avg.csv')