from audioop import minmax
from fileinput import filename
from logging import exception
# from nis import cat
import os
from turtle import left
import cv2
from re import search
from cv2 import NORM_TYPE_MASK

import pydicom
import numpy as np

input_path = "D:\Test" 
output_path = "D:\Test_output"

l = 0.01
r = 0.01
u = 0.04
d = 0.04
thresh = 0.1
maxval = 1.0
ksize = 23
operation = "open"
reverse = True
top_x = 1
clip = 2.0
tile = 8

def cropBorders(img):
    try:
        nrows, ncols = img.shape
        #print(f'Before {img.shape}')
        l_crop = int(ncols * l)
        r_crop = int(ncols * (1 - r))
        u_crop = int(nrows * u)
        d_crop = int(nrows * (1 - d))
        
        return img[u_crop:d_crop, l_crop:r_crop]       

    except Exception as e:
        print("Unable to crop")

def minMaxNormalize(img):
    try: 
        return (img - img.min()) / (img.max() - img.min())      
    except:
        print("unable to normalize")

def globalBinarise(img):
    try:
        binarised_img = np.zeros(img.shape, np.uint8)
        binarised_img[img >= thresh] = maxval
        return binarised_img 

    except:
        print(' Unable to globalBinarise')

def edit_mask(img):
    try:
        kernel = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(23,23))

        if operation == "open":
            edited_mask = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        elif operation == "close":
            edited_mask = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

        edited_mask = cv2.morphologyEx(edited_mask, cv2.MORPH_DILATE, kernel)

        #print(edited_mask)

        return edited_mask        

    except Exception as ex:
        print(f'Unable to edit mask {ex}')


def sortContoursByArea(contours, reverse=True):
    try:
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=reverse)

        bounding_boxes = [cv2.boundingRect(c) for c in sorted_contours]
        return sorted_contours, bounding_boxes

    except:
        print('Unable to sort contour area')

def xLargestBlobs(mask, top_x=None, reverse=True):
    try:
        contours, hierarachy = cv2.findContours(image=mask, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)

        n_contours = len(contours)

        if n_contours > 0:
           
            if n_contours < top_x or top_x == None:
                top_x = n_contours

            sorted_contours, bounding_boxes = sortContoursByArea(
                contours=contours, reverse=reverse
            )

            X_largest_contours = sorted_contours[0:top_x]

            to_draw_on = np.zeros(mask.shape, np.uint8)

            X_largest_blobs = cv2.drawContours(
                image=to_draw_on,  
                contours=X_largest_contours, 
                contourIdx=-1,  
                color=1,  
                thickness=-1,  
            )
            return n_contours, X_largest_blobs
    except Exception as ex:
        print(f"Error in finding xLargest Blobs {ex}")

def applyMask(img, mask):
    try:
      masked_img = img.copy()
      masked_img[mask == 0] = 0
      return masked_img
    except:
        print("Error processing applyMask")

def checkLRFlip(mask):
    try:
        _, ncols = mask.shape
        x_center = ncols // 2         

        col_sum = mask.sum(axis=0)

        left_sum = sum(col_sum[0:x_center])
        right_sum = sum(col_sum[x_center:-1])

        return True if left_sum < right_sum else False 

    except:
        print("Error in checking LR Flip")

def makeLRFlip(img):
    try:
       return np.fliplr(img)
    except Exception as ex:
        print("Failed to flip LR")

def clahe(img):
    try:
        img = cv2.normalize(img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        img_uint8 = img.astype("uint8")
        
        clahe_create = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
        return clahe_create.apply(img_uint8)
    except Exception as ex:
        print("Failed to clahe")

def pad(img):
    try:
        nrows, ncols = img.shape 
        if nrows != ncols:
            target_shape = (nrows, nrows) if ncols < nrows else (ncols, ncols) 
            padded_img = np.zeros(shape=target_shape) 
            padded_img[:nrows, :ncols] = img            
            return padded_img
    except Exception as e:
        print((f"Unable to pad!\n{e}"))

def fullMammoPreprocess(img):    
    crop_img = cropBorders(img)
    norm_img = minMaxNormalize(crop_img)
    binarised_img = globalBinarise(norm_img)
    edited_mask = edit_mask(binarised_img) 
    _, xlargest_mask = xLargestBlobs(edited_mask,top_x, reverse)
    masked_img = applyMask(img=norm_img, mask=xlargest_mask)

    lr_flip = checkLRFlip(mask=xlargest_mask)
    if checkLRFlip(mask=xlargest_mask):
        flipped_img = makeLRFlip(masked_img)
    else:
        flipped_img = masked_img
    
    clahe_img = clahe(flipped_img)
    padded_img = pad(img=clahe_img)
    padded_img = cv2.normalize(padded_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    img_pre =minMaxNormalize(img=padded_img)
    return img_pre, lr_flip

def maskPreprocess(mask, lr_flip):
    mask = cropBorders(mask)
    if lr_flip:
        mask = makeLRFlip(mask)
    return pad(mask)
    

def process_images():
    dcm_path = []
    fullmamm_path = []
    maskmamm_path = []
    crop_path = []
    for dir, _, files in os.walk(input_path):
        files.sort()
        i = 0
        for f in files:
            if f.endswith(".dcm"):
                dcm_path.append(os.path.join(dir, f))  
                #if filename.endswith("FULL"):
                if "FULL" in f:
                    fullmamm_path.append(os.path.join(dir, f)) 
                elif "MASK"in f:
                    maskmamm_path.append(os.path.join(dir, f))
                elif "CROP"in f:
                    crop_path.append(os.path.join(dir, f))
        print(len(fullmamm_path))
        print(len(maskmamm_path))
        for mamm_path in fullmamm_path:
            ds = pydicom.dcmread(mamm_path)
            full_id = str(ds.PatientID).split("_")[1:3]
            patient_id = f"{full_id[0]}_{full_id[1]}" 

            fullmamm = ds.pixel_array
            img_pre, lr_flip = fullMammoPreprocess(fullmamm)
            
            fullmamm_pre_norm = cv2.normalize(img_pre, None, alpha=0,
            beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
            save_filename = (os.path.basename(mamm_path).replace(".dcm", "") + "__PRE.png")
            save_path = os.path.join(output_path, save_filename)
            cv2.imwrite(save_path, fullmamm_pre_norm)
            i += 1
            print(i)

            mask_path = [mp for mp in maskmamm_path if patient_id in mp]
            for mp in mask_path:
                mask_ds = pydicom.dcmread(mp)
                mask = mask_ds.pixel_array

                mask_pre = maskPreprocess(mask=mask, lr_flip=lr_flip)
                save_filename = (os.path.basename(mp).replace(".dcm", "") + "__PRE.png")
                save_path = os.path.join(output_path, save_filename)
                cv2.imwrite(save_path, mask_pre)

process_images()