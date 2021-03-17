# -*- coding: utf-8 -*-
"""
This is the GUI for cell spreading analysis.
Simply click Run to initial the GUI.

By Ernest Dec 2020
"""

import PySimpleGUI as sg
import os.path
import re
from skimage import io
from cell_spreading_gui_version import cell_spreading
from kymographs_generator_gui_version import kymo_generator

tab1_layout = [


    [sg.Text("Image location", font=('Arial', 11))],

    [sg.In(size=(30, 1), enable_events=True, key="-FOLDER1-"),

    sg.FileBrowse(target='-FOLDER1-', enable_events=True)],
    
    [sg.Text("Save data to", font=('Arial', 11))],
    
    [sg.In(size=(30, 1), enable_events=True, key="-FOLDER3-"),

    sg.FolderBrowse(target='-FOLDER3-', enable_events=True)],
    
    [sg.Text("Output settings:", font=('Arial', 12, 'bold'))],
        
    [sg.Checkbox('Save masks', default=False, key='-MASK-', font=('Arial', 11))],
        
    [sg.Checkbox('Export data', default=True, key='-DATA-', font=('Arial', 11))],
        
    [sg.Checkbox('Save contours', default=False, key='-CONTOUR-', font=('Arial', 11))],
    
    [sg.Text("Segmentation settings:", font=('Arial', 12, 'bold'))],
    
    [sg.Checkbox('Show segmentation (will take longer)', default=False, key='-SEG-', font=('Arial', 11))],
    
    [sg.Text('Smallest cell area (um^2): ', font=('Arial', 11)), sg.InputText(key='-CELL_SIZE-', size=(6, 1)), sg.Text(' (Try 33 um^2)', font=('Arial', 9))],
    
    [sg.Text("Image parameters:", font=('Arial', 12, 'bold'))],
    
    [sg.Text('Acquisition interval (s): ', font=('Arial', 11)), sg.InputText(key='-INTERVAL-', size=(5, 1))],
    
    [sg.Text('Pixel size (um): ', font=('Arial', 11)), sg.InputText(key='-PIXEL-', size=(5, 1))],
    
    [sg.Text('Image bit depth: ', font=('Arial', 11)), sg.Listbox(values=('8', '12', '16'), size=(2, 3), key='-BIT_DEPTH-', font=('Arial', 10))],
    
    [sg.Button("Run", key="-SUBMIT1-", enable_events=True, font=('Arial', 11)), sg.Button('Cancel', key="-CANCEL-", font=('Arial', 11))]

]

tab2_layout = [
    
    [sg.Text("Image location", font=('Arial', 11))],

    [sg.In(size=(30, 1), enable_events=True, key="-FOLDER2-"),

    sg.FileBrowse(target='-FOLDER2-', enable_events=True)],  
    
    [sg.Text("Save data to", font=('Arial', 11))],
    
    [sg.In(size=(30, 1), enable_events=True, key="-FOLDER4-"),
     
     sg.FolderBrowse(target='-FOLDER4-', enable_events=True)],
    
    [sg.Text("Output settings:", font=('Arial', 12, 'bold'))],
    
    [sg.Checkbox('Export data', default=True, key='-DATA2-', font=('Arial', 11))],
    
    [sg.Text("Image parameters:", font=('Arial', 12, 'bold'))],
            
    [sg.Text('Acquisition interval (s): ', font=('Arial', 11)), sg.InputText(key='-INTERVAL2-', size=(5, 1))],
    
    [sg.Text('Pixel size (um): ', font=('Arial', 11)), sg.InputText(key='-PIXEL2-', size=(5, 1))],
    
    [sg.Text('Smallest cell area (um^2): ', font=('Arial', 11)), sg.InputText(key='-CELL_SIZE2-', size=(6, 1)), sg.Text(' (Try 33 um^2)', font=('Arial', 9))],
    
    [sg.Text('Image bit depth: ', font=('Arial', 11)), sg.Listbox(values=('8', '12', '16'), size=(2, 3), key='-BIT_DEPTH2-', font=('Arial', 10))],
    
    [sg.Button("Run", key="-SUBMIT2-", enable_events=True, font=('Arial', 11)), sg.Button('Cancel', key="-CANCEL-", font=('Arial', 11))]
     
    
]

# ----- Full layout -----

layout = [
    
    [sg.TabGroup([[sg.Tab('Cell spread area', tab1_layout), sg.Tab('Kymograph generator & analysis', tab2_layout)]])],

    

    [sg.Text("Last updated by Ernest in Mar, 2021", justification='right', font=('Arial', 9), size=(52, 1))]
    

]


window = sg.Window("Cell Spreading Analysis", layout, font=("Arial", 12))


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
            save_data = values['-DATA2-']
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

