#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 10:11:22 2026

@author: khanh
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 14:54:19 2026

@author: khanh
"""

import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import time
#from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
#from sklearn.linear_model import LinearRegression
import pandas as pd
import csv
import netCDF4 as nc
import math
from math import radians, cos, sin, asin, sqrt
import datetime as tdelta
import cv2
import copy
import calendar
import multiprocessing as mp
from multiprocessing import Pool
import random

############################ MODIFY ###############################################################################
# paths
metDataDir = '/home/khanh/Documents/biasCorrection/'
dsoutDir = '/home/khanh/Documents/biasCorrection/gaussianFilter/'
wrfDir = '/home/khanh/Documents/biasCorrection/'
temp_type = 'tasmax'
max_dis = 1
modInitYear = datetime(2010, 1, 1, 0, 0, 0)
startYear = datetime(2014, 6, 1, 0, 0, 0)
################# MODIFY ##########################################################################################

ds_in_cm4 = nc.Dataset(f'{wrfDir}/gaussianFilter/cm4_10km_{temp_type}.nc')
# import data to variables
lon_cm4 = np.ma.filled(ds_in_cm4['lon'])
lat_cm4 = np.ma.filled(ds_in_cm4['lat'])

lon2d, lat2d = np.meshgrid(lon_cm4, lat_cm4)
lat1d = np.reshape(lat2d, (1, np.shape(lat2d)[0]*np.shape(lat2d)[1]))[0]
lon1d = np.reshape(lon2d, (1, np.shape(lon2d)[0]*np.shape(lon2d)[1]))[0]

xlong = lon2d
xlat = lat2d

xy = np.stack([lon1d, lat1d])
xy = np.transpose(xy)

# calculate the day. days start from 1850-01-01
modTime = np.ma.filled(ds_in_cm4['time'])
delYear, delDay = divmod(modTime, 365)

# exclude leap year. all years have 365 days
modDate = []
leapCount = 1
for i in range(0, len(delYear)):
    dt = modInitYear + tdelta.timedelta(days=i)
    leapYear = calendar.isleap(dt.year)
    if dt.month != 2 or dt.day != 29 or not leapYear:
        modDate.append(modInitYear + tdelta.timedelta(days=i))
    else:
        modDate.append(modInitYear + tdelta.timedelta(days=i + leapCount))
        leapCount += 1

# import obs data
if temp_type == 'tasmax':
    loc = 20
elif temp_type == 'tas':
    loc = 6
elif temp_type == 'tasmin':
    loc = 22
        
for d in range(np.where(np.array(modDate) == startYear)[0][0], len(modDate)):
    
    # import cmip6 data
    wrftmp = np.ma.filled(ds_in_cm4['tasmax'][d,:,:])
    
    start = modDate[d]
    end = modDate[d] + tdelta.timedelta(hours=23)
        
    with open(metDataDir + f'/gaussianFilter/meteorology_daily_{str(modDate[d].year)}.csv', 'r', encoding = 'utf-8', errors = 'ignore') as readFile:
        reader = csv.reader(readFile)
        lines = list(reader)

    station = []
    lat = []
    lon = []
    lon_org = []
    tmpObs = []
    station = []
    dat = []
    tim = []
    dnt = []
    lat_org = []
    stationName = []
    # for i in range(1, len(lines)):
    for i in range(1, len(lines)):
        if float(lines[i][loc].split(',')[0]) != 9999.9:
            timeTmp = datetime.strptime(lines[i][1], '%Y-%m-%d')
            if timeTmp == modDate[d]:
                station.append(lines[i][0])
                dat.append(lines[i][1])
                dnt.append(datetime.strptime(lines[i][1], '%Y-%m-%d'))
                lat.append(float(lines[i][2]))
                lat_org.append(float(lines[i][2]))
                lon.append(float(lines[i][3])%360)
                lon_org.append(float(lines[i][3]))
                tmpObs.append((float(lines[i][loc])-32)*(5/9) + 273.15) # convert Farenheit to Celcius
                stationName.append(lines[i][5])
            
    # initial search for closest grid cell
    x = lon[1]
    y = lat[1]

    idx_min = np.sum((xy-[x, y])**2, axis=1, keepdims=True).argmin(axis=0)
    closest_points = xy[idx_min]
    y_ind = idx_min%xlong.shape[1]
    x_ind = np.int16(np.floor(idx_min/xlong.shape[1]))
    dis = np.min(np.sqrt(np.sum((xy-[x, y])**2, axis=1, keepdims=True)))

    # generate 3d map with ones
    tMapRatio = np.ones((wrftmp.shape[0], wrftmp.shape[1]))

    # load pre match rows cols to obs lat and lon
    df = pd.read_csv('station_id.csv')
    preload_station = np.array(df['station'])
    preload_rows = df['rows']
    preload_cols = df['cols']
    preload_lat = df['lat']
    preload_lon = df['lon']
    preload_name = df['name']
    
    om_ratio = []

    row = []
    col = []
    value = []
    eval_lat = []
    eval_lon = []
    eval_obs = []
    eval_station = []
    eval_name = []
    def compute_ratio(i):
        # check if station ID already recorded
        pre_ind_tmp = np.where(preload_station == station[i])[0]
        if len(pre_ind_tmp) != 0:
            pre_ind = pre_ind_tmp[0]
            row = (preload_rows[pre_ind])
            col = (preload_cols[pre_ind])
            
            eval_lat = preload_lat[pre_ind]
            eval_lon = preload_lon[pre_ind]
            eval_obs = tmpObs[i]
            eval_wrf = wrftmp[row, col]
            eval_station = preload_station[pre_ind]
            eval_name = preload_name[pre_ind]
            
            obsTmp = tmpObs[i]
            wrfDailyAtObs = wrftmp[row, col]
            ratio = obsTmp/wrfDailyAtObs
            value = (ratio)
            return row, col, value, eval_lat, eval_lon, eval_obs, eval_wrf, eval_station, eval_name
        
        else: # search for grid
            # find k index that closest to the
            x = lon[i]
            y = lat[i]
            # xy = np.stack([wrfLon1d, wrfLat1d], axis=1)
    
            idx_min = np.sum((xy-[x, y])**2, axis=1, keepdims=True).argmin(axis=0)
            # closest_points1 = xy[idx_min]
            y_ind = idx_min%xlong.shape[1]
            x_ind = np.int32(np.floor(idx_min/xlong.shape[1]))
            dis = np.min(np.sqrt(np.sum((xy-[x, y])**2, axis=1, keepdims=True)))
    
            # wrf_k = np.mean(wrftmp[:, x_ind, y_ind])
    
            if dis < max_dis:
                # dis = np.min(np.sqrt(np.sum((xy-[x, y])**2, axis=1, keepdims=True)))
                # idx_sort = np.argsort(np.sum((xy-[x, y])**2, axis=1, keepdims=True).ravel())
    
                # # obtain the daily temperature from the closet observations from knn
                obsTmp = tmpObs[i]
                # dntTmp = dnt[i]
    
                # obtain the WRF daily temperature from the obs location
                wrfDailyAtObs = wrftmp[x_ind, y_ind]
    
                # ratio
                ratio = obsTmp/wrfDailyAtObs
                om_ratio.append(ratio)
    
                # assign ratio to o3 map
                tMapRatio[x_ind, y_ind] = ratio
                
                row = (x_ind[0])
                col = (y_ind[0])
                value = (ratio[0])
                eval_lat = lat[i]
                eval_lon = lon[i]
                eval_obs = tmpObs[i]
                eval_wrf = wrftmp[x_ind, y_ind][0]
                eval_station = station[i]
                eval_name = stationName[i]
                print('station not found')
                return row, col, value, eval_lat, eval_lon, eval_obs, eval_wrf, eval_station, eval_name

    i = np.linspace(0, len(dnt)-1, len(dnt), dtype='int')
    
    max_cpus = 64
    # i = np.linspace(0, 5000, 5001, dtype='int')
    with Pool(processes=max_cpus) as pool:
        values = pool.map(compute_ratio, i)
    
    count = 0
    for i in range(0, len(values)):
        if values[i - count] == None:
            values.pop(i - count)
            count += 1
        
    values = np.array(values)
    rows = np.int16(values[:,0])
    cols = np.int16(values[:,1])
    value = values[:,2]
    eval_lat = values[:,3]
    eval_lon = values[:,4]
    eval_obs = np.float32(values[:,5])
    eval_wrf = np.float32(values[:,6])
    eval_station = values[:,7]
    eval_name = values[:,8]
    
    # check if is there any not found station and update station id file
    newStation = list(set(eval_station) - set(preload_station))
    if len(newStation) != 0:
        with open('station_id.csv', 'a') as f:
            # f.write('station' + ',' + 'name' + ',' + 'rows' + ',' + 'cols' + ',' + 'lat' + ',' + 'lon' + '\n')
            for i in range(0, len(newStation)):
                newStation_ind = np.where(eval_station == newStation[i])[0][0]
                f.write(str(eval_station[newStation_ind]) + ',' + str(eval_name[newStation_ind]).replace(',', '-') + ',' + str(rows[newStation_ind]) + ',' + 
                        str(cols[newStation_ind]) + ',' + str(eval_lat[newStation_ind]) + ',' + str(eval_lon[newStation_ind]) + '\n')        
    
    # with open('station_id.csv', 'w') as f:
    #     f.write('station' + ',' + 'name' + ',' + 'rows' + ',' + 'cols' + ',' + 'lat' + ',' + 'lon' + '\n')
    #     for i in range(0, len(eval_station)):
    #         f.write(str(eval_station[i]) + ',' + str(eval_name[i]).replace(',', '-') + ',' + str(rows[i]) + ',' + str(cols[i]) + ',' + str(eval_lat[i]) + ',' + str(eval_lon[i]) + '\n')   
    
    # tMapRatio = np.array(tMapRatio)
    tMapRatio[rows, cols] = value

    wrfDaily = wrftmp[:,:]
    value = np.float32(value)
    value[value > 2] = 2
    meanRatio = np.mean(value)
    tMapRatio[tMapRatio > 2] = 2
    filtered_o3MapRatio = tMapRatio

    kernel = np.array([[ 1,  4,  7,  4,  1],
                       [ 4, 16, 26, 16,  4],
                       [ 7, 26, 41, 26,  7],
                       [ 4, 16, 26, 16,  4],
                       [ 1,  4,  7,  4,  1]])*(1/273)

    for i in range(0, 1000):
        filtered_o3MapRatio = cv2.filter2D(src=filtered_o3MapRatio, ddepth=-1, kernel=kernel)
        n_1 = copy.deepcopy(filtered_o3MapRatio)

        filtered_o3MapRatio[rows, cols] = tMapRatio[np.array(rows), np.array(cols)]

        n = copy.deepcopy(filtered_o3MapRatio)
        # print(np.sum(n_1-n))

    for i in range(0, 10):
        filtered_o3MapRatio = cv2.filter2D(src=filtered_o3MapRatio, ddepth=-1, kernel=kernel)
        n_1 = copy.deepcopy(filtered_o3MapRatio)
        
    row, col = np.where(tMapRatio == 1)
    filtered_o3MapRatio[row, col] = filtered_o3MapRatio[row, col]*meanRatio
    
    # reduce overprediction
    filtered_o3MapRatio = filtered_o3MapRatio*0.987
    
    for i in range(0, 10):
        filtered_o3MapRatio = cv2.filter2D(src=filtered_o3MapRatio, ddepth=-1, kernel=kernel)
        filtered_o3MapRatio[rows, cols] = tMapRatio[np.array(rows), np.array(cols)]
        
    for i in range(0, 1):
        filtered_o3MapRatio = cv2.filter2D(src=filtered_o3MapRatio, ddepth=-1, kernel=kernel)
    
    # eval
    test_rows = rows
    test_cols = cols
    test_lat = eval_lat
    test_lon = eval_lon
    test_obs = eval_obs
    test_wrf = eval_wrf
    test_station = eval_station
    test_name = eval_name
    test_corrected = (filtered_o3MapRatio*wrfDaily)[np.array(rows).ravel(), np.array(cols).ravel()]
        
    corr_matrix = np.corrcoef(test_corrected, test_obs)
    corr = corr_matrix[0, 1]
    r2 = corr**2
    mb = np.mean(test_corrected-test_obs)
    print(f'{modDate[d]} - R: {str(corr)[0:4]} - MB: {str(mb)[0:4]}')
        
    # write daily
    ds_in = ds_in_cm4
    # create ds_out
    file = f'{temp_type}_10km_hist_{str(modDate[d]).split(" ")[0]}'
    ds_out = nc.Dataset(dsoutDir + file + '.nc', "w")
    # create dimensions
    _ = ds_out.createDimension('Time', 1)
    _ = ds_out.createDimension('lon', ds_in.dimensions['lon'].size)
    _ = ds_out.createDimension('lat', ds_in.dimensions['lat'].size)

    # create variable
    v_out = ds_out.createVariable(
        'tasmax_corrected',
        np.float32,
        ("Time", "lat", "lon"),
        zlib=True,
        complevel=1,
    )
    # Note: `zlib=True` is deprecated in favor of `compression='zlib'`
    # Note: complevel=4 is default, 0--9 with 9 most compression
    v_in = ds_in.variables[temp_type]
    v_out.units = v_in.units.strip()
    v_out[:] = 0

    v_out[:] = filtered_o3MapRatio*wrfDaily
    v_out.units = v_in.units
    v_out.coordinates = v_in.coordinates

    # create variable
    v_out = ds_out.createVariable(
        temp_type,
        np.float32,
        ("Time", "lat", "lon"),
        zlib=True,
        complevel=1,
    )
    # Note: `zlib=True` is deprecated in favor of `compression='zlib'`
    # Note: complevel=4 is default, 0--9 with 9 most compression
    v_in = ds_in.variables[temp_type]
    v_out.units = v_in.units.strip()
    v_out[:] = 0

    v_out[:] = wrfDaily
    v_out.units = v_in.units
    v_out.coordinates = v_in.coordinates

    ds_out.close()
    
    # write calculated ratio filtered_o3MapRatio
    # if init == True:
    ds_in_ratio = ds_in_cm4
    # create ds_out
    file = f'{temp_type}_10km_hist_ratio_{str(modDate[d]).split(" ")[0]}'
    ds_out = nc.Dataset(dsoutDir + file + '.nc', "r+")
    # create dimensions
    _ = ds_out.createDimension('Time', 1)
    _ = ds_out.createDimension('lon', ds_in_ratio.dimensions['lon'].size)
    _ = ds_out.createDimension('lat', ds_in_ratio.dimensions['lat'].size)

    # create variable
    v_out = ds_out.createVariable(
        f'{temp_type}_ratio',
        np.float32,
        ("Time", "lat", "lon"),
        zlib=True,
        complevel=1,
    )
    
    v_in = ds_in_ratio.variables[temp_type]
    v_out.units = v_in.units.strip()
    v_out[:] = 0

    v_out[:,:] = filtered_o3MapRatio
    v_out.units = v_in.units
    v_out.coordinates = v_in.coordinates
    ds_out.close()
        
    # else:
    #     ds_in_ratio = ds_in_cm4
    #     file = f'{temp_type}_10km_hist_ratio'
    #     ds_out = nc.Dataset(dsoutDir + file + '.nc', "r+")
    #     v_in = ds_in_ratio.variables[temp_type]
    #     v_out.units = v_in.units.strip()
    #     v_out[:] = 0

    #     v_out[count_ratio,:,:] = filtered_o3MapRatio
    #     v_out.units = v_in.units
    #     v_out.coordinates = v_in.coordinates
    #     ds_out.close()
    #     count_ratio += 1
    