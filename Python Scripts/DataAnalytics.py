# -*- coding: utf-8 -*-
"""
Simple counting algorithm for looking at the ammount of data we have
can also be converted to get a general peak count from an inference

Created on Fri Jun  9 15:21:00 2023

@author: Mason
"""
import os

DATA_DIR = "C:\\Users\\Mason\\Desktop\\flowCytometerCounter\\DATA"
rebound = 0
peak = 0
double_peak = 0
poly_peak = 0
for file in os.listdir(DATA_DIR):
    with open(os.path.join(DATA_DIR, file), 'r') as openFile:
        
        lines = openFile.readlines()
        print("NUM LINES:",len(lines))
        for i in range(len(lines)):
            x = int(lines[i][0])
            if x == 0:
                rebound += 1
            elif x == 1:
                peak += 1
            elif x == 2:
                double_peak += 1
            elif x == 3:
                poly_peak += 1

print("REBOUND PEAKS:", rebound)
print("SINGLE  PEAKS:", peak)
print("DOUBLE  PEAKS:", double_peak)
print("POLY    PEAKS:", poly_peak)

        