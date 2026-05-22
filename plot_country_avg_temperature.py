#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 13:40:52 2026

@author: khanh
"""

# this script plot the month average temperature for SSP for different countries
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

filename = f'{temp_type}_{resolution}_test.csv'
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

# # split by country code name
# countryName = []
# for j in range(0, len(locationName)):
#     countryName.append(locationName[j].split(' ')[-1])
# country_ind = np.where(np.array(countryName) == 'CH')
    
#compute the monthly average
monthObs = []
monthCor = []
monthMod = []
monthLat = []
monthLon = []
monthLocName = []
monthStationID = []
dnt_array = []
for i in range(0, 12): # 12 months
    # split based on the name
    monthLocName_tmp = locationName[monthIndex[i]][0][0]
    locName = []
    for j in range(0, len(monthLocName_tmp)):
        locName.append(monthLocName_tmp[j].split(' ')[-1])
    country_ind = np.where(np.array(locName) == 'CH')

    monthObs.append(np.float64(obs[monthIndex[i]][0][0])[country_ind[0]])
    monthCor.append(np.float64(cor[monthIndex[i]][0][0])[country_ind[0]])
    monthMod.append(np.float64(mod[monthIndex[i]][0][0])[country_ind[0]])
    monthLat.append(np.float64(lat[monthIndex[i]][0][0])[country_ind[0]])
    monthLon.append(np.float64(lon[monthIndex[i]][0][0])[country_ind[0]])
    monthLocName.append(locationName[monthIndex[i]][0][0][country_ind[0]])
    monthStationID.append(stationID[monthIndex[i]][0][0][country_ind[0]])
    dnt_array.append(dnt[monthIndex[i]][0][0][country_ind[0]])

# compute the monthly average
monthObs_avg = []
monthCor_avg = []
monthMod_avg = []

for i in range(0, 12): # 12 months
    monthObs_avg.append(np.mean(monthObs[i]))
    monthCor_avg.append(np.mean(monthCor[i]))
    monthMod_avg.append(np.mean(monthMod[i]))

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
plt.plot(months, monthObs_avg)
plt.plot(months, monthCor_avg)
plt.plot(months, monthMod_avg)
