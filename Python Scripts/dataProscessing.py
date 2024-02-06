# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 12:22:22 2023

@author: Mason
"""

import pandas as pd
from os import path
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from FileDetection import detect
import numpy as np
matplotlib.use('TkAgg')

CWD_DIR = path.dirname(os.getcwd())
DATA_DIR = path.join(CWD_DIR, "RAWDATA")

N_NNErrPpm = []
N_CErrPpm = []
N_NNMissPpm = []
N_CMissPpm = []
N_Ccounts = []
N_NNcounts = []

O_NNErrPpm = []
O_CErrPpm = []
O_NNMissPpm = []
O_CMissPpm = []
O_Ccounts = []
O_NNcounts = []

files = []


while True:
    plt.close('all')
    matplotlib.use('TkAgg')
    fig, ax = plt.subplots(3)
    plt.ion()
    
    
    O_NNErrPpm.extend(N_NNErrPpm)
    O_CErrPpm.extend(N_CErrPpm)
    O_NNMissPpm.extend(N_NNMissPpm)
    O_CMissPpm.extend(N_CMissPpm)
    O_Ccounts.extend(N_Ccounts)
    O_NNcounts.extend(N_NNcounts)
    
    N_NNErrPpm = []
    N_CErrPpm = []
    N_NNMissPpm = []
    N_CMissPpm = []
    N_Ccounts = []
    N_NNcounts = []

    data = pd.read_excel(path.join(CWD_DIR, 'Data Collection.xlsx'), usecols = 'A:D')

    for index, row in data.iterrows():
        file = row[0]
        if file not in files:
            NN_count = row[1]
            Corrected_count = row[2]
            Slide_count = row[3]
            filePath = path.join(DATA_DIR, file)
            filePath = filePath + ".csv"
            if path.isfile(filePath):
                print(file, NN_count, Corrected_count, Slide_count)

                df = pd.read_csv(filePath, names = ["Time", "Amps"])
                ppm = Slide_count/(df["Time"].iloc[-1] / 60000)
                N_NNErrPpm.append((ppm, abs(NN_count - Slide_count) * 100 / Slide_count))
                N_CErrPpm.append((ppm, abs(Corrected_count - Slide_count) * 100 / Slide_count))
                N_NNMissPpm.append((ppm, Slide_count - NN_count))
                N_CMissPpm.append((ppm, Slide_count - Corrected_count))
                
                N_Ccounts.append((np.log(Slide_count), np.log(Corrected_count)))
                N_NNcounts.append((np.log(Slide_count), np.log(NN_count)))
                files.append(file)
    
    if len(N_NNcounts) > 0 and len(N_Ccounts) > 0:
        ax[0].scatter(*zip(*N_NNcounts), c = '#fc039d')
        ax[0].scatter(*zip(*N_Ccounts), c = '#03a9fc')
    if len(O_NNcounts) > 0 and len(O_Ccounts) > 0:
        ax[0].scatter(*zip(*O_NNcounts), c = '#fc0314')
        ax[0].scatter(*zip(*O_Ccounts), c = '#7b03fc')
    
    lims = [np.min([ax[0].get_xlim(), ax[0].get_ylim()]),
            np.max([ax[0].get_xlim(), ax[0].get_ylim()])]
    ax[0].plot(lims, lims, 'k-')
    #ax[0].set_aspect('equal')
    ax[0].set_xlim(lims)
    ax[0].set_ylim(lims)
    ax[1].yaxis.set_major_formatter(mtick.PercentFormatter())
    if len(N_NNErrPpm) > 0 and len(N_CErrPpm) > 0:
        ax[1].scatter(*zip(*N_NNErrPpm), c = '#fc039d')
        ax[1].scatter(*zip(*N_CErrPpm), c = '#03a9fc')
    if len(O_NNErrPpm) > 0 and len(O_CErrPpm) > 0:
        ax[1].scatter(*zip(*O_NNErrPpm), c = '#fc0314')
        ax[1].scatter(*zip(*O_CErrPpm), c = '#7b03fc')
        
    if len(N_NNMissPpm) > 0 and len(N_CMissPpm) > 0:
        ax[2].scatter(*zip(*N_NNMissPpm), c = '#fc039d')
        ax[2].scatter(*zip(*N_CMissPpm), c = '#03a9fc')
    if len(O_NNMissPpm) > 0 and len(O_CMissPpm) > 0:
        ax[2].scatter(*zip(*O_NNMissPpm), c = '#fc0314')
        ax[2].scatter(*zip(*O_CMissPpm), c = '#7b03fc')
        
    plt.show()
    plt.pause(0.001)
    
    x = input("r to refresh, q to quit: ")
    
    if (x == 'q'):
        plt.close('all')
        break
    elif (x == 'r'):
        print('Converting')
        detect(r'yolov5\runs\train\PeakDetection-6-28-234\weights\best.pt')