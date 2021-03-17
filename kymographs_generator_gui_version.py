# -*- coding: utf-8 -*-
"""
This function creates kymographs from a stack of images.

By Ernest Dec 2020
"""

from skimage import io, measure
import matplotlib.pyplot as plt
import numpy as np
from cell_segmentation import cell_seg_no_cell_crop
import statistics
from matplotlib import gridspec
import pandas as pd
import os

def kymo_generator(image, fname, save_data, interval, pixel_size, bit_depth, small_obj = 1000, save_destination = os.path.dirname(__file__)):
    """
    This function takes an image, generates four kymographs, and analyze them.

    Parameters
    ----------
    image : array
        An input image.
    fname : string
        The filename.
    save_data : boolean
        Whether to save the data.
    interval : integer
        The interval at which images were acquired (e.g. every 5 seconds)
    pixel_size : integer
        The pixel size of the image.
    bit_depth : integer
        The bit depth of the image.
    small_obj : integer, optional
        The smallest object allowed. The default is 1000 pixels.
    save_destination : string, optional
        The saving directory. The default is os.path.dirname(__file__).

    Returns
    -------
    A confirmation note "done".

    """
    all_cell_masks, all_cell_props = cell_seg_no_cell_crop(image, filename = fname, DEPTH = bit_depth, small_obj = small_obj,
                                                            show_img = False,  save_contour = False)
    
    y, x = all_cell_props[0][-1].centroid
    y = int(y)
    x = int(x)
    
    kymo_1 = np.empty((y+1,all_cell_masks[0].shape[0]))
    kymo_2 = np.empty((all_cell_masks[0].shape[1]-y,all_cell_masks[0].shape[0]))
    kymo_3 = np.empty((x+1,all_cell_masks[0].shape[0]))
    kymo_4 = np.empty((all_cell_masks[0].shape[2]-x,all_cell_masks[0].shape[0]))
    width = 3
    all_kymos = []
    
    for slice_number in range (all_cell_masks[0].shape[0]):
        
        profile_line_1 = measure.profile_line(all_cell_masks[0][slice_number, :, :], src=(y, x), dst=(0, x), linewidth=width, mode='constant')
        kymo_1[:,slice_number] = np.flip(profile_line_1, axis=0)
       
        profile_line_2 = measure.profile_line(all_cell_masks[0][slice_number, :, :], src=(y, x), dst=(all_cell_masks[0][slice_number, :, :].shape[0]-1, x), linewidth=width, mode='constant')
        kymo_2[:,slice_number] = np.flip(profile_line_2, axis=0)
        
        profile_line_3 = measure.profile_line(all_cell_masks[0][slice_number, :, :], src=(y, x), dst=(y, 0), linewidth=width, mode='constant')
        kymo_3[:,slice_number] = np.flip(profile_line_3, axis=0)
        
        profile_line_4 = measure.profile_line(all_cell_masks[0][slice_number, :, :], src=(y, x), dst=(y, all_cell_masks[0][slice_number, :, :].shape[1]-1), linewidth=width, mode='constant')
        kymo_4[:,slice_number] = np.flip(profile_line_4, axis=0)
    
    all_kymos.append(kymo_1)
    all_kymos.append(kymo_2)
    all_kymos.append(kymo_3)
    all_kymos.append(kymo_4)
    
    
    del kymo_1, kymo_2, kymo_3, kymo_4 # to save memory
    
    
    from kymo_to_coords import kymo_to_coords
    all_normalized_coords = []
    all_filtered_coords = []
    
    for n in range(len(all_kymos)):
        normalized, filtered_coords = kymo_to_coords(all_kymos[n], thres=15, pixel_length = 0.1833333)
        all_normalized_coords.append(normalized)
        all_filtered_coords.append(filtered_coords)
    
        
    
    ################################dividing line###########################################
    
    from measure_protrusions import measure_protrusions
    
    all_plateau_idx = []
    all_minimas = []
    all_retraction_rate = []
    all_avg_speed = []
    all_lowest_point_idx = []
    
    
    print(fname + ' results')
    print('----------------------------------------')
    
    for n in range(len(all_normalized_coords)):
        
        lowest_point_idx, plateau_idx, minima, retraction_rate, avg_speed = measure_protrusions(normalized_coords = all_normalized_coords[n], frame_rate = interval)
        all_plateau_idx.append(plateau_idx)
        all_minimas.append(minima)
        all_retraction_rate.append(retraction_rate)
        all_avg_speed.append(avg_speed)
        all_lowest_point_idx.append(lowest_point_idx)
     
    
    all_avg_speed_avg = statistics.mean(all_avg_speed)
    all_avg_speed_stdev = statistics.stdev(all_avg_speed)
    
    all_retraction_rate_avg = statistics.mean(all_retraction_rate)
    all_retraction_rate_stdev = statistics.stdev(all_retraction_rate)
    
    print('----------------------------------------')
    print('Average retraction rate of all kymos = ' + str(round(all_retraction_rate_avg, 3))+ ' ± ' + str(round(all_retraction_rate_stdev,2)))
    print('Average protrusion speed of all kymos = ' + str(round(all_avg_speed_avg, 2))+ ' ± ' + str(round(all_avg_speed_stdev,2)))
    
    
    
    
    ################################dividing line###########################################
    
        
    color_1 = '#003f5c'
    color_2 = '#7a5195'
    color_3 = '#ef5675'
    color_4 = '#ffa600'
    
    fig = plt.figure(figsize=(20, 10)) # 20 in x and 10 in y
    gs = gridspec.GridSpec(2, 4) # 2 in x and 4 in y
    axes0 = plt.subplot(gs[:,0:2])
    axes0.imshow(image[-1,:,:], cmap='Greys')
    axes0.plot([x, x], [y, 0], color_1, [x, x], [y, all_cell_masks[0][slice_number, :, :].shape[0]-1], color_2,
                    [x, 0], [y, y], color_3, [x, all_cell_masks[0][slice_number, :, :].shape[1]-1], [y, y], color_4, linewidth = width, linestyle='dashed')
    axes0.axis('off')
   
    ###################
   
    axes1 = plt.subplot(gs[0,2])
    x_axis = np.linspace(start = 0, stop = int((len(all_normalized_coords[0])-1)*interval), num = len(all_normalized_coords[0]))
    axes1.plot(x_axis, all_normalized_coords[0], 'k')
    
    last_slope_point_0 = x_axis[all_plateau_idx[0]]
    
    axes1.plot([x_axis[all_lowest_point_idx[0]], last_slope_point_0], [all_normalized_coords[0][all_lowest_point_idx[0]], 
                                                                          all_normalized_coords[0][all_plateau_idx[0]]], color_1, linewidth = width/2, linestyle='dashed', label='Protrusion speed')
    
    # plot retraction points
    axes1.scatter(all_minimas[0]*interval, [all_normalized_coords[0][n] for n in all_minimas[0]], s=20, c='r', label='Retraction')
    axes1.legend(loc="lower right")
    for spine in axes1.spines.values():
        spine.set_edgecolor(color_1)
        spine.set_linewidth(3)
    axes1.set_ylabel('Distance ‎(µm)')
    axes1.set_ylim(top = int(np.max(all_normalized_coords)+2)) #limit y axis to be the maximum of all the numbers
    
    ###################
    
    axes2 = plt.subplot(gs[0,3], sharex=axes1, sharey=axes1)
    x_axis = np.linspace(start = 0, stop = int((len(all_normalized_coords[1])-1)*interval), num = len(all_normalized_coords[1]))
    axes2.plot(x_axis, all_normalized_coords[1], 'k')
    
    last_slope_point_1 = x_axis[all_plateau_idx[1]]
    
    axes2.plot([x_axis[all_lowest_point_idx[1]], last_slope_point_1], [all_normalized_coords[1][all_lowest_point_idx[1]], 
                                                                          all_normalized_coords[1][all_plateau_idx[1]]], color_2, linewidth = width/2, linestyle='dashed', label='Protrusion speed')
    
    axes2.scatter(all_minimas[1]*interval, [all_normalized_coords[1][n] for n in all_minimas[1]], s=20, c='r', label='Retraction')
    axes2.legend(loc="lower right")
    for spine in axes2.spines.values():
        spine.set_edgecolor(color_2)
        spine.set_linewidth(3)
    
    ###################
    
    axes3 = plt.subplot(gs[1,2], sharex=axes1, sharey=axes1)
    x_axis = np.linspace(start = 0, stop = int((len(all_normalized_coords[2])-1)*interval), num = len(all_normalized_coords[2]))
    axes3.plot(x_axis, all_normalized_coords[2], 'k')
    
    last_slope_point_2 = x_axis[all_plateau_idx[2]]
    
    axes3.plot([x_axis[all_lowest_point_idx[2]], last_slope_point_2], [all_normalized_coords[2][all_lowest_point_idx[2]], 
                                                                          all_normalized_coords[2][all_plateau_idx[2]]], color_3, linewidth = width/2, linestyle='dashed', label='Protrusion speed')
    
    axes3.scatter(all_minimas[2]*interval, [all_normalized_coords[2][n] for n in all_minimas[2]], s=20, c='r', label='Retraction')
    axes3.legend(loc="lower right")
    for spine in axes3.spines.values():
        spine.set_edgecolor(color_3)
        spine.set_linewidth(3)
    axes3.set_xlabel('Time (s)')
    axes3.set_ylabel('Distance ‎(µm)')
    
    ###################
    
    axes4 = plt.subplot(gs[1,3], sharex=axes1, sharey=axes1)
    x_axis = np.linspace(start = 0, stop = int((len(all_normalized_coords[3])-1)*interval), num = len(all_normalized_coords[3]))
    axes4.plot(x_axis, all_normalized_coords[3], 'k')
    
    last_slope_point_3 = x_axis[all_plateau_idx[3]]
    
    axes4.plot([x_axis[all_lowest_point_idx[3]], last_slope_point_3], [all_normalized_coords[3][all_lowest_point_idx[3]], 
                                                                          all_normalized_coords[3][all_plateau_idx[3]]], color_4, linewidth = width/2, linestyle='dashed', label='Protrusion speed')
    axes4.scatter(all_minimas[3]*interval, [all_normalized_coords[3][n] for n in all_minimas[3]], s=20, c='r', label='Retraction')
    axes4.legend(loc="lower right")
    for spine in axes4.spines.values():
        spine.set_edgecolor(color_4)
        spine.set_linewidth(3)
    axes4.set_xlabel('Time (s)')
    
    plt.show()    
    
    
    ################################dividing line###########################################
    if save_data:
    
        df = pd.DataFrame()    
        
        df[fname + ' Kymo_1'] = pd.Series(all_normalized_coords[0])
        df[fname + ' Kymo_1' + ' retraction pts'] = pd.Series(all_minimas[0]*interval)
        
        df[fname + ' Kymo_2'] = pd.Series(all_normalized_coords[1])
        df[fname + ' Kymo_2' + ' retraction pts'] = pd.Series(all_minimas[1]*interval)
        
        df[fname + ' Kymo_3'] = pd.Series(all_normalized_coords[2])
        df[fname + ' Kymo_3' + ' retraction pts'] = pd.Series(all_minimas[2]*interval)
        
        df[fname + ' Kymo_4'] = pd.Series(all_normalized_coords[3])
        df[fname + ' Kymo_4' + ' retraction pts'] = pd.Series(all_minimas[3]*interval)
        
        df['Time'] = pd.Series(np.linspace(start = 0, stop = int((len(df.index)-1)*interval), num = len(df.index)))
        df = df.set_index('Time') 
       
        df.to_excel(save_destination + "/" + fname + "_kymographs" + ".xlsx")
    
    return print('done')