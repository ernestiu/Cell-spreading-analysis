# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 13:21:43 2020

@author: ernes
"""

import PySimpleGUI as sg
import os.path
import re
from skimage import io
from cell_spreading_gui_version import cell_spreading
from kymographs_generator_gui_version import kymo_generator

tab1_layout = [

#image_params_column = [

    [sg.Text("Image location")],

    [sg.In(size=(25, 1), enable_events=True, key="-FOLDER1-"),

    sg.FileBrowse(target='-FOLDER1-', enable_events=True)],
    
    [sg.Text("Data save to")],
    
    [sg.In(size=(25, 1), enable_events=True, key="-FOLDER3-"),

    sg.FolderBrowse(target='-FOLDER3-', enable_events=True)],
    
    [sg.Text("Segmentation settings:")],
        
    [sg.Checkbox('Save masks', default=False, key='-MASK-')],
        
    [sg.Checkbox('Export data', default=True, key='-DATA-')],
         
    [sg.Checkbox('Show segmentation (will take longer)', default=False, key='-SEG-')],
        
    [sg.Checkbox('Save contours', default=False, key='-CONTOUR-')],
    
    [sg.Text("Image parameters:")],
    
    [sg.Text('Acquisition interval (s): '), sg.InputText(key='-INTERVAL-', size=(5, 1))],
    
    [sg.Text('Pixel size (um): '), sg.InputText(key='-PIXEL-', size=(5, 1))],
    
    [sg.Text('Smallest cell area (um^2): '), sg.InputText(key='-CELL_SIZE-', size=(6, 1)), sg.Text(' (Try 33 um^2)')],
    
    [sg.Text('Image bit depth: '), sg.Listbox(values=('8', '12', '16'), size=(3, 3), key='-BIT_DEPTH-')],
    
    [sg.Button("Run", key="-SUBMIT1-", enable_events=True), sg.Button('Cancel', key="-CANCEL-")]

]

tab2_layout = [
    
    [sg.Text("Image location")],

    [sg.In(size=(25, 1), enable_events=True, key="-FOLDER2-"),

    sg.FileBrowse(target='-FOLDER2-', enable_events=True)],  
    
    [sg.Text("Data save to")],
    
    [sg.In(size=(25, 1), enable_events=True, key="-FOLDER4-"),
     
     sg.FolderBrowse(target='-FOLDER4-', enable_events=True)],
    
    [sg.Text("Settings:")],
    
    [sg.Checkbox('Export data', default=True, key='-DATA-')],
            
    [sg.Text('Acquisition interval (s): '), sg.InputText(key='-INTERVAL2-', size=(5, 1))],
    
    [sg.Text('Pixel size (um): '), sg.InputText(key='-PIXEL2-', size=(5, 1))],
    
    [sg.Text('Smallest cell area (um^2): '), sg.InputText(key='-CELL_SIZE2-', size=(6, 1)), sg.Text(' (Try 33 um^2)')],
    
    [sg.Text('Image bit depth: '), sg.Listbox(values=('8', '12', '16'), size=(3, 3), key='-BIT_DEPTH2-')],
    
    [sg.Button("Run", key="-SUBMIT2-", enable_events=True), sg.Button('Cancel', key="-CANCEL-")]
     
    
]

# ----- Full layout -----

layout = [
    
    [sg.TabGroup([[sg.Tab('Cell spread area', tab1_layout), sg.Tab('Kymograph generator & analysis', tab2_layout)]])],
    #[sg.Column(image_params_column)],
    

    [sg.Text("by Ernest in 2020", justification='right')]

]


window = sg.Window("Cell Spreading Analysis", layout, font=("Helvetica", 12))


# Run the Event Loop

while True:

    event, values = window.read()
        
    if event in (sg.WIN_CLOSED, '-CANCEL-'):
        
        break

    if event == "-FOLDER1-":

        filepath = values["-FOLDER1-"]
    
    if event == "-FOLDER2-":
        
        filepath = values["-FOLDER2-"]
        
    if event in "-SUBMIT1-": 
        
        try:
            image = io.imread(filepath)
            fname = os.path.basename(filepath)
            fname = re.sub('.tif', '', fname)
            print(fname)
            save_masks = values['-MASK-']
            print(save_masks)            
            save_data = values['-DATA-']
            print(save_data)
            show_img = values['-SEG-']
            save_contour = values['-CONTOUR-']
            print(save_contour)
            if save_contour == True:
                show_img = True
            interval = int(values['-INTERVAL-'])
            print(interval)            
            pixel_size = float(values['-PIXEL-'])
            print(pixel_size)
            try:
                small_obj = int(float(values['-CELL_SIZE-'])/pixel_size**2)
                print(small_obj)
            except:
                small_obj = 1000
                print('Default smallest cell size was used.')
            bit_depth = int(values['-BIT_DEPTH-'][0])
            print(bit_depth)  
            save_destination = values['-FOLDER3-']    
            cell_spreading(image, fname, save_masks, save_data, save_contour, show_img, interval, pixel_size, bit_depth, small_obj, save_destination)
        
        except:
            print('Error')
            
    
    if event in "-SUBMIT2-": 

        try:       
            image = io.imread(filepath)
            fname = os.path.basename(filepath)
            fname = re.sub('.tif', '', fname)
            print(fname)        
            save_data = values['-DATA-']
            print(save_data)
            interval = int(values['-INTERVAL2-'])
            print(interval)            
            pixel_size = float(values['-PIXEL2-'])
            print(pixel_size)       
            # small_obj = int(float(values['-CELL_SIZE2-'])/pixel_size**2)
            # print(small_obj)
            try:
                small_obj = int(float(values['-CELL_SIZE2-'])/pixel_size**2)
                print(small_obj)
            except:
                small_obj = 1000
                print('Default smallest cell size was used.')
            bit_depth = int(values['-BIT_DEPTH2-'][0])
            print(bit_depth)  
            save_destination = values['-FOLDER4-']
            kymo_generator(image, fname, save_data, interval, pixel_size, bit_depth, small_obj = small_obj, save_destination = save_destination)
            
        except:
            print('Error')

window.close()

