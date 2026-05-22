#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 12:25:15 2026

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

################ CHANGE DATE AND TIME ####################################################
inputDir = '/home/khanh/Documents/biasCorrection/gaussianFilter/10FoldCV/10km/tasmin/'
# example file name tas_1990-01-01.csv
temp_type = 'tasmin'
# Define desired date range
start = datetime(2014,1,1,0,0,0)  # start date
end = datetime(2014,12,31,0,0,0) # end date
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

# while start <= end:
#     leapYear = calendar.isleap(start.year)
#     if start.month != 2 or start.day != 29 or not leapYear:
#         filename = f'{temp_type}_{start.year}-{str(start.month).zfill(2)}-{str(start.day).zfill(2)}.csv'
#         df = pd.read_csv(f'{inputDir}{filename}')
#         stationID.append((np.array(df['station_id'])))
#         locationName.append((np.array(df['name'])))
#         lat.append((np.array(df['lat'])))
#         lon.append((np.array(df['lon'])))
#         obs.append((np.array(df['obs'])))
#         cor.append((np.array(df['corrected'])))
#         mod.append((np.array(df['wrf'])))
#         dnt.append(start)
#         monthIndex[start.month-1].append(count)
#         count += 1
#     else:
#         print(start)
#     start = start + tdelta.timedelta(days = 1)

while start <= end:
    leapYear = calendar.isleap(start.year)
    if start.month != 2 or start.day != 29 or not leapYear:
        filename = f'{temp_type}_{start.year}-{str(start.month).zfill(2)}-{str(start.day).zfill(2)}.csv'
        with open(f'{inputDir}{filename}', 'r', encoding = 'utf-8', errors = 'ignore') as readFile:
            reader = csv.reader(readFile)
            lines = list(reader)
        for i in range(1, len(lines)):
            stationID.append(lines[i][0])
            locationName.append(lines[i][1])
            lat.append(lines[i][4])
            lon.append(lines[i][5])
            obs.append(lines[i][6])
            cor.append(lines[i][7])
            mod.append(lines[i][8])
            dnt.append(start)
            monthIndex[start.month-1].append(count)
            count += 1
    else:
        print(start)
    start = start + tdelta.timedelta(days = 1)
    print(start)
r = [[] for x in range(0, 12)] 
r2 = [[] for x in range(0, 12)]
mb = [[] for x in range(0, 12)]
rmse = [[] for x in range(0, 12)]
lat_array = [[] for x in range(0, 12)]
lat_array = [[] for x in range(0, 12)]
locationName_array = [[] for x in range(0, 12)]
stationID_array = [[] for x in range(0, 12)]
# compute the monthly average
# for i in range(0, 12): # 12 months
#     obs

cor = np.float32(cor)
mod = np.float32(mod)
obs = np.float32(obs)

plt.ecdf(np.float32(cor), color='red')
plt.ecdf(np.float32(mod))
plt.ecdf(np.float32(obs))
plt.legend(['cor', 'mod', 'obs'])


cor[cor < 230] = 0
mod[mod < 230] = 0
obs[obs < 230] = 0

maxi = np.max(cor), np.max(mod), np.max(obs)
cor[cor > np.min(maxi)] = 0
mod[mod > np.min(maxi)] = 0
obs[obs > np.min(maxi)] = 0

cor = np.delete(cor, np.where(cor == 0))
mod = np.delete(mod, np.where(mod == 0))
obs = np.delete(obs, np.where(obs == 0))

maxi = np.max(cor), np.max(mod), np.max(obs)
cor[cor == np.max(cor)] = np.max(maxi)
mod[mod == np.max(mod)] = np.max(maxi)
obs[obs == np.max(obs)] = np.max(maxi)

fig, a1 = plt.subplots(figsize=(8, 6))
plt.title('Daily MIN Distribution in 2014')
cnt, b_mod = np.histogram(mod, bins=30)
p_mod = cnt / cnt.sum()
c_mod = np.cumsum(p_mod)
a1.bar(b_mod[:-1], p_mod, width=2.5, color='green', alpha=0.8)

cnt, b_cor = np.histogram(cor, bins=30)
p_cor = cnt / cnt.sum()
c_cor = np.cumsum(p_cor)
a1.bar(b_cor[:-1], p_cor, width=1.5, color='red', alpha=0.8)
a1.set_ylabel('PDF', color='k')

cnt, b_obs = np.histogram(obs, bins=30)
p_obs = cnt / cnt.sum()
c_obs = np.cumsum(p_obs)
a1.bar(b_obs[:-1], p_obs, width=0.7, color='black', alpha=0.8)

plt.legend(['GCM', 'Corrected GCM', 'Observations'], loc='upper left')
plt.xlim([230, 320])
plt.xlabel('Temperature [\u00b0K]')

a2 = a1.twinx()
a2.plot(b_mod[1:], c_mod, color='green')
a2.set_ylabel('CDF', color='green')

a2 = a1.twinx()
a2.plot(b_cor[1:], c_cor, color='red')
a2.set_ylabel('CDF', color='k')

a2 = a1.twinx()
a2.plot(b_obs[1:], c_obs, color='black')
a2.set_ylabel('CDF', color='black')

plt.xlim([230, 320])
plt.savefig(f'histogram_{temp_type}.png', dpi=300)