#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 15:16:16 2026

@author: khanh
"""

# this script plot spatial mean bias and r2

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
import pandas as pd

####################################################################################
temp_type = 'tas'
resolution = '10km'
statDir = '/home/khanh/Documents/biasCorrection/gaussianFilter/stats/'
####################################################################################

# read input csv
filename = f'location_stats_{temp_type}_{resolution}.csv'
df = pd.read_csv(f'{statDir}{filename}', low_memory=False)
stationID = np.array(df['station_id'])
locationName = np.array(df['name'])
lat = np.array(df['lat'])
lon = np.array(df['lon'])
lon1 = np.array(df['lon']) - 360

r2_corrected = np.array(df['r2_corrected'])
mb_corrected = np.array(df['mb_corrected'])
rmse_corrected = np.array(df['rmse_corrected'])
r2_ssp = np.array(df['r2_ssp'])
mb_ssp = np.array(df['mb_ssp'])
rmse_ssp = np.array(df['rmse_ssp'])

# remove invalid value
sspInvalidInd = np.where(mb_ssp == -9999)
correctedInvalidInd = np.where(mb_corrected == -9999)

r2_corrected = np.delete(r2_corrected, sspInvalidInd)
mb_corrected = np.delete(mb_corrected, sspInvalidInd)
rmse_corrected = np.delete(rmse_corrected, sspInvalidInd)

r2_ssp = np.delete(r2_ssp, sspInvalidInd)
mb_ssp = np.delete(mb_ssp, sspInvalidInd)
rmse_ssp = np.delete(rmse_ssp, sspInvalidInd)

lat = np.delete(lat, sspInvalidInd)
lon = np.delete(lon, sspInvalidInd)
lon1 = np.delete(lon1, sspInvalidInd)

# plot bias corrected
vmin = -5
vmax = 5
fig, (ax1) = plt.subplots(1, 1, figsize = (12, 5)) 
im1 = ax1.scatter(lon, lat, c=mb_ssp, s=5, cmap='bwr', vmin=vmin, vmax=vmax)
im1 = ax1.scatter(lon1, lat, c=mb_ssp, s=5, cmap='bwr', vmin=vmin, vmax=vmax)
df=gpd.read_file("/run/media/khanh/NU1/ssp585_pgw/shapefiles/test.shp")
df.plot(ax=ax1, color="none", edgecolor='black', linewidth=0.5)
fig.colorbar(im1, ax=ax1, label='Temperature [\u00b0K]')
ax1.set_xlim([-180, 180])
# ax1.set_title(f'Bias Corrected GFDL ESM4 ({sspName})')
plt.savefig(f'stat_{temp_type}_{resolution}.png', dpi=300)
plt.close('all')