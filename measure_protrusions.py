# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import find_peaks, savgol_filter

from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def logistic_growth(t, a, b, c):
    return c / (1 + a * np.exp(-b*t))

def logistic_fit(all_areas):
    """
    This function takes a list of values (e.g. y coordinates) and fits a logistic growth curve.
    
    Parameters
    ----------
    all_areas : list
        A list of values


    Returns
    -------
    a : the parameter that determines the rate of exponential growth
    b : the parameter that determines the start of exponential growth
    c : the parameter that determines the plateau of the curve

    """
    #for area in all_areas:
    x = np.array(np.linspace(0, len(all_areas)-1, len(all_areas)))
    y = np.array(all_areas)
    
    (a, b, c), cov = curve_fit(logistic_growth, x, y)

    plt.scatter(x, y, s=0.8)
    plt.plot(x, logistic_growth(x, a, b, c),'r-',  linewidth=3)
    plt.xlabel('Frame')
    plt.ylabel('Area')
    plt.legend(['Logistic model', 'Experimental data'])
    plt.show()
    return a, b, c

def measure_protrusions(normalized_coords, frame_rate = 6):
    """
    This function takes the coordinates (tuples) of the membrane and measure protrusion properties.
    Parameters
    ----------
    normalized_coords : list
        A list of tuples
    frame_rate : integer, optional
        The frame rate at which images were acquired. The default is 6.

    Returns
    -------
    lowest_point_idx : integer
        The first frame when the membrane starts to move.
    plateau_time : list
        A list of plateaus identified.
    minima : list
        A list of minima (retractions) identified.
    retraction_rate : float
        The average retraction frequency.
    avg_speed : float
        The average protrusion speed.

    """

    # this is the beginning frame of a spreading cell. search for lowest point from the second frame to the middle of the movie
    lowest_point_idx = np.argmin(normalized_coords[1:len(normalized_coords)//2]) #don't start with 0
    lowest_point_idx = lowest_point_idx + 1
    
    # smooth the curve
    smoothed_y = savgol_filter(normalized_coords, 51, 3) # window size 51, polynomial order 3


    # calculate the fitting parameters   
    a, b, c = logistic_fit(smoothed_y[lowest_point_idx:])
    
    # find the plateau point by searching for the value closest to parameter c
    plateau = min(normalized_coords, key=lambda x:abs(x-c))
    
    # find the index of the plateau
    plateau_time = normalized_coords.index(plateau)
    
    # find retraction events
    minima, _ = find_peaks([normalized_coords[k]*-1 for k in range(lowest_point_idx, plateau_time)], distance=3)
    minima = minima[minima > lowest_point_idx]
    
    spread_duration = len(normalized_coords[lowest_point_idx:plateau_time]) # in terms of number of frames
    retraction_rate = len(minima)/(spread_duration*frame_rate//60)
    avg_speed = (plateau - normalized_coords[lowest_point_idx])*1000/(spread_duration*frame_rate)
    print('Retraction frequency (min-1) = ' + str(round(retraction_rate, 2)))
    print('Average protrusion speed (nm/s) = '+ str(round(avg_speed, 2)))


    return lowest_point_idx, plateau_time, minima, retraction_rate, avg_speed

        
        # find the first increase in slope (using second derivative) and first decrease in slope
    

#     print('Warning: Curve fitting unsuccessful - an estimation of cell spreading progress is used.')
#     # this is the beginning frame of a spreading cell. search for lowest point from the second frame to the middle of the movie
#     lowest_point_idx = np.argmin(normalized_coords[1:len(normalized_coords)//2]) #don't start with 0
#     lowest_point_idx = lowest_point_idx + 1


#     # find peaks (i.e. protrusions)
#     maxima, _ = find_peaks(normalized_coords, distance=3)
#     maxima = maxima[maxima >= lowest_point_idx]
    
#     # find retraction events
#     minima, _ = find_peaks([normalized_coords[k]*-1 for k in range(lowest_point_idx, len(normalized_coords))], distance=3)
#     minima = minima[minima > lowest_point_idx]
    
#     spread_duration = len(normalized_coords[lowest_point_idx:]) # in terms of number of frames
#     retraction_rate = len(minima)/(spread_duration*frame_rate//60)
#     avg_speed = (normalized_coords[-1] - normalized_coords[lowest_point_idx])*1000/(spread_duration*frame_rate)
#     print('Retraction frequency (min-1) = ' + str(round(retraction_rate, 2)))
#     print('Average protrusion speed (nm/s) = '+ str(round(avg_speed, 2)))


    # return lowest_point_idx, maxima, minima, retraction_rate, avg_speed


    

