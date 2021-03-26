# -*- coding: utf-8 -*-
"""
find_optimal_thres finds the threshold separating the background and foreground.
This code can be used for images with a uniform background
and objects of one single intensity distribution. This code
is adopted from M Machacek, G Danuser, Biophys J (2006).

By Ernest Dec 2020
"""
import numpy as np 
from scipy import signal
import math
from find_relevant_max import find_relevant_max
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema


def find_optimal_thres(img_in, DEPTH, F_SIGMA=0.6, LOWER_CUT=0.005, UPPER_CUT=0.99, REL_RELEVANCE=0.6, TOT_RELEVANCE=0.005):

    DEPTH_options = [8, 10, 12, 14, 16]
    def DEPTH_conversion(i):
        switcher = {
            8: 2**8-1,
            10: 2**10-1,
            12: 2**12-1,
            14: 2**14-1,
            16: 2**16-1
            }
        return switcher.get(i, "Invalid bit depth")
    if DEPTH not in DEPTH_options:
        raise ValueError('unsuported image depth, only images of 8,10,12,14,16 bit are accepted.')
    else: 
        DEPTH = DEPTH_conversion(DEPTH)
###End parameters###
    img_hist, hist_val = np.histogram(img_in.ravel(), bins=DEPTH, range=(0, DEPTH))
    while len(img_hist) < len(hist_val):
        hist_val = np.delete(hist_val, -1)
    total_pix = sum(img_hist)
    cs = np.cumsum(img_hist) #calculate cumulative sum
    LOWER_THRES = LOWER_CUT*float(total_pix)
    UPPER_THRES = UPPER_CUT*float(total_pix)
    #find 0.5%
    i = 0
    while cs[i] < LOWER_THRES:
        i = i + 1
    i_lower = i
    
    #find 99%
    i = 0
    while cs[i] < UPPER_THRES:
        i = i + 1
    i_upper = i 
        
    img_hist[0:(i_lower+1)] = 0
    hist_val[0:(i_lower+1)] = 0
    img_hist = img_hist[0:(i_upper)]
    hist_val = hist_val[0:(i_upper)]
     
    # filter the histogram to smooth it
    if DEPTH == 65535:
        F_WINDOW=17
        F_SIGMA = 3.8
    elif  DEPTH == 16383:
        F_WINDOW=15
        F_SIGMA= 8
    elif  DEPTH == 255:
        F_WINDOW=15
        F_SIGMA= 15     
    elif  DEPTH < 16383:
        F_WINDOW=15
        F_SIGMA= 8
    
    #f_sigma_fourier = 1/(2*np.pi/F_SIGMA)/DEPTH
  
    #Data must have length more than 3 times filter order
    #test if this is the case
    if 3 * F_WINDOW >= len(img_hist):
        F_WINDOW = math.floor(len(img_hist)/3)
    
    #conversion to SD
    if DEPTH == 65535:
        F_SIGMA = (F_WINDOW-1)/(2*3.8)
    elif  DEPTH == 16383:
        F_SIGMA = (F_WINDOW-1)/(2*8)
    elif  DEPTH == 255:
        F_SIGMA = (F_WINDOW-1)/(2*15)    
    elif  DEPTH < 16383:
        F_SIGMA = (F_WINDOW-1)/(2*8)
       
    w = signal.windows.gaussian(M=F_WINDOW, std=F_SIGMA)
    img_hist_ff = signal.filtfilt(b=(w/sum(w)), a=1, x=img_hist)
      
    #find local maximas
    i_max = argrelextrema(img_hist_ff, np.greater)
    i_max = i_max[0] 
    val_max = img_hist_ff[i_max]
    
    # find local minimas
    i_min = argrelextrema(img_hist_ff, np.less)
    i_min = i_min[0]
    val_min = img_hist_ff[i_min]
    if len(i_min) < 1 or len(i_max) < 1:
        thresh  = 0
        max_bg  = 0
        max_obj = 0
        return thresh, max_bg, max_obj
    else:
        if i_min[-1] < i_max[-1]:
            i_min = np.append(i_min, (img_hist_ff.shape[0]-1))
            val_min = np.append(val_min, img_hist_ff[i_min[-1]])
        
        #find the relevant maximas from all local maximas
        ind_max, ind_min = find_relevant_max(i_max, val_max, i_min, val_min)
                
        if ind_max[0] == -99: 
            #no solution was found
            thresh  = 0
            max_bg  = 0
            max_obj = 0
            return thresh, max_bg, max_obj
       
        elif len(ind_max) < 2:
            print('Only one object found!')
            thresh  = 0
            max_bg  = 0
            max_obj = 0
            return thresh, max_bg, max_obj
    # elif len(ind_min.tolist())==0:
    #     print('No minima (thus threshold found)')
    #     ans=-1

        else:        
            thresh = ind_min[0]
            max_bg = ind_max[0]
            max_obj= ind_max[1]
            return thresh, max_bg, max_obj


