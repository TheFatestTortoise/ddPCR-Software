# -*- coding: utf-8 -*-
"""
Splits data into train test and validation sets then moves them to the appropriate dataset

THIS SCRIPT PERMANENTLY MOVES FILES FROM BOX_IN_DIR AND IMG_IN_DIR to val, test, train files

Run autoSplit.py first to ensure there are files to move

Advised to clear files from train, val, test directories

Created on Tue Jun 13 10:34:01 2023

@author: Mason
"""
import random, shutil, os

TTVSPLIT_RATIOS = [20, 20, 60] #Must add to 100

def clearDir(fileDir, imgDir):
    files = os.listdir(fileDir)
    images = os.listdir(imgDir)
    
    for f in files:
        os.remove(os.path.join(fileDir, f))
    for i in images:
        os.remove(os.path.join(imgDir, i))


IMG_IN_DIR = r"C:\Users\Mason\Desktop\flowCytometerCounter\SPLIT_IMAGES"

BOX_IN_DIR   = r"C:\Users\Mason\Desktop\flowCytometerCounter\SPLIT_BOXES"

BOX_VAL = r"C:\Users\Mason\Desktop\flowCytometerCounter\Datasets\labels\val"
IMG_VAL = r"C:\Users\Mason\Desktop\flowCytometerCounter\Datasets\images\val"

BOX_TEST = r"C:\Users\Mason\Desktop\flowCytometerCounter\Datasets\labels\test"
IMG_TEST = r"C:\Users\Mason\Desktop\flowCytometerCounter\Datasets\images\test"

BOX_TRAIN = r"C:\Users\Mason\Desktop\flowCytometerCounter\Datasets\labels\train"
IMG_TRAIN = r"C:\Users\Mason\Desktop\flowCytometerCounter\Datasets\images\train"

clearFiles = input("Clear Files?(Enter to Skip)")

if clearFiles:
    confirmation = input("Are you sure?(Enter to skip)")
else:
    confirmation = False
    

if confirmation:
    print("Clearing directories")
    clearDir(BOX_VAL, IMG_VAL)
    clearDir(BOX_TEST, IMG_TEST)
    clearDir(BOX_TRAIN, IMG_TRAIN)

fileSplitCounts = [0, 0, 0]
for file in os.listdir(BOX_IN_DIR):
    image = file.replace("txt", "png")
    x = random.randrange(0, 100)
    
    if x < TTVSPLIT_RATIOS[0]:
        fileSplitCounts[0] += 1
        shutil.move(os.path.join(BOX_IN_DIR, file), os.path.join(BOX_VAL, file))
        shutil.move(os.path.join(IMG_IN_DIR, image), os.path.join(IMG_VAL, image))
    elif x < (TTVSPLIT_RATIOS[0] + TTVSPLIT_RATIOS[1]):
        fileSplitCounts[1] += 1
        shutil.move(os.path.join(BOX_IN_DIR, file), os.path.join(BOX_TEST, file))
        shutil.move(os.path.join(IMG_IN_DIR, image), os.path.join(IMG_TEST, image))
    else:
        fileSplitCounts[2] += 1
        shutil.move(os.path.join(BOX_IN_DIR, file), os.path.join(BOX_TRAIN, file))
        shutil.move(os.path.join(IMG_IN_DIR, image), os.path.join(IMG_TRAIN, image))

print("", fileSplitCounts[0], "Validation files\n", fileSplitCounts[1], "Test files\n", fileSplitCounts[2], "Training Files\n", sum(fileSplitCounts), "Total Files Allocated")