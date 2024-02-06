# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 14:45:59 2023

@author: Mason
"""
import os

directories = [r"C:\Users\Mason\Desktop\flowCytometerCounter\Datasets\labels\test",
               r"C:\Users\Mason\Desktop\flowCytometerCounter\Datasets\labels\train",
               r"C:\Users\Mason\Desktop\flowCytometerCounter\Datasets\labels\val"]


sumW = 0
sumH = 0
num = 0
counts = {}
for directory in directories:
    count = 0
    for txt in os.listdir(directory):
        searchStart = 0
        
        boxInDir = os.path.join(directory, txt)
        
        with open(boxInDir, "r") as file:
           boxes = file.readlines()
        open(boxInDir, 'w').close()
        
        for box in boxes:
            scBoxR = box.replace('\n', '').split(' ')
            
            line = [int(scBoxR[0]), float(scBoxR[1]), float(scBoxR[2]), float(scBoxR[3]), float(scBoxR[4])]
            sumH += line[4]
            sumW += line[3]
            num += 1
            if line[3] < 0.005 or line[4] < .09:
                count += 1
            else:
                if int(box[0]) == 3:
                     out = '2' + box[1:]
                else:
                    out = box
                with open(boxInDir, "a") as w:
                    w.write(out)
    counts[directory.split('\\')[-1]] = count
print("Average W, H:", sumW/num, sumH/num)

print(counts)