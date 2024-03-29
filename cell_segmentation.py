# -*- coding: utf-8 -*-
"""
There are two functions in this script: cell_seg requires the cropping function and cell_seg_no_cell_crop doesn't. They both take an 
image and perform image segmentation.

By Ernest Dec 2020
"""
import numpy as np
from skimage import measure, filters
import matplotlib.pyplot as plt
import scipy.ndimage as ndimage
from skimage.morphology import disk, binary_closing
from matplotlib import patches
from find_optimal_thres import find_optimal_thres
from intensity_seg import intensity_seg, intensity_seg_str
from scipy.ndimage import gaussian_filter
import os

def cell_seg(image, cell_num, bounding_box, filename, save_destination = os.path.dirname(__file__), sigma = 1, MEDIAN_F = 3, SE = disk(6), DEPTH = 16, tolerance = 2000, small_obj = 1000, show_img = False, save_contour = False):
    """    
    Parameters
    ----------
    image : array
        An image.
    cell_num : integer
        The total number of cells detected by crop_cell function.
    bounding_box : list
        A list of tuples that indicate the 4 corners of each bounding box
    filename : string
        The filename of the image
    save_destination : string, optional
        The saving destination of the masks, images etc. The default is the directory of the script.
    sigma : integer, optional
        The degree of Gaussian blur. The default is 1.
    MEDIAN_F : integer, optional
        The size of median filter. The default is 3.
    SE : array, optional
        The structuring element used for morphological operations. The default is disk(6).
    DEPTH : integer, optional
        The image bit depth. The default is 16.
    tolerance : integer, optional
        The maximum number of pixels allowed to be removed after morphological operations. The default is 2000 pixels.
    small_obj : integer, optional
        The smallest object allowed. The default is 1000 pixels.
    show_img : boolean, optional
        Whether to show images or not. The default is False.
    save_contour : boolean, optional
        Whether to save the cell contours or not. The default is False.

    Returns
    -------
    all_cell_masks : list
        A list of binary masks generated from cell segmentation.
    all_cell_props : list
        A list of regionprops of each cell and each binary mask.

    """
    # create placeholders to store masks and regionprops
    all_cell_masks = [] #check line 77 and 100
    all_cell_props = []
    
    for kk in range(cell_num): #go thru each cell
    
        labels_stat = None #reset labels_stat for each cell
        
        # create placeholders to store masks and regionprops of each slice
        cell_masks = []
        cell_props = []
        
        # retrieve bounding box for each cell
        cell = image[:,bounding_box[kk][0]:bounding_box[kk][2],bounding_box[kk][1]:bounding_box[kk][3]] #the following code returns a cropped image of timelapse image
        # create an empty array to store masks
        cell_masks = np.empty(cell.shape, dtype=np.uint8)
        # apply gaussian filter and enhance contrast by laplacian filter
        image_smooth = gaussian_filter(cell, sigma=sigma)
        image_smooth = image_smooth + filters.laplace(image_smooth, ksize=3)
        
        
        for ii in range(cell.shape[0]): #going through individual slice of one single cell:
            
            flag = 0
            
            # finding threshold using the histogram function
            thresh_val, max_bg_val, max_obj_val = find_optimal_thres(image_smooth[ii, :, :], DEPTH)
            
            if thresh_val == 0:
                #print('Histogram based segmentation failed, now try other segmentation method.')  
                flag = 1
                # reroute to another thresholding method
                img_bg = intensity_seg(image_smooth[ii, :, :])
                
            else: 
                img_thresh = image_smooth[ii, :, :] < thresh_val 
                
                # apply median filter to smooth the edge of the binary mask
                img = ndimage.median_filter(img_thresh, footprint=np.ones((MEDIAN_F,MEDIAN_F)))
                img = ~img
                
                # label and regionprop the mask to find out the largest object (i.e. the cell) in the mask
                img_labels = measure.label(img,connectivity=2)
                labels_stat = measure.regionprops(img_labels)         
                largest_idx = np.argmax([i.area for i in labels_stat])
                img_bg = img_labels == labels_stat[largest_idx].label
                
                # measure the bounding box of the cell to eliminate cells too close to the borders
                min_row, min_col, max_row, max_col = labels_stat[largest_idx].bbox
                if min_row == 0 or min_col == 0 or max_row == img_bg.shape[0] or max_col == img_bg.shape[1]:
                    #print('Segmented area is too close to the image border. Try other segmentation method.')
                    flag = 1
                    img_bg = intensity_seg_str(image_smooth[ii, :, :])
                
                else:   
                    # fill holes and close the binary mask
                    img_bg = ndimage.morphology.binary_fill_holes(img_bg)    
                    img_bg_er_dil = binary_closing(img_bg, selem=SE)   
                    
                    # measure how many pixels where removed
                    diff_img = img_bg*1 - img_bg_er_dil*1
        
                    rem_pix = abs(sum(sum(diff_img)))
                    #print('Number of removed pixels: ' + str(rem_pix))
                    if rem_pix > tolerance:
                        #print('Histogram based segmentation removed too many pixels, now try other segmentation method.')
                        flag = 1
                        # reroute to another thresholding method because the first segmentation method failed
                        img_bg = intensity_seg(image_smooth[ii, :, :])
                    else:
                        img_bg = img_bg_er_dil
                        #compare change in area with previous frame
                        if abs(np.bincount(img_bg.flat)[1:] - labels_stat[0].area)/labels_stat[0].area > 0.5:
                            #print('Segmented area is 50% larger than that of the previous frame. Try other segmentation method.')
                            flag = 1
                            img_bg = intensity_seg(image_smooth[ii, :, :])

            cell_masks[ii] = img_bg #save the mask to the array created in the beginning

            # label and regionprops the binary masks to measure the properties of the cell (e.g. area)
            img_labels = measure.label(img_bg)
            labels_stat = measure.regionprops(img_labels)
            
            # whether to show the segmented image during the process. it is False by default to save memory
            if show_img:
                img_edge = measure.find_contours(img_bg, 0)            
                fig, axes = plt.subplots(ncols=1, nrows=1, figsize=(6, 5))
                plt.tight_layout()
                axes.axis('off')
                axes.imshow(cell[ii,:,:], cmap=plt.cm.gray)
                for acontour in img_edge:
                    axes.add_patch(patches.Polygon(acontour[:, [1, 0]], linewidth=2, edgecolor='r', facecolor='none'))      
                    # whether to save the contour overlay. by default, it will create a folder cell contours in the same directory
                    # as the script and save all the images as png
                    if save_contour:
                        results_dir = os.path.join(save_destination, 'Cell Contours/' + filename + '/cell_' + str(kk) + '/')
                        if not os.path.isdir(results_dir):
                            os.makedirs(results_dir)
                        plt.savefig(results_dir + filename + '_cell_' + str(kk) + '_' + str(ii) + '.png', transparent=True, dpi=150, bbox_inches='tight', pad_inches = 0)
                    plt.show()
            
            if flag == 0:
                print('Cell segmentation progress: ' + str(ii+1) + '/' + str(cell.shape[0]) + '  Segmentation method: Histogram minima')
            else:
                print('Cell segmentation progress: ' + str(ii+1) + '/' + str(cell.shape[0]) + '  Segmentation method: Triangle method')
            
            if labels_stat == []:
                print('no cells are identified.')
                cell_props.append(0)

            else:
                largest_idx = np.argmax([aCell.area for aCell in labels_stat])                    
                cell_props.append(labels_stat[largest_idx])

        all_cell_masks.append(cell_masks) 
        all_cell_props.append(cell_props)
    return all_cell_masks, all_cell_props


def cell_seg_no_cell_crop(image, filename, save_destination = os.path.dirname(__file__), cell_num = 1, sigma = 1, MEDIAN_F = 3, SE = disk(6), DEPTH = 16, tolerance = 2000, small_obj = 1000, show_img = False, save_contour = False):
    # create placeholders to store masks and regionprops
    all_cell_masks = [] #check line 77 and 100
    all_cell_props = []
    
    for kk in range(cell_num): #go thru each cell
    
        labels_stat = None #reset labels_stat for each cell
        
        # create placeholders to store masks and regionprops of each slice
        cell_masks = []
        cell_props = []
        
        # retrieve bounding box for each cell
        cell = image 
        # create an empty array to store masks
        cell_masks = np.empty(cell.shape, dtype=np.uint8)
        # apply gaussian filter and enhance contrast by laplacian filter
        image_smooth = gaussian_filter(cell, sigma=sigma)
        image_smooth = image_smooth + filters.laplace(image_smooth, ksize=3)
        
        
        for ii in range(cell.shape[0]): #going through individual slice of one single cell:
            
            # this flag is used to tell what segmentation is used. 0 = histogram minima, 1 = triangle method
            flag = 0
            
            # finding threshold using the histogram function
            thresh_val, max_bg_val, max_obj_val = find_optimal_thres(image_smooth[ii, :, :], DEPTH)
            
            if thresh_val == 0:
                #print('Histogram based segmentation failed, now try other segmentation method.') 
                flat = 1
                # reroute to another thresholding method
                img_bg = intensity_seg(image_smooth[ii, :, :])
                
            else: 
                img_thresh = image_smooth[ii, :, :] < thresh_val 
                
                # apply median filter to smooth the edge of the binary mask
                img = ndimage.median_filter(img_thresh, footprint=np.ones((MEDIAN_F,MEDIAN_F)))
                img = ~img
                
                # label and regionprop the mask to find out the largest object (i.e. the cell) in the mask
                img_labels = measure.label(img,connectivity=2)
                labels_stat = measure.regionprops(img_labels)         
                largest_idx = np.argmax([i.area for i in labels_stat])
                img_bg = img_labels == labels_stat[largest_idx].label
                
                # measure the bounding box of the cell to eliminate cells too close to the borders
                min_row, min_col, max_row, max_col = labels_stat[largest_idx].bbox
                if min_row == 0 or min_col == 0 or max_row == img_bg.shape[0] or max_col == img_bg.shape[1]:
                    #print('Segmented area is too close to the image border. Try other segmentation method.')
                    flag = 1
                    img_bg = intensity_seg_str(image_smooth[ii, :, :])
                
                else:   
                    # fill holes and close the binary mask
                    img_bg = ndimage.morphology.binary_fill_holes(img_bg)    
                    img_bg_er_dil = binary_closing(img_bg, selem=SE)   
                    
                    # measure how many pixels where removed
                    diff_img = img_bg*1 - img_bg_er_dil*1
        
                    rem_pix = abs(sum(sum(diff_img)))
                    #print('Number of removed pixels: ' + str(rem_pix))
                    if rem_pix > tolerance:
                        #print('Histogram based segmentation removed too many pixels, now try other segmentation method.')
                        flag = 1
                        # reroute to another thresholding method because the first segmentation method failed
                        img_bg = intensity_seg(image_smooth[ii, :, :])
                    else:
                        img_bg = img_bg_er_dil
                        #compare change in area with previous frame
                        if abs(np.bincount(img_bg.flat)[1:] - labels_stat[0].area)/labels_stat[0].area > 0.5:
                            #print('Segmented area is 50% larger than that of the previous frame. Try other segmentation method.')
                            flag = 1
                            img_bg = intensity_seg(image_smooth[ii, :, :])

            cell_masks[ii] = img_bg #save the mask to the array created in the beginning

            # label and regionprops the binary masks to measure the properties of the cell (e.g. area)
            img_labels = measure.label(img_bg)
            labels_stat = measure.regionprops(img_labels)
            
            # whether to show the segmented image during the process. it is False by default to save memory
            if show_img:
                img_edge = measure.find_contours(img_bg, 0)            
                fig, axes = plt.subplots(ncols=1, nrows=1, figsize=(6, 5))
                plt.tight_layout()
                axes.axis('off')
                axes.imshow(cell[ii,:,:], cmap=plt.cm.gray)
                for acontour in img_edge:
                    axes.add_patch(patches.Polygon(acontour[:, [1, 0]], linewidth=2, edgecolor='r', facecolor='none'))      
                    # whether to save the contour overlay. by default, it will create a folder cell contours in the same directory
                    # as the script and save all the images as png
                    if save_contour:                        
                        results_dir = os.path.join(save_destination, 'Cell Contours/' + filename + '/cell_' + str(kk) + '/')
                        if not os.path.isdir(results_dir):
                            os.makedirs(results_dir)
                        plt.savefig(results_dir + filename + '_cell_' + str(kk) + '_' + str(ii) + '.png', transparent=True, dpi=150, bbox_inches='tight', pad_inches = 0)
                    plt.show()
            if flag == 0:
                print('Cell segmentation progress: ' + str(ii+1) + '/' + str(cell.shape[0]) + '  Segmentation method: Histogram minima')
            else:
                print('Cell segmentation progress: ' + str(ii+1) + '/' + str(cell.shape[0]) + '  Segmentation method: Triangle method')
            
            if labels_stat == []:
                print('no cells are identified.')
                cell_props.append(0)

            else:
                largest_idx = np.argmax([aCell.area for aCell in labels_stat])                    
                cell_props.append(labels_stat[largest_idx])

        all_cell_masks.append(cell_masks) 
        all_cell_props.append(cell_props)
    return all_cell_masks, all_cell_props
