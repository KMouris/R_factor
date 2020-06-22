# Purpose
Python package for calculating the R factor based on gridded data with high temporal resolution

Main code is RFactor_5, whereas RasterManipulation_2 is used to pre-process the raw data

# RFactor_5

Calculates the R factor on a per storm, per month and per year basis for each cell in the original Raster, and generates an output raster for each time frame with the corresponding R factors for each cell. The resulting Rasters can be opened in GIS program in order to be used in the RUSLE equation. 

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

## Error checks 
The program checks for the following information: 
* If the input file directories and the result directories exist 
* If there are an equal number of precipitation and temperature files, in case the temp binary variable is True 
* It does NOT check if the precipitation files and temperature files correspond to the same dates. It combines the precipitation with the temperature in the same order they are read in the folder 

## Main functions in the program
A detailed description of the functions is included in the user manual.
