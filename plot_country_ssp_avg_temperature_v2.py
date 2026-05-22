#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 17:14:06 2026

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
import sys
from sklearn.metrics import mean_squared_error
import geopandas as gpd 

############################ MODIFY ###############################################################################
syymmdd = '20050101'
eyymmdd = '20071231'

smm = int(syymmdd[4:6])
sdd = int(syymmdd[6:8])
syy = int(syymmdd[0:4])

emm = int(eyymmdd[4:6])
edd = int(eyymmdd[6:8])
eyy = int(eyymmdd[0:4])

startYear = datetime(syy, smm, sdd, 0, 0, 0) #datetime(2013, 12, 31, 0, 0, 0)
endYear = datetime(eyy, emm, edd, 23, 0, 0)

country = 'CH'

eval_wrf_country = []
dnt = []
start = startYear
firstStart = startYear
init = True
initFile = ''
firstFile = True
while start < endYear:
    
    # check in range
    f1 = '20050101-20091231'
    f2 = '20100101-20141231'

    smmf1 = int(f1[4:6])
    sddf1 = int(f1[6:8])
    syyf1 = int(f1[0:4])

    emmf1 = int(f1[13:15])
    eddf1 = int(f1[15:17])
    eyyf1 = int(f1[9:13])
    
    startYearF1 = datetime(int(f1[0:4]), int(f1[4:6]), int(f1[6:8]), 0, 0, 0)
    endYearF1 = datetime(int(f1[9:13]), int(f1[13:15]), int(f1[15:17]), 23, 0, 0)
    
    startYearF2 = datetime(int(f2[0:4]), int(f2[4:6]), int(f2[6:8]), 0, 0, 0)
    endYearF2 = datetime(int(f2[9:13]), int(f1[13:15]), int(f2[15:17]), 23, 0, 0)
        
    if startYearF1 <= start <= endYearF1:
        filename = f'tasmax_day_GFDL-CM4_historical_r1i1p1f1_gr1_{f1}_10km.nc'
        startYear = startYearF1
    elif startYearF2 <= start <= endYearF2:
        filename = f'tasmax_day_GFDL-CM4_historical_r1i1p1f1_gr1_{f2}_10km.nc'
        startYear = startYearF2
    if initFile != filename:
        init = True
        initFile = filename
    
    temp_type = filename.split('_')[0]
    ssp = filename.split('_')[3]
    dateRange = filename.split('_')[6]
    resolution = filename.split('_')[7].split('.')[0]
    
    wrfDir = '/home/khanh/Documents/biasCorrection/gaussianFilter/'
    
    # preload matched location between model and obs
    # if not, model generates new one. Just provide a name
    preMatch = f'/home/khanh/Documents/biasCorrection/gaussianFilter/station_id_{resolution}.csv'
    
    iyymmdd = dateRange.split('-')[0]
    
    imm = int(iyymmdd[0:4])
    idd = int(iyymmdd[4:6])
    iyy = int(iyymmdd[6:8])
    
    modInitYear = datetime(imm, idd, iyy, 0, 0, 0)
    
    # number of days to run after startYear
    lengthDays = (endYear - startYear).days
    ################# MODIFY ##########################################################################################
    
    # import obs data
    if temp_type == 'tasmax':
        varT = 'MAX'
    elif temp_type == 'tas':
        varT = 'TEMP'
    elif temp_type == 'tasmin':
        varT = 'MIN'
        
    # ds_in_cm4 = nc.Dataset(f'{wrfDir}/{temp_type}_day_GFDL-CM4_historical_r1i1p1f1_gr1_20100101-20141231_{resolution}.nc')
    ds_in_cm4 = nc.Dataset(f'{wrfDir}/{filename}')
    
    # calculate the day. days start from 1850-01-01
    modTime = np.ma.filled(ds_in_cm4['time'])
    delYear, delDay = divmod(modTime, 365)
            
    # exclude leap year. all years have 365 days
    modDate = []
    leapCount = 0
    i = 0
    nYear = len(delYear)
    while i < nYear:
        dt = modInitYear + tdelta.timedelta(days=i)
        leapYear = calendar.isleap(dt.year)
        if dt.month != 2 or dt.day != 29 or not leapYear:
            modDate.append(modInitYear + tdelta.timedelta(days=i))
        else:
            leapCount += 1
            nYear += 1
        i += 1
    
    # load pre match rows cols to obs lat and lon
    if os.path.isfile(preMatch):
        df = pd.read_csv(preMatch, dtype={'station': str})
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
    
    locName = []
    for j in range(0, len(preload_name)):
        locName.append(preload_name[j].split(' ')[-1])
    pre_ind_tmp = np.where(np.array(locName) == country)
    
    if init == True and firstFile == True:
        init_d = np.where(np.array(modDate) == firstStart)[0][0]
        init = False
        firstFile = False
    elif init == True:
        init_d = np.where(np.array(modDate) == startYear)[0][0]
        init = False
    # start = modDate[init_d]
    end_d = np.where(np.array(modDate) == startYear)[0][0]+lengthDays-nYear
    
    # import cmip6 data
    wrftmp = np.mean(ds_in_cm4[temp_type][init_d:init_d+365,:,:], axis=0)
    if len(pre_ind_tmp) != 0:
        # print('station found')
        pre_ind = pre_ind_tmp[0]
        row = (preload_rows[pre_ind])
        col = (preload_cols[pre_ind])
        
        eval_lat = preload_lat[pre_ind]
        eval_lon = preload_lon[pre_ind]
        eval_wrf = wrftmp[row, col]
        eval_station = preload_station[pre_ind]
        eval_name = preload_name[pre_ind]
        wrfDailyAtObs = wrftmp[row, col]
    
    eval_wrf_country.append(np.mean(wrftmp[row, col]))  
    dnt.append(start)
    
    init_d += 365
    leapYear = calendar.isleap(start.year)
    if not leapYear:
        start = start + tdelta.timedelta(days = 365)
    else:
        start = start + tdelta.timedelta(days = 366)

country_name = ['a', 'b', 'c']
dnt = [2010, 2011, 2012]
eval_wrf_country = [290, 291, 292]
c = 0
with open('test.csv', 'a') as f:
    if c == 0:
        f.write(',')
        for i in range(0, len(dnt)):
            f.write(str(dnt[i]) + ',')
        f.write('\n')
        f.write(country_name[c])
        for i in range(0, len(dnt)):
            f.write(str(eval_wrf_country[i]) + ',')
        f.write('\n')
            
plt.plot(dnt, eval_wrf_country, label='test')
plt.subplots_adjust(bottom=0.2, top=.94)
plt.legend(
        loc='lower center',         # Anchor the top center of the legend box
        bbox_to_anchor=(0.5, -0.2), # at the (0.5, -0.15) coordinates
        ncol=7,                     # Use two columns for a horizontal legend
        # fancybox=True,              # Optional: adds a rounded box
        # shadow=True,                 # Optional: adds a shadow
        fontsize=11
            )