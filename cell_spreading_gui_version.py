# -*- coding: utf-8 -*-
"""
This functions takes a timelapse image, segment individual cells and measure cell area, circularity and aspect ratio over time.
--------
Input parameters:
    
    1. image: numpy array of the image
    2. fname: string, filename of the image
    3. save_masks: boolean, indicate whether individual cell masks generated should be saved 
    4. save_data: boolean, indicate whether cell area, circularity and aspect ratio should be exported as an excel spreadsheet
    5. interval: integer, how frequent images were acquired (will affect the data in the spreadsheet)
    6. pixel_size: float, area of a pixel
    7. bit_depth: integer
    8. small_obj: integer, the smallest acceptable object size in pixel
    9. save_destination: string, the saving destination of the masks, images etc
    
Outputs:
    print "done"
    
By Ernest Dec 2020    
"""
import numpy as np
from skimage import io
import matplotlib.pyplot as plt
from crop_cell_function import crop_cell
from cell_segmentation import cell_seg
import pandas as pd
from cell_measure import cell_measure
import re
import os


def cell_spreading(image, fname, save_masks, save_data, save_contour, show_img, interval, pixel_size, bit_depth, small_obj, save_destination):

    cell_num, label_mask, bounding_box = crop_cell(image)
    
    all_cell_masks, all_cell_props = cell_seg(image, cell_num, bounding_box, filename = fname, save_destination = save_destination,
                                              DEPTH = bit_depth, show_img = show_img, save_contour = save_contour, small_obj=small_obj)
    
    all_cell_area, all_cell_aspect_ratio, all_cell_circularity = cell_measure(all_cell_props, pixel_size = pixel_size)
    
    if save_masks:
        from tifffile import imsave 
        #script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(save_destination, 'Cell Masks/' + fname + '/')
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)
        for jj in range(len(all_cell_masks)):
            imsave(results_dir + fname + '_mask' + str(jj) + '.tif', all_cell_masks[jj].astype(np.uint8))
            print('saving: ' + str(jj+1) + '/' + str(len(all_cell_masks)))
                
    df = pd.DataFrame()    
      
    for n in range(len(all_cell_area)):
        df[fname + ' Cell areas' + str(n+1)] = pd.Series(all_cell_area[n])
        #replacing 0s with an empty box
        df[fname + ' Cell areas' + str(n+1)] = df[fname + ' Cell areas' + str(n+1)].replace('-', np.nan)
        
        df[fname + ' Aspect ratio' + str(n+1)] = pd.Series(all_cell_aspect_ratio[n])
        df[fname + ' Aspect ratio' + str(n+1)] = df[fname + ' Aspect ratio' + str(n+1)].replace('-', np.nan)
    
        df[fname + ' Circularity' + str(n+1)] = pd.Series(all_cell_circularity[n])
        df[fname + ' Circularity' + str(n+1)] = df[fname + ' Circularity' + str(n+1)].replace('-', np.nan)
        
    df['Time'] = pd.Series(np.linspace(start = 0, stop = int((len(df.index)-1)*interval), num = len(df.index)))
    df = df.set_index('Time') 
    if save_data:
        df.to_excel(save_destination + "/cell_spreading_data " + fname + ".xlsx")
        
    return print('done')




    