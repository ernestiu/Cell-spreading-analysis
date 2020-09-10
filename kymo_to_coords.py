# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 12:09:02 2020

@author: ernes
"""
import numpy as np
import statistics
from skimage import filters, morphology, measure
import matplotlib.pyplot as plt

def kymo_to_coords(kymo, thres=15, pixel_length = 0.1833333):
    
    smooth_kymo = filters.median(kymo > 0, morphology.disk(3))
    # plt.imshow(smooth_kymo)
    # plt.show()
    sobel_kymo = filters.sobel(smooth_kymo)
    # plt.imshow(sobel_kymo)
    # plt.show()
    coords = []
    coords.append(np.argmax(np.gradient(smooth_kymo[:,0]*1)))
    for time in range(1, sobel_kymo.shape[1]-1):
        local_max = np.argmax(sobel_kymo[:,time])
        coords.append(local_max)
    coords.append(np.argmax(np.gradient(smooth_kymo[:,-1]*1)))
     
    # the following code replaces outliers with interpolated points
    filtered_coords = [] #save all the filtered points
    filtered_coords.append(coords[0])
    for kk in range(1, len(coords)-1):
        z = coords[kk]
        z_before = coords[kk-1]
        z_after = coords[kk+1]
        if np.abs(z_before - z) > thres or np.abs(z_after - z) > thres:

            if kk < 3:
                new_coords = int(statistics.mean([coords[kk+1], coords[kk+2], coords[kk+3]]))
                filtered_coords.append(new_coords)
            if kk >= 3 and kk <= len(coords)-4:
                new_coords = int(statistics.mean([coords[kk+1], coords[kk+2], coords[kk+3], coords[kk-1], coords[kk-2], coords[kk-3]]))
                filtered_coords.append(new_coords)
            if kk > len(coords)-4:
                new_coords = int(statistics.mean([coords[kk-1],coords[kk-2],coords[kk-3]]))
                filtered_coords.append(new_coords)
        else:
            filtered_coords.append(z)
    filtered_coords.append(coords[-1])
    
    # the following code normalize the coordinates to the lowest point
    normalized_coords = []
    for jj in range(len(filtered_coords)):
        #norm_coords = filtered_coords[jj]*-1 + max(filtered_coords)
        norm_coords = (filtered_coords[jj]*-1 + max(filtered_coords)) * pixel_length
        normalized_coords.append(norm_coords)
    
    return normalized_coords, filtered_coords