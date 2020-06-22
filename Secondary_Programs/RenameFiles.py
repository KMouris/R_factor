import glob
import os
import shutil
from os import listdir
from os.path import isfile, join

#----FUNCTIONS----#

#--Function 1--#
###Function receives the base name of the file and removes the prefix and reorganizes it to the format "YYYYMMDD_HH"
def ChangeName(name):
    save_name=name[10:18] + "_" + name[19:]
    return save_name

#----USER INPUT----#

input_path = r'C:\Users\Oreamuno\Desktop\Banja Reservoir\Data\Corrected Data\Precip_Banja_corr'
save_path = r'C:\Users\Oreamuno\Desktop\Banja Reservoir\Data\Corrected Data\Precip_Banja_corr_textfiles'

#----MAIN CODE----#

filenames = [f for f in listdir(input_path) if isfile(join(input_path, f))] #reads all files in my folder
i=0  #counter


for file in filenames:
    name = os.path.basename(filenames[i])  # gets name of file being read
    save_name=ChangeName(name) #Changes name to the needed format
    os.rename(input_path + "\\" + name, input_path + "\\" + save_name + ".txt") #renames file and changes extenson to .txt
    i+=1 #to go over all the files in the folder


#NOTES:
#The program renames the current files, so if you need the original files make sure you save them in another folder (have a back up)
