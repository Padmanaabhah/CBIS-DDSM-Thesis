from enum import unique
import os
from pathlib import Path
import pydicom
import numpy as np
import shutil

top = Path("D:/CBIS-DDSM-1/Mass-Training_Full_Mammogram_Images/")
top = Path("D:/CBIS-DDSM-1/Mass-Training_ROI_and_Cropped_Images/")
#top = Path("D:/CBIS-DDSM-1/Mass-Test_full_mammogram_images/")
top = Path("D:/CBIS-DDSM-1/Mass-Test_ROI-mask_and_crpped_images/")
top = Path("D:/CBIS-DDSM-1/Train")

dest_path = Path("D:/Train/")

def getfilecount(path):     
    count = 0
    for _, _, files in os.walk(path):
        for file in files:
            if Path(file).suffix == ".dcm":
                count += 1
    print(f'Total files to be updated {count}')

def getnewname(current_name):
    try:
        dcm = pydicom.dcmread(current_name)
        patient_id = dcm.PatientID.replace(".dcm", "") 

        try:
            img_type =  dcm.SeriesDescription
            if "full" in img_type:
                return f"{patient_id}_FULL.dcm"       

            elif "crop" in img_type:
                suffix = patient_id.split("_")[-1]

                if suffix.isdigit():
                    new_patient_id = patient_id.split("_" + suffix)[0] 
                    return f"{new_patient_id}_CROP_{suffix}.dcm" 
            
            elif "mask" in img_type:
                suffix = patient_id.split("_")[-1]
                if suffix.isdigit():
                    new_patient_id = patient_id.split("_" + suffix)[0] 
                    return f"{new_patient_id}_MASK_{suffix}.dcm" 


          
        except:
            if "full" in current_name:                
                return f"{patient_id}_FULL.dcm"
            else:
                arr = dcm.pixel_array
                unique = np.unique(arr).tolist()

                if len(unique) != 2:
                    suffix = patient_id.split("_")[-1]
                    if suffix.isdigit():
                        new_patient_id = patient_id.split("_" + suffix)[0] 
                        return f"{new_patient_id}_CROP_{suffix}.dcm" 
                
                else:
                    if len(unique) != 2:
                        suffix = patient_id.split("_")[-1]
                        if suffix.isdigit():
                            new_patient_id = patient_id.split("_" + suffix)[0] 
                            return f"{new_patient_id}_MASK_{suffix}.dcm" 

            print("Error")

    except Exception as e:
        print(f"Failed to se new name because of {e}")


def move_dcm_up(dest_dir, source_dir, dcm_filename):
    try:
        dest_dir_with_new_name = os.path.join(dest_dir, dcm_filename)
        #print(dest_dir)
        #print(source_dir)

        if not os.path.exists(dest_dir_with_new_name): 
            shutil.move(source_dir, dest_dir)
        
        elif os.path.exists(dest_dir_with_new_name): 
            new_name = dcm_filename.strip(".dcm") + "__a.dcm"
            shutil.move(source_dir, os.path.join(dest_dir, new_name))

    except Exception as ex:
        print(f'Error while moving {ex}')

def main():
    getfilecount(top)
    i = 0
    for base_dir, dir, files in os.walk(top):
        dir.sort()
        files.sort()
        
        for file in files:
            if Path(file).suffix == ".dcm":
                #print(f'File name {file}')
                current_name = os.path.join(base_dir, file)
                #print(f'Current Name {current_name}')
                new_name = getnewname(current_name)
    
                if new_name:
                    new_name_path = os.path.join(base_dir, new_name)
                    os.rename(current_name, new_name_path)
                    move_dcm_up(dest_path, new_name_path, new_name)

                #print(new_name_path)
                i += 1
                if i%100 == 0:
                    print(i)
                #     exit(0)
    getfilecount(dest_path)
main()

#getfilecount("d:/CBIS-DDSM-1")
