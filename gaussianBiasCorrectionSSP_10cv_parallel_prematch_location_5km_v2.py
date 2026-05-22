#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  5 09:13:22 2026

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
import os.path

############################ MODIFY ###############################################################################
# paths
ssp = 'historical'
resolution = '5km'
temp_type = 'tasmax'

metDataDir = '/anvil/scratch/x-kdo/downscale/obs/'
dsoutDir = f'/anvil/scratch/x-kdo/downscale/model_outputs/10FoldCV/{resolution}/'
wrfDir = f'/anvil/scratch/x-kdo/downscale/cmip6/interp/{ssp}/{resolution}/'

# preload matched location between model and obs
# if not, model generates new one. Just provide a name
preMatch = f'station_id_{resolution}.csv'

max_dis = 1
modInitYear = datetime(2010, 1, 1, 0, 0, 0)
startYear = datetime(2010, 1, 1, 0, 0, 0)
# number of days to run after startYear
lengthDays = 365*5

months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
factors = [0.992, 0.99, 0.99, 0.99, 0.992, 0.992, 0.992, 0.992, 0.99, 0.99, 0.99, 0.99]
################# MODIFY ##########################################################################################

# import obs data
if temp_type == 'tasmax':
    varT = 'MAX'
elif temp_type == 'tas':
    varT = 'TEMP'
elif temp_type == 'tasmin':
    varT = 'MIN'
    
ds_in_cm4 = nc.Dataset(f'{wrfDir}/{temp_type}_day_GFDL-CM4_historical_r1i1p1f1_gr1_20100101-20141231_{resolution}.nc')
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
        x = lon[i]
        y = lat[i]

        idx_min = np.sum((xy-[x, y])**2, axis=1, keepdims=True).argmin(axis=0)
        # closest_points1 = xy[idx_min]
        y_ind = idx_min%xlong.shape[1]
        x_ind = np.int32(np.floor(idx_min/xlong.shape[1]))
        dis = np.min(np.sqrt(np.sum((xy-[x, y])**2, axis=1, keepdims=True)))


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

def conv2D(filtered_o3MapRatio, tMapRatio,train_ind, rows, cols, n1, n2):
    for i in range(0, n1):
        filtered_o3MapRatio = cv2.filter2D(src=filtered_o3MapRatio, ddepth=-1, kernel=kernel)
        # n_1 = copy.deepcopy(filtered_o3MapRatio)
    
        filtered_o3MapRatio[np.array(rows)[train_ind].ravel(), np.array(cols)[train_ind].ravel()] = (tMapRatio[np.array(rows)[train_ind].ravel(), np.array(cols)[train_ind].ravel()])
    
        # n = copy.deepcopy(filtered_o3MapRatio)
        # print(np.sum(n_1-n))
    
    for i in range(0, n2):
        filtered_o3MapRatio = cv2.filter2D(src=filtered_o3MapRatio, ddepth=-1, kernel=kernel)
    
    return filtered_o3MapRatio

newYear = True
currentYear = modInitYear.year
# for d in range(np.where(np.array(modDate) == startYear)[0][0], len(modDate)):
for d in range(np.where(np.array(modDate) == startYear)[0][0], np.where(np.array(modDate) == startYear)[0][0]+lengthDays):
    print(modDate[d]) 
    # import cmip6 data
    wrftmp = np.ma.filled(ds_in_cm4['tasmax'][d,:,:])
    
    start = modDate[d]
    end = modDate[d] + tdelta.timedelta(hours=23)
    
    # check if the previous year is the same
    if currentYear != modDate[d].year:
        currentYear = modDate[d].year
        newYear = True
    
    # import obs data
    if newYear == True:
        df = pd.read_csv(f'{metDataDir}/meteorology_daily_summaries_{str(modDate[d].year)}.csv', index_col=False, low_memory=False)
        station_tmp = np.array(df['STATION'])
        dat_tmp = np.array(df['DATE'])
        lat_tmp = np.array(df['LATITUDE'])
        lon_tmp = np.array(df['LONGITUDE'])
        tmpObs_tmp = np.array(df[varT])
        stationName_tmp = np.array(df['NAME'])
        newYear = False

    day_select_ind = np.where(dat_tmp == str(modDate[d]).split(' ')[0])[0]
    valid_ind = np.delete(day_select_ind, np.where(tmpObs_tmp[day_select_ind] == 9999.9)[0])
    tmpObs = tmpObs_tmp[valid_ind]
    
    station = station_tmp[valid_ind]
    dat = dat_tmp[valid_ind]
    lat = lat_tmp[valid_ind]
    lon = lon_tmp[valid_ind]%360
    tmpObs = (tmpObs_tmp[valid_ind]-32)*(5/9) + 273.15 # convert Farenheit to Celcius
    stationName = stationName_tmp[valid_ind]

    # generate 3d map with ones
    tMapRatio = np.ones((wrftmp.shape[0], wrftmp.shape[1]))

    # load pre match rows cols to obs lat and lon
    if os.path.isfile(preMatch):
        df = pd.read_csv(preMatch)
        preload_station = np.array(df['station'])
        preload_rows = df['rows']
        preload_cols = df['cols']
        preload_lat = df['lat']
        preload_lon = df['lon']
        preload_name = df['name']
        newFile = False
    else:
        preload_station = np.array([])
        preload_rows = np.array([])
        preload_cols = np.array([])
        preload_lat = np.array([])
        preload_lon = np.array([])
        preload_name = np.array([])
        newFile = True
        
    # compare model and obs using parallel python
    i = np.linspace(0, len(tmpObs)-1, len(tmpObs), dtype='int')
    
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
        with open(preMatch, 'a') as f:
            if newFile == True:
                f.write('station' + ',' + 'name' + ',' + 'rows' + ',' + 'cols' + ',' + 'lat' + ',' + 'lon' + '\n')
            for i in range(0, len(newStation)):
                newStation_ind = np.where(eval_station == newStation[i])[0][0]
                f.write(str(eval_station[newStation_ind]) + ',' + str(eval_name[newStation_ind]).replace(',', '-') + ',' + str(rows[newStation_ind]) + ',' + 
                        str(cols[newStation_ind]) + ',' + str(eval_lat[newStation_ind]) + ',' + str(eval_lon[newStation_ind]) + '\n')             
                
    # 10 fold cross validation
    def random_array(seed, size, min_val, max_val):
        random.seed(seed)
        return random.sample(range(min_val, max_val + 1), size)

    randInd = random_array(seed=42, size=len(rows), min_val=0, max_val=len(rows)-1)

    # seed_value = 42
    # rng = np.random.default_rng(seed=seed_value)
    # randInd = rng.integers(low=0, high=len(dnt), size=(1, len(dnt)))[0]
    ind = np.linspace(0, len(rows)-1, len(rows), dtype='int')
    cvs = 10
    for cv in range(0, cvs):
        # re-initialize the map
        tMapRatio[rows, cols] = value
        
        start_test_set = cv*round(len(rows)/cvs)
        end_test_set = (cv+1)*round(len(rows)/cvs)

        test_ind = randInd[start_test_set: end_test_set]
        train_ind = np.delete(ind, np.sort(test_ind))


        print(len(test_ind) + len(train_ind))
        print(f'start_test_set: {(start_test_set)}')
        print(f'end_test_set: {(end_test_set)}')

        wrfDaily = wrftmp[:,:]
        value = np.float32(value)
        value[value > 2] = 2
        meanRatio = np.mean(value)
        tMapRatio[tMapRatio > 2] = 2
        filtered_o3MapRatio = tMapRatio
        filtered_o3MapRatio[np.array(rows)[test_ind].ravel(), np.array(cols)[test_ind].ravel()] = 1 # set test = 1

        kernel = np.array([[ 1,  4,  7,  4,  1],
                           [ 4, 16, 26, 16,  4],
                           [ 7, 26, 41, 26,  7],
                           [ 4, 16, 26, 16,  4],
                           [ 1,  4,  7,  4,  1]])*(1/273)

        #kernel = np.array([[1,  6,  15,  20,  15, 6, 1],
        #                   [6, 36, 90, 120,  90, 36, 6],
        #                   [15, 90, 225, 300, 225, 90, 15],
        #                   [20, 120, 300, 400,  300, 120, 20],
        #                   [15, 90, 225, 300, 225, 90, 15],
        #                   [6, 36, 90, 120,  90, 36, 6],
        #                   [1,  6,  15,  20,  15, 6, 1]])*(1/4096)

        # apply conv2D
        filtered_o3MapRatio = conv2D(filtered_o3MapRatio, tMapRatio,train_ind, rows, cols, 1500, 1)
            
        # row, col = np.where(tMapRatio == 1)
        # filtered_o3MapRatio[row, col] = filtered_o3MapRatio[row, col]*meanRatio
        
        # reduce overprediction
        # filtered_o3MapRatio = filtered_o3MapRatio*factors[modDate[d].month-1]
        
        # reapply conv2D
        # filtered_o3MapRatio = conv2D(filtered_o3MapRatio, tMapRatio,train_ind, rows, cols, 10, 1)
                
        # extract 10% test data and write to csv
        test_rows = rows[test_ind]
        test_cols = cols[test_ind]
        test_lat = eval_lat[test_ind]
        test_lon = eval_lon[test_ind]
        test_obs = eval_obs[test_ind]
        test_wrf = eval_wrf[test_ind]
        test_station = eval_station[test_ind]
        test_name = eval_name[test_ind]
        test_corrected = (filtered_o3MapRatio*wrfDaily)[np.array(rows)[test_ind].ravel(), np.array(cols)[test_ind].ravel()]
        
        corr_matrix = np.corrcoef(test_corrected, test_obs)
        corr = corr_matrix[0, 1]
        r2 = corr**2
        mb = np.mean(test_corrected-test_obs)
        print(f'cv_{cv} - R: {str(corr)[0:4]} - MB: {str(mb)[0:4]}')
        
        # # extract 90% train data and write to csv
        # test_rows = rows[train_ind]
        # test_cols = cols[train_ind]
        # test_lat = eval_lat[train_ind]
        # test_lon = eval_lon[train_ind]
        # test_obs = eval_obs[train_ind]
        # test_wrf = eval_wrf[train_ind]
        # test_corrected = (filtered_o3MapRatio*wrfDaily)[np.array(rows)[train_ind].ravel(), np.array(cols)[train_ind].ravel()]
        
        # corr_matrix = np.corrcoef(test_corrected, test_obs)
        # corr = corr_matrix[0, 1]
        # r2 = corr**2
        # mb = np.mean(test_corrected-test_obs)
        # print(f'cv_{cv} - R: {str(corr)[0:4]} - MB: {str(mb)[0:4]}')
        
        with open(f'{dsoutDir}{temp_type}_{str(modDate[d]).split(" ")[0]}.csv', 'a') as f:
            f.write('station_id' + ',' + 'name' + ',' + 'rows' + ',' + 'cols' + ',' + 'lat' + ',' + 'lon' + ',' + 'obs' + ',' + 'corrected' + ',' + 'wrf' + '\n')
            for i in range(0, len(test_rows)):
                f.write(str(test_station[i]) + ',' + str(test_name[i]).replace(',', '-') + ',' + str(test_rows[i]) + ',' + str(test_cols[i]) + ',' + str(test_lat[i]) + ',' + str(test_lon[i]) + ',' + str(test_obs[i]) + ',' + 
                        str(test_corrected[i]) + ',' + str(test_wrf[i]) + '\n') 
