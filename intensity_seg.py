# -*- coding: utf-8 -*-
"""
This script includes two functions that performs segmentation using threshold_triangle function. intensity_seg is a more lenient thresholding function
while intensity_seg_str is a more strict function.

By Ernest Iu, Dec 2020
"""

from skimage import filters, morphology, measure
#import matplotlib.pyplot as plt
import scipy.ndimage as ndimage
from skimage.morphology import disk
from skimage.filters import threshold_triangle
import numpy as np


def intensity_seg(image, SE = disk(3), small_obj = 1000):
            
###the following uses intensity thresholding to create another mask
    
    intensity_mask = image > threshold_triangle(image)
    median_mask = filters.median(~intensity_mask, selem=SE)
    intensity_fill_mask = ndimage.morphology.binary_fill_holes(~median_mask)
    intensity_close_mask = ndimage.morphology.binary_closing(intensity_fill_mask, structure=SE)
    intensity_remove_small_object_mask = morphology.remove_small_objects(intensity_close_mask, min_size=small_obj)
    img_labels_bg = measure.label(intensity_remove_small_object_mask,connectivity=2)
    labels_stat = measure.regionprops(img_labels_bg)
    if labels_stat == []:
        return intensity_remove_small_object_mask
    else:
        largest_idx = np.argmax([aCell.area for aCell in labels_stat])                    
        img_bg = img_labels_bg == labels_stat[largest_idx].label
        return img_bg
    
def intensity_seg_str(image, SE = disk(3), small_obj = 1000):
            
###the following uses intensity thresholding to create another mask
    
    intensity_mask = image > threshold_triangle(image) + 0.5*np.std(image) 
    median_mask = filters.median(~intensity_mask, selem=SE)
    intensity_fill_mask = ndimage.morphology.binary_fill_holes(~median_mask)
    intensity_close_mask = ndimage.morphology.binary_closing(intensity_fill_mask, structure=SE)
    intensity_remove_small_object_mask = morphology.remove_small_objects(intensity_close_mask, min_size=small_obj)
    img_labels_bg = measure.label(intensity_remove_small_object_mask,connectivity=2)
    labels_stat = measure.regionprops(img_labels_bg)
    if labels_stat == []:
        return intensity_remove_small_object_mask
    else:
        largest_idx = np.argmax([aCell.area for aCell in labels_stat])                    
        img_bg = img_labels_bg == labels_stat[largest_idx].label
        return img_bg