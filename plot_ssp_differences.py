#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 13:13:59 2026

@author: khanh
"""

from datetime import datetime
import os
import sys 
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt 
import geopandas as gpd 
import cv2
from scipy.ndimage import zoom
import matplotlib.colors as colors
import datetime as tdelta
import calendar

####################################################################################
var = 'tas'
file = 'tas_day_GFDL-ESM4_ssp126_r1i1p1f1_gr1_20950101-21001231_10km.nc'
file_corrected = 'tas_day_GFDL-ESM4_ssp126_r1i1p1f1_gr1_20950101-21001231_10km_corrected.nc'

startDate = datetime(2099,5,1,0,0,0)
endDate = datetime(2099,9,30,0,0,0)

# this factor to resize and save plot for efficiency.
# scaled by original image / factor
factor = 5
####################################################################################

# read input ssp
inFile = '/home/khanh/Downloads/' + file
ds_in = nc.Dataset(inFile)

# read corrected
inFile_corrected = '/home/khanh/Downloads/' + file_corrected
ds_in_corrected = nc.Dataset(inFile_corrected)

lat = np.ma.filled(ds_in['lat'])
lon = np.ma.filled(ds_in['lon'])
# for i in range(0, len(lon)):
#     if lon[i] > 180:
#         lon[i] = lon[i] - 360
lon1 = ((np.ma.filled(ds_in['lon']) - 360))
fig, (ax1) = plt.subplots(1, 1, figsize = (12, 5)) 

iyymmdd = file_corrected.split('_')[6].split('-')[0]

imm = int(iyymmdd[0:4])
idd = int(iyymmdd[4:6])
iyy = int(iyymmdd[6:8])

modInitYear = datetime(imm, idd, iyy, 0, 0, 0)

# calculate the day. days start from 1850-01-01
modTime = np.ma.filled(ds_in_corrected['time'])
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

# file the range date
d1 = np.where(np.array(modDate) == startDate)
d2 = np.where(np.array(modDate) == endDate)
if len(d1[0]) > 0 and len(d2[0]) > 0:
    d1 = d1[0][0]
    d2 = d2[0][0]
else:
    raise ValueError('Please enter start date and end date in the range of the file')
    
zLon = int(len(lon)/factor)
zLat = int(len(lat)/factor)

ssp = np.mean(ds_in[var][d1:d2,:,:], axis=0)
ssp = cv2.resize(ssp, (zLon, zLat))
corrected = np.mean(ds_in_corrected[var][d1:d2,:,:], axis=0)
corrected = cv2.resize(corrected, (zLon, zLat))

dif = corrected - ssp

lonResize = zoom(lon, zLon/len(lon))
lonResize1 = zoom(lon1, zLon/len(lon1))
latResize = zoom(lat, zLat/len(lat))
# lat = cv2.resize(lat, 180)

# title
fileSSP = np.array(['ssp126', 'ssp245', 'ssp585'])
titleSSP = ['SSP126', 'SSP245', 'SSP585']
sspName = titleSSP[np.where(fileSSP == file_corrected.split('_')[3])[0][0]]

# plot bias corrected
fig, (ax1) = plt.subplots(1, 1, figsize = (12, 5)) 
vmin = -np.max([abs(np.min(corrected)), abs(np.max(corrected))])
vmax = np.max([abs(np.min(corrected)), abs(np.max(corrected))])
im1 = ax1.pcolormesh(lonResize, latResize, corrected, cmap='jet')
im1 = ax1.pcolormesh(lonResize1, latResize, corrected, cmap='jet')
df=gpd.read_file("/run/media/khanh/NU1/ssp585_pgw/shapefiles/test.shp")
df.plot(ax=ax1, color="none", edgecolor='black', linewidth=0.5)
fig.colorbar(im1, ax=ax1, label='Temperature [\u00b0K]')
ax1.set_xlim([-180, 180])
ax1.set_title(f'Bias Corrected GFDL ESM4 ({sspName})')
plt.savefig(f'corrected_{sspName}.png', dpi=300)
plt.close('all')

# plot ssp. use the same vmin/vmax from bias corrected
fig, (ax1) = plt.subplots(1, 1, figsize = (12, 5)) 
im1 = ax1.pcolormesh(lonResize, latResize, ssp, cmap='jet')
im1 = ax1.pcolormesh(lonResize1, latResize, ssp, cmap='jet')
df=gpd.read_file("/run/media/khanh/NU1/ssp585_pgw/shapefiles/test.shp")
df.plot(ax=ax1, color="none", edgecolor='black', linewidth=0.5)
fig.colorbar(im1, ax=ax1, label='Temperature [\u00b0K]')
ax1.set_xlim([-180, 180])
ax1.set_title(f'GFDL ESM4 ({sspName})')
plt.savefig(f'{sspName}.png', dpi=300)
plt.close('all')

# # plt.imshow(np.flipud(era))

fig, (ax1) = plt.subplots(1, 1, figsize = (12, 5)) 
vmin = -np.max([abs(np.min(dif)), abs(np.max(dif))])
vmax = np.max([abs(np.min(dif)), abs(np.max(dif))])

im1 = ax1.pcolormesh(lonResize, latResize, dif, cmap='bwr', vmin=vmin, vmax=vmax)
im1 = ax1.pcolormesh(lonResize1, latResize, dif, cmap='bwr', vmin=vmin, vmax=vmax)
df=gpd.read_file("/run/media/khanh/NU1/ssp585_pgw/shapefiles/test.shp")
df.plot(ax=ax1, color="none", edgecolor='black', linewidth=0.5)
fig.colorbar(im1, ax=ax1, label='Temperature [\u00b0C]')
ax1.set_xlim([-180, 180])
ax1.set_title(f'Differences ({sspName})')
plt.savefig(f'dif_{sspName}.png', dpi=300)
plt.close('all')