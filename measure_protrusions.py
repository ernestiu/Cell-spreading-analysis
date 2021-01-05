# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import find_peaks


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
    maxima : list
        A list of maxima (protrusions) identified.
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


    # find peaks (i.e. protrusions)
    maxima, _ = find_peaks(normalized_coords, distance=3)
    maxima = maxima[maxima >= lowest_point_idx]
    minima, _ = find_peaks([normalized_coords[k]*-1 for k in range(lowest_point_idx, len(normalized_coords))], distance=3)
    minima = minima[minima > lowest_point_idx]
    
    spread_duration = len(normalized_coords[lowest_point_idx:]) # in terms of number of frames
    retraction_rate = len(minima)/(spread_duration*frame_rate//60)
    avg_speed = (normalized_coords[-1] - normalized_coords[lowest_point_idx])*1000/(spread_duration*frame_rate)
    print('Retraction frequency (min-1) = ' + str(round(retraction_rate, 2)))
    print('Average protrusion speed (nm/s) = '+ str(round(avg_speed, 2)))
    
    
    return lowest_point_idx, maxima, minima, retraction_rate, avg_speed


