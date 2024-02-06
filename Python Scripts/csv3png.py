# -*- coding: utf-8 -*-
"""
Converts csv files to graphed png files

This uses a system of plotting smaller sections and then stitching them together
These large images are useful for tagging since it can all be done in one push
which is nice

For inference save the temp images instead of the whole images

Created on Tue Jun  6 16:08:44 2023

@author: Mason
"""

import numpy as np
import pandas as pd

from PIL import Image

from matplotlib import pyplot as plt
from matplotlib import transforms

import os

#Setup variables
#Number of points per graph
SPLIT_NUMBER = 5000

global ROOT_DIR, TEMP_DIR, OUT_DIR

#Directories to pull and save data
#CSV location
ROOT_DIR = r"C:\Users\Mason\Desktop\flowCytometerCounter\RAWDATA"
#Save temporary png files generated before stitching
TEMP_DIR = r"C:\Users\Mason\Desktop\flowCytometerCounter\TEMP_IMAGES"
#Final image out directory
OUT_DIR  = r"C:\Users\Mason\Desktop\flowCytometerCounter\IMAGES"


#A list of temporary file names to save each axis to
TEMP_FILE_NAMES = []
for m in range(60):
    TEMP_FILE_NAMES.append(os.path.join(TEMP_DIR, "TEMP" + str(m) + ".png"))

#Prompt user for directories if left blank, useful for sharing the code
if ROOT_DIR == "":
    ROOT_DIR = input("LOCATION OF CSV FILES: ")
if TEMP_DIR == "":
    TEMP_DIR = input("LOCATION TO SAVE TEMP FILE: ")
if OUT_DIR == "":
    OUT_DIR = input("LOCATION TO SAVE IMAGE FILES: ")

#The big man himself
def convert(filename):
    #Creates paths from directories listed above and appends filenames
    OUT_FILE = os.path.join(OUT_DIR, filename)
    
    OUT_FILE = OUT_FILE.replace("csv", "png")
    
    #Creates full dataframe from csv
    df = pd.read_csv(os.path.join(ROOT_DIR, filename),names = ["Time", "Amps"])
    dfSize = len(df)
    
    #Splits into chunks based on SPLIT_NUMBER
    numSplits = dfSize//SPLIT_NUMBER + 1
    splitDFs = []
    for i in range(numSplits - 1):
        splitDFs.append(df.iloc[i*SPLIT_NUMBER:(i+1)*SPLIT_NUMBER, :])
        
    #Appends split dataframes to a list of the dataframes for easy access to each
    splitDFs.append(df.iloc[(numSplits-1)*SPLIT_NUMBER:, :])
    print(numSplits, len(splitDFs))
    '''
    If they only have one split the data tends to get too small to be useful after the filler data appending, I'm not sure why this occurs
    only for the less than one splt. I think it has to do with how fast the particles come in the peaks tend to become very narrow and
    Unusable if the excess data is added in. Temporary fix.
    '''

    previousTime = int(splitDFs[-1]['Time'].iloc[-1])

    populateRows = []
    for k in range(SPLIT_NUMBER - len(splitDFs[-1])):
        previousTime += splitDFs[-1]['Time'].diff().mean()
        populateRows.append({'Time' : previousTime, 'Amps' : 0})

    splitDFs[-1] = pd.concat([splitDFs[-1], pd.DataFrame(populateRows)])
    #Create a figure of the appropriate size for the number of graphs
    
    for l in range(numSplits):
        fig, ax = plt.subplots(figsize=(12, 6))
        #removes the margins making it easier to stitch back together
        ax.margins(x=0)
        #Turns off the axis, we don't need them and it makes it impossible to stitch together, could probably keep it in but I can't be bothered
        ax.axis('off')
        
        plt.ylim([-4.5, 4.5])
        #Plots the first dataframe Time vs Amps(amplitude in volts not current) as a black line with 0.3 size
        ax.plot(splitDFs[l].Time, splitDFs[l].Amps, 'k', linewidth = 0.3)
        #Gets the bounding box of the plot in pixels
        axBoxT = ax.get_tightbbox()
        #Converts the bounding box to inches using the defult DPI of matplotlib
        axBox = transforms.Bbox([[axBoxT.x0/100, axBoxT.y0/100],[axBoxT.x1/100, axBoxT.y1/100]])
        #Saves the bounding box to the temp name
        fig.savefig(TEMP_FILE_NAMES[l], bbox_inches=axBox)
        #Closes the fucking plot thank god I don't have to keep doing this manually
        plt.close()

    #Creates a new blank image with the width of each plot(They should all be the same size...) times the number of plots and then finds the height. Not sure what the tuple at the end does
    outputImage = Image.new('RGB', (int(numSplits * (axBoxT.x1-axBoxT.x0)), int(axBoxT.y1-axBoxT.y0)), (250, 250, 250))
    
    #Opens each temp image and copies it to the new image we just created
    for j in range(numSplits):
        with Image.open(TEMP_FILE_NAMES[j]) as im:
        
            w, h = im.size

            outputImage.paste(im, (int(j*(axBoxT.x1-axBoxT.x0)), 0))

    #Saves the stitched image as a PNG
    outputImage.save(OUT_FILE, "PNG")
    
#Does the loop

regenerate = input("Regenerate files?(ENTER to skip) ")

for file in os.listdir(ROOT_DIR):
    OUT_FILE = os.path.join(OUT_DIR, file)
    OUT_FILE = OUT_FILE.replace("csv", "png")
    if regenerate or not os.path.isfile(OUT_FILE):
        convert(file)
    
for image in os.listdir(TEMP_DIR):
    os.remove(os.path.join(TEMP_DIR, image))