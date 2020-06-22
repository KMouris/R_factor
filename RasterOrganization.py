import glob
import os
import shutil

###PROGRAM RECEIVES THE FOLDER WHERE THE RASTER FILES ARE LOCATED AND SAVES THEM, BY MONTH, TO ANOTHER FOLDER
###The main objective is to separate the daya by month in order to do the calculations on a monthly basis, for the sensitiviy analysis primarily
###But the organization can serve other purposes in the future, to copy large amounts of data to other folders

#----Function 1: ----#
#Function receives the folder path where the
def fast_scandir(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    # for dirname in list(subfolders):
    #     subfolders.extend(fast_scandir(dirname))
    return subfolders

#----Function 2:
###In case the file names have not been modified to the necessary name (removing the prefix), this function does that
def ChangeName(name):
    if name.startswith("tempbanja_") or name.startswith("precbanja_"):
        rename= name[10:]
    else:
        rename=name
    return rename

#Function 3: Get Month----#
###Function extracts the month from the file name, in order to later determine in which folder the file must be saved in
def GetMonth(name):
    month=int(name[4:6]) #month
    print("Month: ", month)
    return month

#User Input#

#Folder with original files
import_file= r'C:\Users\Oreamuno\Desktop\Banja Reservoir\Data\Corrected Data\Precip_Banja_corr_Text'
save_file = r'C:\Users\Oreamuno\Desktop\Banja Reservoir\RFactor_SensitivityAnalysis' #Location where monthly folders are located, in descending order
suffix = "\\" + "01_Precipitation" #Name of folder within the main month directory where I want to save the corresponding files (the folder must be names the same in all folders)


folders = fast_scandir(save_file) #List with save folder paths, in montly order
filenames = glob.glob(import_file + "\*.txt")
i=0

for file in filenames:
    name = os.path.basename(filenames[i])  # gets name of file being read
    name=ChangeName(name)
    month=GetMonth(name)
    target = folders[month-1] + suffix + "\\" + name
    shutil.copyfile(file, target)
    i+=1

