from logging import exception
from tkinter import EXCEPTION
import pandas as pd
import os
import cv2
import numpy as np

from sympy import imageset

img_path = "D:\Test_output"
csv_path = "D:\CBIS-DDSM-1\mass_case_description_test_set.csv"
abnormality_col = "abnormality_id"
extension = ".png"
output = "D:\Test_Summed_output"
save=True

def findMultiTumour():
    try:
        df = pd.read_csv(csv_path, header=0)
        multi_df = df.loc[df["abnormality id"] > 1]
        print(len(multi_df))
        multi_tumour_list = []        
        for row in multi_df.itertuples(): 
            patient_id = row.patient_id
            lr = row._3
            img_view = row._4  
            identifier = "_".join([patient_id, lr, img_view])
            multi_tumour_list.append(identifier)
        print(len(multi_tumour_list))
        multi_tumor_set = set(multi_tumour_list)
        return multi_tumor_set
    except Exception as e:
        print("Error in finding multi tumour")

def masksToSum(multitumourset):
    try:
        images = [f for f in os.listdir(img_path) if (not f.startswith(".") and f.endswith(extension))]
        masks_to_sum = [ m for m in images 
        if ("MASK" in m and any(multi in m for multi in multitumourset))]
        masks_to_sum_dict = {patient_id: [] for patient_id in multitumourset}
         
        for k, s in masks_to_sum_dict.items():
            v = [os.path.join(img_path, m) for m in masks_to_sum if k in m]
            masks_to_sum_dict[k] = sorted(v)

        to_pop = [k for k,v in masks_to_sum_dict.items() if len(v) == 1]

        for k in to_pop:
            masks_to_sum_dict.pop(k)
        
        return masks_to_sum_dict
    
    except:
        print("There is an error in mask to sum")


def sumMasks(mask_list):
    try:
        summed_mask = np.zeros(mask_list[0].shape)

        for arr in mask_list:
            summed_mask = np.add(summed_mask, arr)

        _, summed_mask_bw = cv2.threshold(src=summed_mask, thresh=1, maxval=255, type=cv2.THRESH_BINARY)
        
        return summed_mask_bw
    
    except Exception as e:
        print("There is error in summed mask")


def main():
    multi_tumour_set = findMultiTumour()
    masks_to_sum_dict = masksToSum(multi_tumour_set)
    for k, v in masks_to_sum_dict.items():
        mask_list = [cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE) for mask_path in v]
        
        summed_mask = sumMasks(mask_list=mask_list)
        save_path = os.path.join(output, "_".join(["Mass-Test", k, "MASK__PRE.png"]))
        cv2.imwrite(save_path, summed_mask)
main()
