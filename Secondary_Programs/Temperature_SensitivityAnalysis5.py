import numpy as np
import pandas as pd
import os
import glob
import sys
import math
import numbers
import re
import datetime
import time
start_time = time.time()

#Program does a sensitivity analysis for 1 MONTH, to observe the impact of the temperature threshold in the overal monthly R factor for each cell in the Raster

#----Error Check Function 1: Check errors----#
### Function checks user input and makes sure the user input is correct
def CheckInput(time_interval, min_6hours, min_P, CF):
    if time_interval == 10 or time_interval == 15 or time_interval == 30 or time_interval == 60:
        pass
    else:
        sys.exit('ERROR: Time interval not accepted. Must choose 10, 15, 30 or 60 minutes')
    if isinstance(min_6Hours, numbers.Number) is False:
        sys.exit("ERROR: 'min_6Hours' is not a number. Numbers use point as decimal separator.")
    if isinstance(min_P, numbers.Number) is False:
        sys.exit("ERROR: 'min_P' is not a number. Numbers use point as decimal separator.")
    if(CF== True and time_interval != 60):
        sys.exit("ERROR: The R conversion factor is only valid when time interval is of 60 min.")

#----Function 1: Convert to date-time----#
###Function recieves a row number and transforms columns 0 to 5 to date form: YYYY-MM-DD HH:MM:SS
def ConvertDateTime(i, Station):
    dt_string = str(int(Station[i, 2]))+"-"+str(int(Station[i, 1]))+"-"+str(int((Station[i, 0])))+ " "+str(int(Station[i, 3]))+\
               ":"+str(int(Station[i, 4]))+":"+str((int(Station[i, 5])))
    dt=datetime.datetime.strptime(dt_string, '%d-%m-%Y %H:%M:%S') #transform into date-time format
    return dt

#----Error check Function 9: Check correct input----#
###Function checks each file input and makes sure the time interval in the user input is the correct one
def CheckTimeInterval(time_interval, Station):
    length = len(Station)
    for i in range(1, length-1):
        duration = ConvertDateTime(i, Station) - ConvertDateTime(i-1, Station)
        year = ConvertDateTime(i, Station).year - ConvertDateTime(i-1, Station).year
        Seconds = duration.total_seconds()
        if Seconds/60 != time_interval and year == 0:
            print("Time interval: ", Seconds / 60)
            sys.exit("ERROR: Time interval input is incorrect. Check user input")

##----Function 10-----##
###Function receives ONE input data file (saved in a data frame) and extracts the unique months and years within the record and saves it in a vector.
###The assumption is that all the files contain the same date records. The length of the unique_months vector equals the amount of months analyzed and
### The size of the unique_years vector = the amount of years analyzed (whether they are complete years or not)
def MonthYear(Station):
    unique_years = Station['Year'].unique().tolist() #Get the unique years in the input files  and save them in a list
    unique_months = Station['Month'].unique().tolist()  # Get the unique months in the input files  and save them in a list
    unique_my = [None]*len(unique_years)*len(unique_months) #Initialize list for all the month-year combination, since results are only in a monthly basis
    print("Months: ", unique_months, "\nYears: ", unique_years)
    print("Number of months: ", len(unique_months), "\nNumber of years: ", len(unique_years))
    i=0
    for y in range(0, len(unique_years)):  # for each year to be analyzed
        for m in range(0, len(unique_months)):  # for each month to be analyzed
            # From MonthYear function results, save to a string the given combination year-month
            unique_my[i] = str(int(unique_years[y])) + "-" + str(int(unique_months[m]))
            i+=1
    # print(unique_my)
    return unique_months, unique_years, unique_my

#----Error Check Function 3: Check if month input corresponds to amount of months in files----#
def CheckMonth(month, df_months):
    if month == len(df_month):
        pass
    else:
        sys.exit("ERROR: The months determined by the user differ from the amount of months being analyzed")

#----Function 8:To save each Filled Matrix into a .csv file, for each station
def SaveCSV(df, name, path):
    name= path + "\\" + name
    df.to_csv(name, sep=',')

#----Function: Save Results in raster form, as .txt files
###Function receives 3D matrix with R Factor for each cell. Each array corresponds to a different month
def SaveRaster(R_3D, path):
    k=0 #to iterate through the 3D arrays
    df_head = pd.DataFrame(
        [['ncols', int(original_columns)], ['nrows', int(original_rows)], ['xllcorner', xllcorner],
         ['yllcorner', yllcorner],
         ['cellsize', cellsize], ['nodata_value', -9999.000000]])  # Header for .txt file

    for j in range (min_temp, max_temp+2): #for each temperature value in range plus 1 extra loop to save the Statistical values for each month-year combination
        for m in range (0,len(unique_m_y)):
            if j <= max_temp:  # to save the rasters with the R factor values, for each temperature value
                save_name = path + "\\" +str(unique_m_y[m])+ "_Temp_"+ str(j)+ ".txt" # File name, to save each array with corresponding temp
                save_raster = np.reshape(R_3D[k, :, :], (int(R_3D.shape[1]), int(R_3D.shape[2])))  # save each array (k) in its own matrix, to later change to 3D array
                df_raster = pd.concat([df_head, pd.DataFrame(save_raster)], axis=0)
                df_raster.to_csv(save_name, header=False, index=False, sep='\t', na_rep="")
                k += 1
            else: #for the statistical values of max-min difference and percentage difference
                #Save Max-Min raster
                save_name = path + "\\" + str(unique_m_y[m]) + "_Max-Min" + ".txt"  # File name, to save Max-Min value for givem Year-Month
                save_raster = np.reshape(R_3D[k, :, :], (int(R_3D.shape[1]), int(R_3D.shape[2])))  # save each array (k) in its own matrix, to later change to 3D array
                df_raster = pd.concat([df_head, pd.DataFrame(save_raster)], axis=0)
                df_raster.to_csv(save_name, header=False, index=False, sep='\t', na_rep="")
                #Save Percentage difference raster:
                save_name = path + "\\" + str(unique_m_y[m]) + "_PercentageDifference" + ".txt"  # File name, to save Max-Min value for givem Year-Month
                save_raster = np.reshape(R_3D[k+1, :, :], (int(R_3D.shape[1]), int(R_3D.shape[2])))  # save each array (k) in its own matrix, to later change to 3D array
                df_raster = pd.concat([df_head, pd.DataFrame(save_raster)], axis=0)
                df_raster.to_csv(save_name, header=False, index=False, sep='\t', na_rep="")
                k += 2 #Because there are 2 statistical values being calculated

#----Function: Save monthly R factor for all raster----#
###Function receives, for each FILE iteration, the monthly R factors for that cell, with the results for each Temperature threshold (an entire row of values).
###It saves it in a Data Frame, to then be able to compare all data. The current iteration values (row) is added BELOW the previous iteratarion's results.
def RFactor_Raster(df_RasterR, df_CellR):
    df_RasterR = pd.concat([df_CellR, df_RasterR], axis=0) #add current cell data into overall results data frame. The order in which you save is important
                                                          #because the new cell must be located beneath the previously calculated cell (row), not before
    return df_RasterR

#----Function: Save monthly R factor for each temperature value iteration in Data Frame
###Function receives, for each TEMPERATURE iteration, the monthly R factor (df_month) and the df_CellR, where the program saves the previous and current T iteration
###R factor results. It adds each iteration's results in a new column, whose column name corresponds to the temperature threshold value. The new iteration is added
###after the previous iteration's results
def RFactor_Cell(df_month, df_CellR):
    # print(df_month)
    if t == min_temp: #If it is the first column, copy the month-year AND the Rfactor for the given temperature
        df_CellR=df_month
    else: #for the rest, only copy thr R factor, since the onth-year is the same
        list1 = list(df_month.columns.values) #Get the name of the columns in the df_month. The valuein column 1 equals the R factor title, with the temperature value
        column = df_month[list1[1]] #extract the values of the column with the R factor values
        df_CellR = pd.concat([df_CellR, column], axis=1) #add ONLY the column with R factors to the cell data frame
    return df_CellR

#----Function 7: Calculate R Factor per month
###Function recieves Data Frame with information per storm, and groups the columns by month, and gets the sum of EI30 (R factor) per month, to determine R factor per month
###Function creates a copy of df_storm in order to avoid affecting the final data frame
def RFactor(df_storm):
    storm_copy = df_storm.copy()  # Save a copy of data frame, so as not to modify original one
    storm_copy['Year-Month'] = pd.to_datetime(storm_copy['1']).dt.to_period('M')  # add column with Year-Month combination to the copied data frame
    df_sum = pd.DataFrame(storm_copy.groupby(['Year-Month'], as_index=False).EI.agg(['sum'])).reset_index()
    df_RFactor = pd.DataFrame(columns = ["Year-Month", "R Factor (Temp= " + str(min_temp_loop) + "C)"]) #initialize the data frame for the onthly R factors

    for i in range (0,len(unique_m_y)):
        date = datetime.datetime.strptime(str(unique_m_y[i]), '%Y-%m')
        date2 = date.strftime('%Y-%m') #string version of date with year-month value

        storm_copy['Year-Month'] = pd.to_datetime(storm_copy['1']).dt.to_period('M')
        # Lookup in the df_sum data frame the value whose month and year correspond to "date" value.
        # The "add function is used, but there should only be  1 value per year-month combo
        value = df_sum.loc[(df_sum['Year-Month'].dt.month == date.month) & (
            df_sum['Year-Month'].dt.year == date.year), 'sum'].sum()
        df_temp = pd.DataFrame([{'Year-Month': date2, "R Factor (Temp= " + str(min_temp_loop) + "C)": value}])
        df_RFactor= df_RFactor.append(df_temp, ignore_index=True)

    return df_RFactor

#----Funtion 6: Recieves information from StartTime and fills the result list----#
###Function fills a data frame with the information for each storm
def FillMatrix(df_Storm, sd, ed, hours, t_interval, precip, I30, E, EI, Station):
    start_date = ConvertDateTime(sd, Station)
    end_date = ConvertDateTime(ed, Station)
    duration=round(hours*(t_interval/60),2)
    df_Storm = df_Storm.append({"1": start_date, "2": end_date, "3": duration, "4": precip, "5": I30, "6": E, "EI": EI}, ignore_index=True)
    return df_Storm

#----Function 5: Calculates total precipitation----#
###Function calculates the total precipitation in the given storm, adding the precipitation values between the start and end date for the storm.
def TotalPrecipitation(sd, ed, Station):
    precip=np.sum(Station[sd:ed,6])
    return precip

#----Function 4: Calculate EI----#
###Recieves I30 (maximum intensity in 30 min) and the total kinetic energy for the storm
def CalculateEI(E,I30, CF):
    if CF == True: #If user decides to use R factor conversion factor
        EI=1.5597*E*I30 #COnversion factor = 1.5597 according to Panagos et.al
    else:
        EI=E*I30
    return EI

#----Function 3.1: Calculate time step intensity
###Function calculates the intensity for the given time step in order to calculate the unit energy for the given time step. Used only from FUNCTION 2
def TSIntensity(value,time_interval): #precipitation value for given time step (in mm), time interval
    intensity=0
    if time_interval==10: #input data is every 10 min
        intensity=value*6
    elif time_interval==15:#input data is every 15 min
        intensity=value*4
    elif time_interval==30: #input data is every 30 min
        intensity=value*2
    else: #input data is every 60 min (only option left)
        intensity = value
    return intensity

#----Function 3: Calculate kinetic energy (E) ----#
#USER INPUT: time_interval (every 10, 15, 30 or 60 min), sd (start date), ed (end date), data matrix (for the station)
#######FUTURE USER INPUT: eq (Which equation to use)
###Function calculates the total kinetic energy for the given storm (E), in MJ/ha. First it calculates the unit energy for
###the given time step and multiplies it by the total precipitation for the given time step.
def CalculateEnergy(time_interval, sd, ed, Station):
    E = 0 #Value to modify in each step, adding the previous value
    cells=0
    for i in range (sd,ed+1): #For every value in range
        intensity=TSIntensity(Station[i, 6], time_interval)
        e = 0.29*(1-0.72*math.exp(-0.05*intensity)) #Brown and Foster (1987) equation, cited by Panagos, et.al (2014)
        E += e*Station[i,6]
    return E

#----Function 2: Calculate I30----
#User input: time interval, start date index, end date index,
##Function calculates the maximum intensity in 30 min for the given storm (in mm/h).
###For hourly time intervals, the I30max is the same as the max intensity in an hour
def CalculateI30(time_interval, sd, ed,Station):
    I30=0
    for i in range(sd, ed):  #do procedure for each time interval
        if time_interval==10:
            intensity= (np.sum(Station[i:i+3, 6]))*2 #Sums cell i and the next 2 cells to get P30, multipies by 2 to get  intensity (mm/h)
            # print('First value:', Station[i,6])
            # print('First value:', Station[i+1, 6])
            # print('First value:', Station[i+2, 6])
            # print('Intensity:', intensity)
        elif time_interval==15:
            intensity = (np.sum(Station[i:i + 2, 6])) * 2  #-Sums cell i plus next cell
        elif time_interval==30:
            intensity=Station[i,6]*2
        else: #For time interval of 60 min
            intensity=Station[i,6]

        if intensity>I30: #Saves maximum I30 value
            I30=intensity

    return I30

#----Function 1.2: Calculate n ----#
###Function calculates how many cells equals 1 hour or 6 hours in the data
def CalculateHour(time_interval, hours):
    n=0
    if time_interval==10:
        n=6*hours
    elif time_interval==15:
        n=4*hours
    elif time_interval==30:
        n=2*hours
    elif time_interval==60:
        n=hours
    else:
        sys.exit('ERROR: Time interval not accepted. Must choose 10, 15, 30 or 60 minutes')
    return n

#----Function 1.1: Sum 6 hours----#
###Function receives row value, storm matrix, temperature threshold, time interval
###Sums the total precipitation in a 6 hour period to compare with min 6 hour precipitation value
def SumSixHours(i, Station, min_temp, time_interval):
    n = CalculateHour(time_interval, 6)  # Calculate how many cells equals 6 hours
    SixHours = np.zeros(n)
    for j in range(0, n): #To fill SixHours vector with the next 6
        if i<len(Station): #Doesnt enter if you have a storm at the end of time interval, and i is greater than number of rows
            if Station[i,7]>=min_temp:
                SixHours[j]=Station[i,6]
                # print("Precipitation value: ", Station[i,6])
                # print("Time step temperature: ", Station[i, 7])
        else:
            SixHours[j] = 0
        i+=1
    SumSixHours = np.sum(SixHours)
    # print("Vector is: ", SixHours, "\nSum is: ", SumSixHours)
    return SumSixHours

##---- Main Function 1: Finds start and end of Rain Event----##
###Function receives the data matrix, for the given station, the time interva of the data, and the users input of min 6 hour Precip, min erosive Precipitation
####a decision CF, which states whether the user wants to consider a conversion factor for 60 min intervals
###If the Min 6 hour precipitation AND the min erosive event precipitation is 0, the program considers all storms:
# ### The storm starts when the precipitation value is greater than 0. It then begins to check when the storm ends
# ### While precipitation is greater than 0, the storm continues. When it reaches a 0, it checks if, for the next 6 hours, the total precipitation is
# ### greater or less than the min 6 hour precipitation. If it is lower, the storm ends.
# ### After making sure the storm ends, it checks if the total precipitation is greater than the min storm precipitation to be considered erosive (according to user input)
# ###If it is an erosive event, it calculates the storm duration, kinetic energy, I30 and EI30, and stores it in a Data Frame
#-------------------------------------------------------------------------------------------------------------------------------#
def StormID(Station, time_interval, min_6Hours, min_P, CF, min_temp):
    #CREATE DATA FRAME -WHERE I WILL SAVE THE INFORMATION FOR EACH STORM
    df_storm = pd.DataFrame(columns = ["1", "2", "3", "4", "5", "6", "EI"]) #Use column names 1 to 7 so simplify input of values (visually)
    iterations=Station.shape[0] #Indicates the number of rows, which equals the number of iterations
    hours=0
    for i in range(0, iterations):#For each row (For each date)
        if Station[i, 6] > 0 and hours==0: #-If the precipitation value is 0 and it is the first  value for the given event
            SixHours = SumSixHours(i, Station, min_temp, time_interval)
            if SixHours > min_6Hours: #Storm starts if, in the next 6 hour period, the precipitation is > MIn 6 hour precipitation
                sd=i #row in which start of storm is located
                hours +=1
        elif hours>0: #If the storm has already begun, check when the storm ends
            SixHours= SumSixHours(i, Station, min_temp, time_interval)
            if SixHours > min_6Hours or Station[i, 6] >=0.001: #If, in the next 6 hours, the total precipitation is greater than the min 6 hour precipitation
                                                                # or the precipitation is greater than 0 (Must stop at a 0)
                hours +=1 #Storm continues
            else: #If, in the next 6 hours, the precipitation is less than or equal to the min precipitation AND precipitation =0, STORM ENDS
                ed=i #index of storm end
                #1. Calculate total precipitation and then check if it is greater than the min Precipitation for an erosive storm criteria
                total_precipitation= TotalPrecipitation(sd, ed, Station)
                if total_precipitation >= min_P: #If the total precipitation is larger than min Precipitation to consider the storm erosive
                    # 2. Send sd, ed, data matrix and t_interval to FUNCTION to calculate intensities, and max I30 intensity
                    I30 = CalculateI30(time_interval, sd, ed, Station)
                    # 3. Send sd, ed, data matrix (and equation?) to FUNCTION to calculate E
                    E = CalculateEnergy(time_interval, sd, ed, Station)
                    # 4. Send E, I30 to calculate EI30 for storm
                    EI = CalculateEI(E, I30, CF)
                    # 5. Send Storm Matrix, storm counter, sd,ed,hour counterI30, E, EI30 and data matrix to FUNCTION to input everything in the matrix for the given station
                    df_storm = FillMatrix(df_storm, sd, ed, hours, time_interval, total_precipitation, I30, E, EI, Station)
                hours = 0 #Restart storm counter to try and find a new storm
    df_month = RFactor(df_storm)
    df_storm= df_storm.rename(columns={"1":"Start Date", "2":"End Date", "3": "Storm duration (h)", "4":'Tot Precipitation (mm)', "5": "I30 (mm/h)", "6": "KE (MJ/ha)", "7": 'EI30 (Mh*mm/ha*h)'})
    # print(df_storm.head())
    return df_storm, df_month

##-----Main Function 2: Save data to 3D array-----##
###Function receives the R Factor values for the given cell and temperature thhreshold value and fills the respective row-column value in the corresponding array
### k is the array index in the 3D array in which to start the data input. It fills i number of arrays, correspodning to the amount of month-year combinations
def ThreeDArray(name, df_month, R_3D, k):
    rc = re.findall("\d+", name)  # "rc[0] is the original row and rc[2] is the original column"
    for i in range (0, len(unique_m_y)):
        date = datetime.datetime.strptime(str(unique_m_y[i]), '%Y-%m').strftime('%Y-%m')
        if k < len(unique_m_y)*(abs(max_temp-min_temp)+1): #Value to input corresponds to a R Factor value
            # Lookup in the df_month data frame the value whose Year-month column correspond to "date" value.
            # The "add function is used, but there should only be  1 value per year-month combo
            value = df_month.loc[(df_month['Year-Month'] == date), "R Factor (Temp= " + str(min_temp_loop) + "C)"].sum()
            R_3D[k, int(rc[0]), int(rc[2])] = value  # save value to the corresponding row-column in 3D array
            k += 1
        else: #to fill the last 2 arrays, corresponding to the statistical values for each cell and year-combination
            #Fill Max-Min value
            value = df_month.loc[(df_month['Year-Month'] == date), "Max-Min"].sum()
            R_3D[k, int(rc[0]), int(rc[2])] = value  # save value to the corresponding row-column in 3D array
            #Fill Max-Min Value:
            value = df_month.loc[(df_month['Year-Month'] == date), "Abs. Difference"].sum()
            R_3D[k+1, int(rc[0]), int(rc[2])] = value  # save value to the corresponding row-column in 3D array
            k+=2 #changes to +=2 because we are filling the statistical values, and there are 2 values being calculated
    return R_3D

##----Main Function 3: Sensitivity Analysis Statistics-----##
def RFactorStatistics(df_RasterR):
    df_RasterR['Max-Min'] = df_RasterR.max(axis=1) - df_RasterR.min(axis=1)
    df_RasterR['Abs. Difference'] = df_RasterR['Max-Min']/df_RasterR.max(axis=1)


##--------MAIN CODE--------##

##-----USER INPUT-----##

#Storm properties
time_interval= 60 #-User can input if time interval is 5 min, 10 min, 30 min or 60 min
min_6Hours= 1.27 #-User can input min precipitation value (in mm) in a 6 hour period (if 0, all storm end when, in 6 hours, the sum is 0)
min_P= 12.7 #-User can input min total precipitation in order to consider it an erosive storm (if 0, all storms are valid)
CF=True #-User decides, if interval is of 60 min, if they want to use the R factor conversion factor

#Input for temperature sensitivity analysis#
min_temp=-5 #Minimum temperature threshold to begin sensitivity analysis for each cell
max_temp= 1 #Number of temperature values to test

#Original Raster Information
original_rows = 115
original_columns = 170
xllcorner = 350000.000000
yllcorner = 4445000.000000
cellsize = 1000

#Folder where the Raster Manipulation .csv files are locates:
path = r'C:\Users\Oreamuno\Desktop\Banja Reservoir\RFactor_SensitivityAnalysis\01_January\03_RasterManipulation_Results'
#Where to save the .csv file with the R factor for each cell, for each Temperature iteration:
save_path_month=r'C:\Users\Oreamuno\Desktop\Banja Reservoir\RFactor_SensitivityAnalysis\01_January\04_EI30_AllCellResults'
#Where to save the .txt file with the raster for each temperature iteration and the statistical analysis results:
save_path_raster= r'C:\Users\Oreamuno\Desktop\Banja Reservoir\RFactor_SensitivityAnalysis\01_January\05_EI30_RasterResults'
save_path_storm = r'C:\Users\Oreamuno\Desktop\Banja Reservoir\RFactor_SensitivityAnalysis\01_January\06_EI30_ByMonth'

CheckInput(time_interval, min_6Hours, min_P, CF) #Checks user input to make sure they are correct

#-----CODE-----#
filenames=glob.glob(path+"\*.csv") #Get all the .csv files in the input folder, and save the names in a list, to iterate thru them
i=0 #to iterate in file names

#From ONE input file, determine the amount of months and years in the record data.
Station=pd.read_csv(filenames[i], delimiter=',')
unique_months, unique_years, unique_m_y = MonthYear(Station) #get vectors with the months and years in the data record

#Check that the time interval for ONE input file coincides with user time interval input (and assume it is the same with the rest of the files)
CheckTimeInterval(time_interval, np.array(Station))

#To save the Monthly R factor for each cell in a data frame
df_RasterR=pd.DataFrame()

#To save the origina, row and colum for each cell, to be filled in order it is being analyzed by the program, and filled in the corresponding result rasters
np_location = np.zeros((len(filenames), 2))

#--In case you want to save the results in a 3D array, to create the rasters with the R factor--#
# R_3D= np.full(((len(unique_years)*len(unique_months)*abs(max_temp-min_temp)+3, 115, 170)), -9999.0)
R_3D= np.full(((len(unique_m_y)*(abs(max_temp-min_temp)+1) + len(unique_m_y)*2, original_rows, original_columns)), -9999.0)

for file in filenames:
    Station=np.array(pd.read_csv(file, delimiter=',')) #Save input file into a Numpy Array
    name = os.path.basename(filenames[i]) #Get file name, including file extension
    print("File: ", name)
    # For sensitivity analysis, create an empty data frame to save all the monthly results for each cell (file):
    df_CellR = pd.DataFrame()
    k=0 #counter for array in 3D array to fill in each t interation

    for t in range(min_temp, (max_temp+1)): #Do calcualtions for each 'file' for each temperature threshold value
        name_loop = name[0:9] + "_" + str(t) + ".csv" #New File name that indicates the min temperature value being used for the results
        min_temp_loop = t #New minimum temerpature is equal to loop counter value
        df_storm, df_month = StormID(Station, time_interval, min_6Hours, min_P, CF, min_temp_loop) #Get R factor per storm and per month - Calculations as in EI30 program

        #For temperature sensitivity analysis, save RFactor, per month, on another data frame, to be added to overall file
        df_CellR= RFactor_Cell(df_month, df_CellR)
        ThreeDArray(name, df_month, R_3D,k)
        k+=(len(unique_years)*len(unique_months)) #used to fill 3D array

    #Save results for each cell in df_CellR data frame into a larger data frame with the results for all the cells.
    RFactorStatistics(df_CellR)
    ThreeDArray(name, df_CellR, R_3D, k)
    df_RasterR= RFactor_Raster(df_CellR, df_RasterR)

    i+=1 #Add to counter

# RFactorStatistics(df_RasterR) #Calculate wanted statistical values for each cell, with regards to the changes in temperature
SaveCSV(df_RasterR, "AllCells.csv", save_path_month) #Save the results for each cell, for each Temperature, in .csv file

#To save R Factor in 3D array, in order to create the Raster
# R_3D = ThreeDArray(np_location, df_RasterR.to_numpy(dtype='float'), R_3D) #Send the results by month, as a numpy array

SaveRaster(R_3D, save_path_raster)



print('My program took ', time.time()-start_time, " to run.")