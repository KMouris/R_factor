# Purpose
Python package for calculating the R factor based on gridded data with high temporal resolution

# RasterManipulation_2 

Its main purpose is to convert the received precipitation and temperature into .csv files that can be used to calculate the R factor for each cell with the program RFactor_5. 
    
## Input data
* path_precip = folder location where the precipitation rasters are found
    * Files must be in .txt form    
    * File name must be in the format: YearMonthDay_Hour (YYYYMMDD_0HH)
* path_temp= folder location where the temperature rasters are found
    * Files must be in .txt form 
    * File name must be in the format: YearMonthDay_Hour (YYYYMMDD_0HH)
    * There must be one temperature file for each precipitation file. 
    * Temperature and precipitation rasters must have the same resolution (same number of cells)
    * It is not mandatory to introduce temperature values (see input file 4)
* savepath= folder location where the .csv files created by the program will be saved
* temp= binary variable
    * True means you are introducing temperature files. 
    * False means you are not introducing temperature files. In the resulting file, the temperature value will be 9999
    
## Output data
= .csv file for each cell, containing the precipitation value for each available time interval
* File name: OriginalRow_OriginalColumn in the raster
    * This information will be used in the “RFactor_5” program in order to recreate the original raster, assigning the corresponding R factor to each cell, in its original position

