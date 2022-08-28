import os,shutil

input_dir = "D:\Test_output"
output_full = "D:\Test_output_full"
output_mask = "D:\Test_output_mask"

def splitfiles():
    #images = [f for f in os.listdir(input_dir) if "FULL" in f]
    i = 0
    j = 0
    for f in os.listdir(input_dir):
        if "FULL" in f:
            i += 1
            path = os.path.join(input_dir, f)
            shutil.copy(path, output_full)
        elif "MASK" in f:            
            path = os.path.join(input_dir, f)
            j += 1
            shutil.copy(path, output_mask)
            #print(path)
    print(i)
    print(j)
    print(i+j)

splitfiles()
