#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 14:45:03 2026

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

filename = 'tasmax_day_GFDL-CM4_historical_r1i1p1f1_gr1_20100101-20141231_10km.nc'

temp_type = filename.split('_')[0]
ssp = filename.split('_')[3]
dateRange = filename.split('_')[6]
resolution = filename.split('_')[7].split('.')[0]

wrfDir = '/home/khanh/Documents/biasCorrection/gaussianFilter/'

# preload matched location between model and obs
# if not, model generates new one. Just provide a name
preMatch = f'/home/khanh/Documents/biasCorrection/gaussianFilter/station_id_{resolution}.csv'

max_dis = 1

iyymmdd = dateRange.split('-')[0]
syymmdd = '20100101'
eyymmdd = '20141231'

imm = int(iyymmdd[0:4])
idd = int(iyymmdd[4:6])
iyy = int(iyymmdd[6:8])

smm = int(syymmdd[4:6])
sdd = int(syymmdd[6:8])
syy = int(syymmdd[0:4])

emm = int(eyymmdd[4:6])
edd = int(eyymmdd[6:8])
eyy = int(eyymmdd[0:4])

modInitYear = datetime(imm, idd, iyy, 0, 0, 0)
startYear = datetime(syy, smm, sdd, 0, 0, 0) #datetime(2013, 12, 31, 0, 0, 0)
endYear = datetime(eyy, emm, edd, 23, 0, 0)

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
pre_ind_tmp = np.where(np.array(locName) == 'CH')
        
eval_wrf_country = []
dnt = []

init_d = np.where(np.array(modDate) == startYear)[0][0]
start = modDate[init_d]
end_d = np.where(np.array(modDate) == startYear)[0][0]+lengthDays-nYear
while start <= modDate[end_d - 364]:
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
    
plt.plot(dnt, eval_wrf_country)
