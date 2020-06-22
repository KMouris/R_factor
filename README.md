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

