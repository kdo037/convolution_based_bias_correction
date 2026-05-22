#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 16:55:13 2026

@author: khanh
"""

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


################ CHANGE DATE AND TIME ####################################################
inputDir = '/home/khanh/Documents/biasCorrection/gaussianFilter/'
# example file name tas_1990-01-01.csv
temp_type = 'tasmax'
# Define desired date range
start = datetime(1990,1,8,0,0,0)  # start date
end = datetime(2014,9,15,0,0,0) # end date
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

convSizes = [0, 100, 500, 1000, 2000, 5000]
convSize = 0

filename = f'{temp_type}_convSize_{convSize}.csv'

dfv7 = pd.read_csv(f'{inputDir}{filename}')
dnt_str = np.array(dfv7['Date'])
r2 = np.array(dfv7['r2'])
mb = np.array(dfv7['mb'])
rmse = np.array(dfv7['rmse'])
avg_obs = np.array(dfv7['avg_obs'])
avg_mod = np.array(dfv7['avg_mod'])
dnt = []
for d in dnt_str:
    dnt.append(datetime.strptime(d, '%Y-%m-%d'))
    
fig1, ax1 = plt.subplots(1, 1, figsize = (6, 4))
ax1.plot(dnt, r2)
plt.plot(dnt, mb)