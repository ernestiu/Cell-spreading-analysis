# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 16:26:22 2020

@author: ernes
"""
import numpy as np
from scipy.signal import find_peaks


def measure_protrusions(normalized_coords, frame_rate = 6):
    
    
    # this is the beginning frame of a spreading cell. search for lowest point from the second frame to the middle of the movie
    lowest_point_idx = np.argmin(normalized_coords[1:len(normalized_coords)//2]) #don't start with 0
    lowest_point_idx = lowest_point_idx + 1


    # find peaks (i.e. protrusions)
    maxima, _ = find_peaks(normalized_coords, distance=3)
    maxima = maxima[maxima >= lowest_point_idx]
    minima, _ = find_peaks([normalized_coords[k]*-1 for k in range(len(normalized_coords))], distance=3)
    minima = minima[minima > lowest_point_idx]
    
    spread_duration = len(normalized_coords[lowest_point_idx:]) # in terms of number of frames
    retraction_rate = len(minima)/(spread_duration*frame_rate//60)
    avg_speed = (normalized_coords[-1] - normalized_coords[lowest_point_idx])*1000/(spread_duration*frame_rate)
    print('Retraction frequency (min-1) = ' + str(round(retraction_rate, 2)))
    print('Average protrusion speed (nm/s) = '+ str(round(avg_speed, 2)))
    
    
    return lowest_point_idx, maxima, minima, retraction_rate, avg_speed

# protrusion_persistence = []
# protrusion_distance = []
# protrusion_velocity = []
# retraction_velocity = []

# if minimas[0] > maximas[0]:
#     # measure protrosion properties
#     for jj in range(0, len(maximas)):
#         low = normalized_coords[minimas[jj]]
#         high = normalized_coords[maximas[jj+1]]
#         time = abs(maximas[jj+1] - minimas[jj])*frame_rate
#         protrusion_persistence.append(time)
#         protrusion_distance.append(abs(high - low))
#         protrusion_velocity.append(abs(high - low)/time)
#     # measure retraction properties
#     for jj in range(0, len(minimas)):
#         low = normalized_coords[minimas[jj]]
#         high = normalized_coords[maximas[jj]]
#         time = abs(maximas[jj] - minimas[jj])*frame_rate
#         retraction_velocity.append((abs(high - low)/time))

# else: # when minima[0] < maxima[0]
#     for jj in range(0, len(maximas)):
#         low = normalized_coords[minimas[jj]]
#         high = normalized_coords[maximas[jj]]
#         time = abs(maximas[jj] - minimas[jj])*frame_rate
#         protrusion_persistence.append(time)
#         protrusion_distance.append(abs(high - low))
#         protrusion_velocity.append(abs(high - low)/time)
#     for jj in range(0, len(minimas)):
#         low = normalized_coords[minimas[jj+1]]
#         high = normalized_coords[maximas[jj]]
#         distance = abs(maximas[jj] - minimas[jj+1])*frame_rate
#         retraction_velocity.append((abs(high - low)/distance))

# print('Protrusion persistence = ' + str(round(np.mean(protrusion_persistence),2)) + '±' + str(round(np.std(protrusion_persistence),2)))
# print('Protrusion distance = ' + str(round(np.mean(protrusion_distance),2))+ '±' + str(round(np.std(protrusion_distance),2)))
# print('Protrusion velocity = ' + str(round(np.mean(protrusion_velocity),4))+ '±' + str(round(np.std(protrusion_velocity),2)))
# print('Retraction velocity = ' + str(round(np.mean(retraction_velocity),4))+ '±' + str(round(np.std(retraction_velocity),2)))
