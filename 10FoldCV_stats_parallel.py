#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 13:26:55 2026

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

################ CHANGE DATE AND TIME ####################################################
inputDir = '/home/khanh/Documents/biasCorrection/gaussianFilter/10FoldCV/10km/tas/'
# example file name tas_1990-01-01.csv
temp_type = 'tas'
# Define desired date range
start = datetime(1990,3,1,0,0,0)  # start date
end = datetime(1996,2,1,0,0,0) # end date
################ CHANGE DATE AND TIME ####################################################

def input_data(i):
    monthIndex = [[] for x in range(0, 12)]
    count = 0
    pStart = start + tdelta.timedelta(days = int(i))

    leapYear = calendar.isleap(pStart.year)
    if pStart.month != 2 or pStart.day != 29 or not leapYear:
        filename = f'{temp_type}_{pStart.year}-{str(pStart.month).zfill(2)}-{str(pStart.day).zfill(2)}.csv'
        with open(f'{inputDir}{filename}', 'r', encoding = 'utf-8', errors = 'ignore') as readFile:
            reader = csv.reader(readFile)
            lines = list(reader)
        for i in range(1, len(lines)):
            stationID=(lines[i][0])
            locationName=(lines[i][1])
            lat=(lines[i][4])
            lon=(lines[i][5])
            obs=(lines[i][6])
            cor=(lines[i][7])
            mod=(lines[i][8])
            dnt=(start)
            monthIndex[start.month-1]=(count)
            count += 1
            
        # # print(filename)
        # df = pd.read_csv(f'{inputDir}{filename}')
        # stationID = np.array(df['station_id'])
        # locationName = df['name']
        # lat = np.array(df['lat'])
        # lon = np.array(df['lon'])
        # obs = np.array(df['obs'])
        # cor = np.array(df['corrected'])
        # mod = np.array(df['wrf'])
        # dnt = np.array(pStart)
        # monthIndex[pStart.month-1].append(count)

          
        return stationID, locationName, lat, lon, obs, cor, mod

# compare model and obs using parallel python
leap = 0
initYear = start.year
for i in range(0, end.year - start.year):
    if calendar.isleap(initYear):
        leap += 1
    initYear += 1

dd = (end - start).days
i = np.linspace(0, (dd)-1, (dd), dtype='int')

max_cpus = 24
with Pool(processes=max_cpus) as pool:
    values = pool.map(input_data, i)

np.array(values)

# stationID = []
# locationName = []
# lat = []
# lon = []
# obs = []
# cor = []
# mod = []
# for i in range(0, len(values)):
#     stationID = np.concatenate((stationID, values[i][0][:]))
#     locationName = np.concatenate((stationID, values[i][1][:]))
#     lat = np.concatenate((stationID, values[i][2][:]))
#     lon = np.concatenate((stationID, values[i][3][:]))
#     obs = np.concatenate((stationID, values[i][4][:]))
#     cor = np.concatenate((stationID, values[i][5][:]))
#     mod = np.concatenate((stationID, values[i][6][:]))

# r = [[] for x in range(0, 12)] 
# r2 = [[] for x in range(0, 12)]
# mb = [[] for x in range(0, 12)]
# rmse = [[] for x in range(0, 12)]
# lat_array = [[] for x in range(0, 12)]
# lat_array = [[] for x in range(0, 12)]
# locationName_array = [[] for x in range(0, 12)]
# stationID_array = [[] for x in range(0, 12)]
# # compute the monthly average
# for i in range(0, 12): # 12 months
#     obs