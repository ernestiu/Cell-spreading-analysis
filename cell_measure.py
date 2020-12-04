# -*- coding: utf-8 -*-
"""
This script includes a function that takes regionprops and generates the properties of the regionprops

By Ernest Iu Dec 2020
"""
import numpy as np
#from skimage import measure, feature
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

def cell_measure(props, pixel_size):
    """

    Parameters
    ----------
    props : dictionary
        A regionprop.
    pixel_size : integer
        The pixel size of the image.

    Returns
    -------
    all_cell_area : a numpy array consisted of all area measurements 
    all_cell_aspect_ratio: a numpy array consisted of all aspect ratio measurements 
    all_cell_circularity: a numpy array consisted of all circularity measurements 


    """
    
    all_cell_area = []
    all_cell_aspect_ratio = []
    all_cell_circularity = []
    
    for n, cell in enumerate(props): #for every cell detected
        cell_areas = []
        cell_aspect_ratio = []
        cell_circularity = []
        num = 0
        for kk in range(len(cell)): #for every slice
            if cell[kk] == [] or cell[kk] == 0:
                cell_areas.append(0)
                cell_aspect_ratio.append(0)
                cell_circularity.append(0)
                num = num +1
                #print('No segmented objects identified in frame ' + str(kk+1))
            else:
                cell_areas.append((cell[kk].area)*pixel_size**2)
                cell_aspect_ratio.append(cell[kk].minor_axis_length/cell[kk].major_axis_length)
                cell_circularity.append((cell[kk].area*4*np.pi)/(cell[kk].perimeter**2))
        all_cell_area.append(cell_areas)
        all_cell_aspect_ratio.append(cell_aspect_ratio)
        all_cell_circularity.append(cell_circularity)
        print(str(num) + ' frames are skipped in cell ' + str(n+1))
        
    for cell, measurments in enumerate(zip(all_cell_area, all_cell_circularity)):
        x = np.array(np.linspace(0, len(measurments[0])-1, len(measurments[0])))[::2]
        y_area = np.array(measurments[0])[::2] # area
        y_cl = np.array(measurments[1])[::2] # circularity
        #filt_y = savgol_filter(y, 5, 3) # window size 51, polynomial order 3
        fig, ax1 = plt.subplots()
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Area', color='b')
        plt.title('Cell ' + str(cell+1))
        ax1.scatter(x, y_area, s=10)
        ax2 = ax1.twinx()
        ax2.set_ylabel('Circularity', color='r')  # we already handled the x-label with ax1
        ax2.scatter(x, y_cl, s=10, color='r')
        fig.tight_layout()
        plt.show()
    # for ar in all_cell_aspect_ratio:
    #     x = np.array(np.linspace(0, len(ar)-1, len(ar)))[::2]
    #     y = np.array(ar)[::2]
    #     plt.scatter(x, y, s=10)
    #     plt.xlabel('Time')
    #     plt.ylabel('AR')
    #     plt.show() 

     
    return np.asarray(all_cell_area), np.asarray(all_cell_aspect_ratio), np.asarray(all_cell_circularity)
    
            