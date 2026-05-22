#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:56:41 2026

@author: khanh
"""

# this script combines daily historical nc to 1 file

import pandas as pd
import netCDF4 as nc
import numpy as np
from datetime import datetime
from datetime import timedelta
import time
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pandas as pd
import csv
import datetime as tdelta
import calendar
from sklearn.metrics import mean_squared_error


################ CHANGE DATE AND TIME ####################################################
inputDir = '/home/khanh/Downloads/'
# example file name tas_1990-01-01.csv
temp_type = 'tas'
resolution = '10km'
# Define desired date range
start = datetime(1990,1,1,0,0,0)  # start date
end = datetime(1990,1,2,0,0,0) # end date
################ CHANGE DATE AND TIME ####################################################

dnt = []
monthIndex = [[] for x in range(0, 12)]
count = 0
lat = []
lon = []
obs = []
cor = []
mod = []
stationID = []
locationName = []

init = True
while start <= end:
    leapYear = calendar.isleap(start.year)
    if start.month != 2 or start.day != 29 or not leapYear:
        filename = f'{temp_type}_{resolution}_hist_{start.year}-{str(start.month).zfill(2)}-{str(start.day).zfill(2)}.nc'
        ds = nc.Dataset(f'{inputDir}/{filename}')
        tas = ds['tasmax_corrected']
    else:
        print(start)

    
    # write calculated ratio filtered_o3MapRatio
    ds_in_ratio = ds
    # create ds_out
    file = 'test'
    ds_out = nc.Dataset(inputDir + file + '.nc', "a")
    
    if init == True:
        # create dimensions
        _ = ds_out.createDimension('Time', None)
        _ = ds_out.createDimension('lon', ds_in_ratio.dimensions['lon'].size)
        _ = ds_out.createDimension('lat', ds_in_ratio.dimensions['lat'].size)
        
        # create variable
        v_out = ds_out.createVariable(
            f'{temp_type}',
            np.float32,
            ("Time", "lat", "lon"),
            zlib=True,
            complevel=1,
        )
        
        v_in = ds_in_ratio.variables[temp_type]
        v_out.units = v_in.units.strip()
        v_out.units = v_in.units
        
        v_out = ds_out.createVariable(
            'Times',
            str,
            ("Time"),
            zlib=True,
            complevel=1,
        )
        
        v_out = ds_out.createVariable(
            'lon',
            np.float32,
            ("lon"),
            zlib=True,
            complevel=1,
        )
        
        v_out = ds_out.createVariable(
            'lat',
            np.float32,
            ("lat"),
            zlib=True,
            complevel=1,
        )
        
        # v_out[count,:,:] = tas[0,:,:]
        temp = ds_out.variables[f'{temp_type}']
        times = ds_out.variables['Times']
        temp[count,:,:] = tas[0,:,:]
        times[count] = str(start)
        init = False
    else:
        temp[count,:,:] = tas[0,:,:]
        times[count] = str(start)
    
    count += 1
    
    start = start + tdelta.timedelta(days = 1)
    print(start)
   
# write lat and lon
filename = f'tasmax_day_GFDL-CM4_historical_r1i1p1f1_gr1_20050101-20091231_{resolution}.nc'
ds_coordinate = nc.Dataset(f'/home/khanh/Documents/biasCorrection/gaussianFilter/{filename}')
lat = ds_out.variables['lat']
lat[:] =  ds_coordinate['lat'][:]
lon = ds_out.variables['lon']
lon[:] = ds_coordinate['lon'][:]

ds_out.close()

