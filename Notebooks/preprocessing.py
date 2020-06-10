# -*- coding: utf-8 -*-
"""preprocessing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mnUCk_DtwG1iISjhWukffiyc2G0pXrUL
"""

pip install pydicom

import argparse
import os
import scipy.misc
import numpy as np
import os
import tensorflow as tf
import time
from glob import glob
import numpy as np
from six.moves import xrange
import scipy.io
from scipy import sparse
import math as m
# astra image recon related importsimport time
import scipy.sparse.linalg
import scipy.io
from glob import glob
import pylab
from sklearn.feature_extraction import image
import numbers
from scipy import sparse
from numpy.lib.stride_tricks import as_strided
from itertools import product
from decimal import Decimal
from sklearn.metrics import mean_squared_error as immse
import matplotlib.pyplot as plt

# new imports
import sys
import matplotlib.pyplot as plt
from numpy import linspace, pi, sin
import tensorflow as tf
import numpy as np
# from skimage.io import imread
# from skimage import data_dir
# from skimage.morphology import disk, erosion, dilation
from scipy.interpolate import griddata
from scipy import interpolate
import h5py
from scipy import sparse
import tables, warnings

from google.colab import drive
drive.flush_and_unmount()

import numpy as np
import cv2
import pydicom
import os
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.transform import radon, rescale
from skimage import morphology
from skimage import measure
from skimage import filters
from google.colab import drive
from google.colab.patches import cv2_imshow
drive.mount('/content/drive/')

"""# Save Sinogram of Image Without Metal Artifact"""

path = '/content/drive/My Drive/Main Project Dataset/True Image'
sliceses = [pydicom.dcmread(path + '/' + s,force=True) for s in os.listdir(path)]
#slices.sort(key = lambda x: int(x.InstanceNumber))
try:
    slice_thickness = np.abs(sliceses[0].ImagePositionPatient[2] - sliceses[1].ImagePositionPatient[2])
except:
    slice_thickness = np.abs(sliceses[0].SliceLocation - sliceses[1].SliceLocation)
    
for s in sliceses:
    s.SliceThickness = slice_thickness
for s in sliceses:
    s.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian

sli = get_pixels_hu(sliceses)    
sino_image = []

print(sli[0].shape)

for s in sli:
    image=s
   # image = rescale(image, scale=1, mode='reflect', multichannel=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))

    ax1.set_title("Original")
    ax1.imshow(image, cmap=plt.cm.Greys_r, interpolation='none')

    theta = np.linspace(0., 180., 512, endpoint=False)
    sinogram = radon(image, theta=theta, circle=True)
    sino_image.append(sinogram)
    ax2.set_title("Sinogram\n(Radon Transform)")
    ax2.set_xlabel("Projection angle (deg)")
    ax2.set_ylabel("Projection position (pixels)")
    ax2.imshow(sinogram, cmap=plt.cm.Greys_r, 
              extent=(0, 180, 0, sinogram.shape[0]), aspect='auto')

    fig.tight_layout()
    plt.show()

for k in range(72):
  min=sino_image[k].min()
  max=sino_image[k].max()
  for i in range(512):
      for j in range(512):
          sino_image[k][i][j]=(((sino_image[k][i][j]-min)/(max-min))*(255))

import scipy.io as sio

path = '/content/drive/My Drive/Main Project Dataset/True Sinogram/'
for i in range(72):
    sio.savemat(path + str(i) + '.mat',{'sino': sino_image[i]})

"""# Save Sinogram of Images With Metal Artifact Removed"""

path = '/content/drive/My Drive/Main Project Dataset/Metal Artifacts'
slices = [pydicom.dcmread(path + '/' + s,force=True) for s in os.listdir(path)]
#slices.sort(key = lambda x: int(x.InstanceNumber))
try:
    slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
except:
    slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    
for s in slices:
    s.SliceThickness = slice_thickness
for s in slices:
    s.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian

slic = get_pixels_hu(slices)    
sino_image_metal = []

#print(slic[0].shape)
i=0
j=0
for s in slic:
    print(j)
    j=j+1
    image=s
   # image = rescale(image, scale=1, mode='reflect', multichannel=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))

    ax1.set_title("Original")
    ax1.imshow(image, cmap=plt.cm.Greys_r, interpolation='none')

    theta = np.linspace(0., 180., 512, endpoint=False)
    sinogram = radon(image, theta=theta, circle=True)
    sino_image_metal.append(sinogram)
    ax2.set_title("Sinogram\n(Radon Transform)")
    ax2.set_xlabel("Projection angle (deg)")
    ax2.set_ylabel("Projection position (pixels)")
    #ax2.imshow(sli[i], cmap=plt.cm.Greys_r, interpolation='none')
    ax2.imshow(sinogram, cmap=plt.cm.Greys_r, 
              extent=(0, 180, 0, sinogram.shape[0]), aspect='auto')
    #i=i+1
    fig.tight_layout()
    plt.show()

"""# Check"""

print(slic[0].min(),slic[0].max())
print(sino_image_metal[0].min(),sino_image_metal[0].max())

for k in range(72):
  min=sino_image_metal[k].min()
  max=sino_image_metal[k].max()
  for i in range(512):
      for j in range(512):
          sino_image_metal[k][i][j]=(((sino_image_metal[k][i][j]-min)/(max-min))*(255))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))

ax1.imshow(sino_image_metal[1], cmap=plt.cm.Greys_r, 
          extent=(0, 180, 0, sino_image_metal[1].shape[0]), aspect='auto')
ax2.set_title("Sinogram\n(Radon Transform)")
ax2.set_xlabel("Projection angle (deg)")
ax2.set_ylabel("Projection position (pixels)")
ax2.imshow(sino_image_metal[0], cmap=plt.cm.Greys_r, 
          extent=(0, 180, 0, sino_image_metal[0].shape[0]), aspect='auto')

fig.tight_layout()
plt.show()

"""# Save Normalised Uncorrected Sinogram"""

import scipy.io as sio
path = '/content/drive/My Drive/Main Project Dataset/Uncorrected Sinogram/'
for i in range(72):
    sio.savemat(path + str(i) + '.mat',{'un_sino': sino_image_metal[i]})

"""# Function to Convert to Hu Units"""

def get_pixels_hu(scans):
    for s in scans:  
       image = np.stack([s.pixel_array for s in scans])
    # Convert to int16 (from sometimes int16), 
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 1
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0
    
    # Convert to Hounsfield units (HU)
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope
    
    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)
        
    image += np.int16(intercept)
    
    return np.array(image, dtype=np.int16)

#slice = get_pixels_hu(slices)

"""# Remove Metal and Generate Metal Sinogram"""

from skimage.morphology import disk, erosion, dilation
thresh_slices = []
metal = []
sino_metal=[]
for s in slic:
    temp = s
    #(T, thresh) = cv2.threshold(temp, 4000, 255, cv2.THRESH_TOZERO)
    #thresh = rescale(thresh, scale=1, mode='reflect', multichannel=False)
    metals = temp > 3000
    eroded = erosion(metals, disk(2)) #eroding
    dilated = dilation(eroded, disk(4)) # dilating
    thresh = dilated > 0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))
    ax1.set_title("Metal Only Image")
    ax1.imshow(thresh, cmap=plt.cm.Greys_r, interpolation='none')
    theta = np.linspace(0., 180., 512, endpoint=False)
    sinogram = radon(thresh, theta=theta, circle=True)
    #mask = (sinogram > 0).astype(np.double)
    metal.append(thresh)
    sino_metal.append(sinogram)
    ax2.set_title("Metal Sinogram")
    ax2.set_xlabel("Projection angle (deg)")
    ax2.set_ylabel("Projection position (pixels)")
    ax2.imshow(sinogram, cmap=plt.cm.Greys_r, 
              extent=(0, 180, 0, sinogram.shape[0]), aspect='auto')
    fig.tight_layout()
    plt.show()

"""**Check**"""

print(metal[0].min(),metal[0].max())
print(sino_metal[0].min(),sino_metal[0].max())

for k in range(72):
    max=sino_metal[0].max()
    min=sino_metal[0].min()

    for i in range(512):
        for j in range(512):
            sino_metal[k][i][j]=(((sino_metal[k][i][j]-min)/(max-min))*(255))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))

ax1.imshow(sino_metal[1], cmap=plt.cm.Greys_r, 
          extent=(0, 180, 0, sino_metal[1].shape[0]), aspect='auto')
ax2.set_title("Sinogram\n(Radon Transform)")
ax2.set_xlabel("Projection angle (deg)")
ax2.set_ylabel("Projection position (pixels)")
ax2.imshow(sino_metal[0], cmap=plt.cm.Greys_r, 
          extent=(0, 180, 0, sino_metal[0].shape[0]), aspect='auto')

fig.tight_layout()
plt.show()

import scipy.io as sio
path = '/content/drive/My Drive/Main Project Dataset/Metal Only Sinogram/'
for i in range(72):
    sio.savemat(path + str(i) + '.mat',{'thresh_sino': sino_metal[i]})

"""# Subtraction"""

#new_sino = []
#for (s,y) in zip(sino,thresh_sino):
#    new_sino.append(s-y)
sino_no_metal=[]
for i in range(0,72):
   # print(sino[i].min())
    #print(thresh_sino[i].min())

    #print(sino[i].max())
    #print(thresh_sino[i].max())
    mask = (sino_metal[i] > 0).astype(np.double)        
    #print(mask)
    new_sino = (1-mask) * sino_image_metal[i]

    #for k in range(512):
     #   for j in range(512):
      #    if new_sino[k][j]==new_sino.max():
       #          new_sino[k][j]=new_sino.min()
    
   # print(new_sino.min())
    #print(new_sino.max())
    
    #--new_sino = sino_image_metal[i] - sino_metal[i]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))

    ax1.set_title("Original Sinogram")
    ax1.set_xlabel("Projection angle (deg)")
    ax1.set_ylabel("Projection position (pixels)")
    ax1.imshow(sino_image_metal[i], cmap=plt.cm.Greys_r, 
              extent=(0, 180, 0, sino_image_metal[i].shape[0]), aspect='auto')
    ax2.set_title("Sinogram after Metal Deletion")
    ax2.set_xlabel("Projection angle (deg)")
    ax2.set_ylabel("Projection position (pixels)")
    ax2.imshow(new_sino, cmap=plt.cm.Greys_r, 
              extent=(0, 180, 0, new_sino.shape[0]), aspect='auto')
    fig.tight_layout()
    plt.show()
    
    sino_no_metal.append(new_sino)
   # new_sino = np.expand_dims(np.expand_dims(new_sino,axis=0),axis=3)
  # completed_sino = completeSinogram(model,incomplete_sino_padded)

print(sino_image_metal[0].min(),sino_image_metal[0].max())
print(sino_no_metal[0].min(),sino_no_metal[0].max())

import scipy.io as sio

path = '/content/drive/My Drive/Main Project Dataset/Metal Deleted Sinogram/'
for i in range(72):
    sio.savemat(path + str(i) + '.mat',{'new_sino': sino_no_metal[i]})

"""**Simulated Dataset**"""

path = '/content/drive/My Drive/Main Project Dataset/Training Image Set (New)'
sisl = [pydicom.dcmread(path + '/' + s,force=True) for s in os.listdir(path)]
#slices.sort(key = lambda x: int(x.InstanceNumber))
try:
    slice_thickness = np.abs(sisl[0].ImagePositionPatient[2] - sisl[1].ImagePositionPatient[2])
except:
    slice_thickness = np.abs(sisl[0].SliceLocation - sisl[1].SliceLocation)
    
for s in sisl:
    s.SliceThickness = slice_thickness
for s in sisl:
    s.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian

sl = get_pixels_hu(sisl)    
sino_sim = []

print(sl[0].shape)

for s in sl:
    image=s
   # image = rescale(image, scale=1, mode='reflect', multichannel=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))

    ax1.set_title("Original")
    ax1.imshow(image, cmap=plt.cm.Greys_r, interpolation='none')

    theta = np.linspace(0., 180., 512, endpoint=False)
    sinogram = radon(image, theta=theta, circle=True)
    sino_sim.append(sinogram)
    ax2.set_title("Sinogram\n(Radon Transform)")
    ax2.set_xlabel("Projection angle (deg)")
    ax2.set_ylabel("Projection position (pixels)")
    ax2.imshow(sinogram, cmap=plt.cm.Greys_r, 
              extent=(0, 180, 0, sinogram.shape[0]), aspect='auto')

    fig.tight_layout()
    plt.show()

print(np.array(sino_sim).shape)

for k in range(233):
  min=sino_sim[k].min()
  max=sino_sim[k].max()
  for i in range(512):
      for j in range(512):
          sino_sim[k][i][j]=(((sino_sim[k][i][j]-min)/(max-min))*(255))

print(sino_sim[0].min(),sino_sim[0].max())

import scipy.io as sio
path = '/content/drive/My Drive/Main Project Dataset/Simulated Output/'
for i in range(72,305):
    sio.savemat(path + str(i) + '.mat',{'sino': sino_sim[i-72]})



"""***Generate Simulated Input***"""

#new_sino = []
#for (s,y) in zip(sino,thresh_sino):
#    new_sino.append(s-y)
sim_input=[]

for i in range(233):
   # print(sino[i].min())
    #print(thresh_sino[i].min())

    #print(sino[i].max())
    #print(thresh_sino[i].max())
    mask = (sino_metal[0] > 0).astype(np.double)        
    #print(mask)
    new_sino = (1-mask) * sino_sim[i]
    #new_sino=sino_sim[i]-sino_metal[0]
    #for k in range(512):
     #   for j in range(512):
      #    if new_sino[k][j]==new_sino.max():
       #          new_sino[k][j]=new_sino.min()
    
   # print(new_sino.min())
    #print(new_sino.max())
    
    #--new_sino = sino_image_metal[i] - sino_metal[i]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))

    ax1.set_title("Original Sinogram")
    ax1.set_xlabel("Projection angle (deg)")
    ax1.set_ylabel("Projection position (pixels)")
    ax1.imshow(sino_sim[i], cmap=plt.cm.Greys_r, 
              extent=(0, 180, 0, sino_sim[i].shape[0]), aspect='auto')
    ax2.set_title("Sinogram after Metal Deletion")
    ax2.set_xlabel("Projection angle (deg)")
    ax2.set_ylabel("Projection position (pixels)")
    ax2.imshow(new_sino, cmap=plt.cm.Greys_r, 
              extent=(0, 180, 0, new_sino.shape[0]), aspect='auto')
    fig.tight_layout()
    plt.show()
    
    sim_input.append(new_sino)



import scipy.io as sio
path = '/content/drive/My Drive/Main Project Dataset/Simulated Input/'
for i in range(72,305):
    sio.savemat(path + str(i) + '.mat',{'new_sino': sim_input[i-72]})



"""**Practice**"""

import scipy.io as sio
path = '/content/drive/My Drive/Main Project Dataset/simulated_project/sample_1.mat'
sample = sio.loadmat(path)
print(sample)
print(np.array(image).shape)
#image=np.reshape(image,(512,512,1))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))

ax1.set_title("Original Sinogram")
ax1.set_xlabel("Projection angle (deg)")
ax1.set_ylabel("Projection position (pixels)")
#ax1.imshow(image, cmap=plt.cm.Greys_r, interpolation='none')
ax2.set_title("Sinogram after Metal Deletion")
ax2.set_xlabel("Projection angle (deg)")
ax2.set_ylabel("Projection position (pixels)")
#ax2.imshow(image, cmap=plt.cm.Greys_r, interpolation='none')
fig.tight_layout()
plt.show()

