# -*- coding: utf-8 -*-
"""
this function returns 3 variables, number of cells, the labelled mask and the coordinates of the bounding box
"""

import numpy as np
from skimage import morphology, measure
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches



def crop_cell(image, min_size=20000, max_size=90000, ar_thres=0.6):
    
    max_proj = np.max(image, axis=0)
    
    mask_image = max_proj > np.mean(max_proj) + 0.5*np.std(max_proj)

    clean_mask = morphology.remove_small_objects(mask_image, min_size=min_size)

    label_mask = morphology.label(clean_mask)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(max_proj, cmap=plt.cm.gray)
    
    bounding_box = []
    num_1 = 0 # number of cells that are too close to the image borders
    num_2 = 0 # number of cells that are too elongated
    num_3 = 0 # number of cells that are too big
    
    for aCell in measure.regionprops(label_mask):
        
        min_row, min_col, max_row, max_col = aCell.bbox
        
        aspect_ratio = aCell.minor_axis_length/aCell.major_axis_length
               
        if min_row - 30 <= 0 or min_col - 30 <= 0 or max_row + 30 >= max_proj.shape[0] or max_col + 30 >= max_proj.shape[1]:
            num_1 = num_1 + 1
            rect_r = mpatches.Rectangle((min_col, min_row), max_col - min_col, max_row - min_row,
                                        fill=False, edgecolor='#989898', linewidth=3)
            ax.add_patch(rect_r)
        
        elif aspect_ratio < ar_thres:
            num_2 = num_2 + 1
            rect_r = mpatches.Rectangle((min_col, min_row), max_col - min_col, max_row - min_row,
                                        fill=False, edgecolor='#989898', linewidth=3)
            ax.add_patch(rect_r)
            
        else:
            if aCell.area > max_size:
                num_3 = num_3 + 1
                rect_r = mpatches.Rectangle((min_col, min_row), max_col - min_col, max_row - min_row,
                                            fill=False, edgecolor='#989898', linewidth=3)
                ax.add_patch(rect_r)
                
            else: 
                cell_boundaries = [min_row - 30, min_col - 30, max_row + 30, max_col + 30]
                bounding_box.append(cell_boundaries)
                rect = mpatches.Rectangle((min_col, min_row), max_col - min_col, max_row - min_row,
                                          fill=False, edgecolor='green', linewidth=3)
                ax.add_patch(rect)
    ax.set_axis_off()
    plt.show()            
    print('Summary: ')
    print(str(len(measure.regionprops(label_mask))) + ' cells are identified.')
    if num_1 > 0:
        print(str(num_1) + ' cells are too close to the boundary.')
    if num_2 > 0:
        print(str(num_2) + ' cells are too elongated.')
    if num_3 > 0:
        print(str(num_3) + ' segmented cells are too big.')
    print(str(len(bounding_box)) + ' cells will be analyzed.')
        
    return (len(bounding_box), label_mask, bounding_box)

