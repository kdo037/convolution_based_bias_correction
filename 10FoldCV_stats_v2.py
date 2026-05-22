#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 17:04:45 2026

@author: khanh
"""
# this script combine the daily 10fold CV to monthly and yearly stats
# example file name tas_1990-01-01.csv, from 1990 to 2014

import pandas as pd
from netCDF4 import Dataset as nc
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
import multiprocessing as mp
from multiprocessing import Pool

def compute_r(mod, obs):
    r = sum((mod-np.mean(mod))*(obs-np.mean(obs)))/(sum((mod-np.mean(mod))**2)*sum((obs-np.mean(obs))**2))**0.5
    r2 = r**2
    return r, r2
def compute_mb(mod, obs):
    mb = np.mean(mod-obs)
    return mb
def compute_rmse(mod, obs):
    mse = mean_squared_error(mod, obs)
    rmse = np.sqrt(mse)
    return mse, rmse

a = datetime.now()

################ CHANGE DATE AND TIME ####################################################
inputDir = '/home/khanh/Documents/biasCorrection/gaussianFilter/'
# example file name tas_1990-01-01.csv
temp_type = 'tas'
resolution = '10km'
# Define desired date range
start = datetime(1990,1,8,0,0,0)  # start date
end = datetime(2014,9,15,0,0,0) # end date
################ CHANGE DATE AND TIME ####################################################

dnt = []
lat = []
lon = []
obs = []
cor = []
mod = []
stationID = []
locationName = []

filename = f'{temp_type}_{resolution}.csv'
df = pd.read_csv(f'{inputDir}{filename}', low_memory=False)
stationID = np.array(df['station_id'])
locationName = np.array(df['name'])
lat = np.array(df['lat'])
lon = np.array(df['lon'])
obs = np.array(df['obs'])
cor = np.array(df['corrected'])
mod = np.array(df['wrf'])
dnt = np.array(df['time'])

print('Done reading files.')

# remove string element
ind = np.where(lat == 'lat')
if len(ind) > 0:
    ind = ind[0]
    dnt = np.delete(dnt, ind)
    lat = np.delete(lat, ind)
    lon = np.delete(lon, ind)
    obs = np.delete(obs, ind)
    cor = np.delete(cor, ind)
    mod = np.delete(mod, ind)
    stationID = np.delete(stationID, ind)
    locationName = np.delete(locationName, ind)

# split the month
months = []
for i in range(0, len(dnt)):
    months.append(int(dnt[i].split('-')[1]))

monthIndex = [[] for x in range(0, 12)]
for i in range(0, 12):
    monthIndex[i].append(np.where(np.array(months) == i+1))

r = [[] for x in range(0, 12)] 
r2 = [[] for x in range(0, 12)]
mb = [[] for x in range(0, 12)]
mse = [[] for x in range(0, 12)]
rmse = [[] for x in range(0, 12)]
lat_array = [[] for x in range(0, 12)]
lat_array = [[] for x in range(0, 12)]
locationName_array = [[] for x in range(0, 12)]
stationID_array = [[] for x in range(0, 12)]
dnt_array = [[] for x in range(0, 12)]

#compute the monthly average
for i in range(0, 12): # 12 months
    monthObs = np.float64(obs[monthIndex[i]][0][0])
    monthCor = np.float64(cor[monthIndex[i]][0][0])
    monthMod = np.float64(mod[monthIndex[i]][0][0])
    dnt_array = dnt[monthIndex[i]][0][0]
    
    r_tmp, r2_tmp = compute_r(monthCor, monthObs)
    mb_tmp = compute_mb(monthCor, monthObs)
    mse_tmp, rmse_tmp = compute_rmse(monthCor, monthObs)
    
    r[i].append(r_tmp)
    r2[i].append(r2_tmp)
    mb[i].append(mb_tmp)
    mse[i].append(mse_tmp)
    rmse[i].append(rmse_tmp)

print('Done computing the monthly average.')

# compute yearly
startYear = int(dnt[0].split('-')[0])
endYear = int(dnt[-1].split('-')[0])
numYear = endYear - startYear + 1

# split the year
years = []
for i in range(0, len(dnt)):
    years.append(int(dnt[i].split('-')[0]))

yearIndex = [[] for x in range(0, numYear)]
for i in range(startYear, endYear+1):
    yearIndex[i-startYear].append(np.where(np.array(years) == i))
    
r_yearly = [[] for x in range(0, numYear)] 
r2_yearly = [[] for x in range(0, numYear)]
mb_yearly = [[] for x in range(0, numYear)]
mse_yearly = [[] for x in range(0, numYear)]
rmse_yearly = [[] for x in range(0, numYear)]
lat_yearly = [[] for x in range(0, numYear)]
lat_yearly = [[] for x in range(0, numYear)]
locationName_yearly = [[] for x in range(0, numYear)]
stationID_yearly = [[] for x in range(0, numYear)]
dnt_yearly = [[] for x in range(0, numYear)]
    
for i in range(0, numYear):
    yearObs = np.float64(obs[yearIndex[i]][0][0])
    yearCor = np.float64(cor[yearIndex[i]][0][0])
    yearMod = np.float64(mod[yearIndex[i]][0][0])
    yearDnt = dnt[yearIndex[i]][0][0]
    
    r_tmp, r2_tmp = compute_r(yearCor, yearObs)
    mb_tmp = compute_mb(yearCor, yearObs)
    mse_tmp, rmse_tmp = compute_rmse(yearCor, yearObs)
    
    r_yearly[i].append(r_tmp)
    r2_yearly[i].append(r2_tmp)
    mb_yearly[i].append(mb_tmp)
    mse_yearly[i].append(mse_tmp)
    rmse_yearly[i].append(rmse_tmp)
    dnt_yearly[i].append(startYear+i)

print('Done computing the yearly average.')

# compute stat for each location
uniqueLocation = np.unique(locationName)
def compute_locationStats(i):
    locIndex = np.where(locationName == uniqueLocation[i])[0]
    if len(locIndex) > 10:
        locBasedObs = np.float32(np.array(obs[locIndex]))
        locBasedCor = np.float32(cor[locIndex])
        locBasedMod = np.float32(mod[locIndex])
        locLat = np.float32(np.array(lat[locIndex]))
        locLon = np.float32(np.array(lon[locIndex]))
        locName = np.array(locationName[locIndex])
        locID = np.array(locationName[locIndex])
        locBasedDnt = dnt[locIndex]
        # bias corrected stats with obs
        r_cor, r2_cor = compute_r(locBasedCor, locBasedObs)
        mb_cor = compute_mb(locBasedCor, locBasedObs)
        mse_cor, rmse_cor = compute_rmse(locBasedCor, locBasedObs)
        # ssp stats with obs
        r_ssp, r2_ssp = compute_r(locBasedMod, locBasedObs)
        mb_ssp = compute_mb(locBasedMod, locBasedObs)
        mse_ssp, rmse_ssp = compute_rmse(locBasedMod, locBasedObs)
        
        return locID[0], locName[0], locLat[0], locLon[0], r_cor, r2_cor, mb_cor, mse_cor, rmse_cor, r_ssp, r2_ssp, mb_ssp, mse_ssp, rmse_ssp
    else:
        return -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999
    
# i = np.linspace(0, (len(uniqueLocation))-1, (len(uniqueLocation)), dtype='int')
i = np.linspace(0, 100-1, 100, dtype='int')
max_cpus = 12
with Pool(processes=max_cpus) as pool:
    values = pool.map(compute_locationStats, i)

values = np.array(values)

b = datetime.now()   
print('Time spent: ', b - a)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    