# -*- coding: utf-8 -*-
"""
Visualize relative pixel data on opencv2 screen
No scroll bar only use for small images

Created on Tue Jun 13 09:41:15 2023

@author: Mason
"""
import random, os, cv2
import numpy as np

IMAGE_DIR = r"C:\Users\Mason\Desktop\flowCytometerCounter\DETECTION_IMAGES"

imgFile1 = random.choice(os.listdir(IMAGE_DIR))
imgFile2 = random.choice(os.listdir(IMAGE_DIR))

img1 = cv2.imread(os.path.join(IMAGE_DIR, imgFile1))
img2 = cv2.imread(os.path.join(IMAGE_DIR, imgFile2))



cv2.rectangle(img1, (5, 29), (46, 43), (100, 100, 100), 2)
cv2.imshow('image', img1 * img2)
cv2.waitKey(0)
cv2.destroyAllWindows()
