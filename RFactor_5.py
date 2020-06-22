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

##--------FUNCTIONS--------##

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

#----Error check: Check correct input----#
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
    print("Months: ", unique_months, "\nYears: ", unique_years)
    print("Number of months: ", len(unique_months), "\nNumber of years: ", len(unique_years))

    for y in range (0,len(unique_years)):
        n_months = Station[Station['Year'] == unique_years[y]].count()['Month']
        #To tell user if there are records for each hour in they given year:
        if n_months == 8784 or n_months == 8760: #If there are 365*24 or 366*24 records, the year is complete
            print("The year ", unique_years[y], " is complete")
        else:
            print("The year ", unique_years[y], " is incomplete")
    return unique_months, unique_years

#----Function 9:To save each Filled Matrix into a .csv file, for each station
def SaveCSV(df_storm, name, path):
    name= path + "\\" + name
    df_storm.to_csv(name, sep=',')

#----Function 8: Save Results in raster form, as .txt files
###Function receives 2 3D matrices, one for the monthly R factors and another with the yearly R factors.
# Each array corresponds to a different month-year combination in te R_3D_monthly raster and for each year in the R_3D_years raster
#There must be a total of #uniquemonths * #uniqueyears arrays in the 3D_months array and the raster name corresponds to the month-year ocmbination
#There must be a total of #uniqueyears arrays in the R_3D_array, and the raster name corresponds only to the year
#The monthly raster's saving order MUST be the same as the 3D Array saving order (first iterate thru years then thru months)
def SaveRaster(R_3D_month, R_3D_years, path):
    k=0 #to iterate through the 3D arrays
    df_head = pd.DataFrame(
        [['ncols', int(original_columns)], ['nrows', int(original_rows)], ['xllcorner', xllcorner], ['yllcorner', yllcorner],
         ['cellsize', cellsize], ['nodata_value', -9999.000000]])  # Header for .txt file
    for y in range(0, len(unique_years)): #for each year to be analyzed, obtained from the MonthYear function
        for m in range(0, len(unique_months)): #for each month to be analyzed, obtained from the MonthYear function
            # Save the monthly R Factors in a Raster .txt ASCII file
            name = path + "\\"+str(unique_months[m]) + "_" + str(unique_years[y]) + ".txt" #Txt File name corresponds to month_year
            save_raster = np.reshape(R_3D_month[k, :, :], (int(R_3D_month.shape[1]), int(R_3D_month.shape[2])))  # save each array (i) in its own 2D matrix,                                                                                                    # to later change to 3D array
            df_raster = pd.concat([df_head, pd.DataFrame(save_raster)], axis=0)
            # print("Save Raster: ", name)
            df_raster.to_csv(name, header=False, index=False, sep='\t', na_rep="")
            k += 1
        #Save the yearly R Factors in a Raster .txt ASCII file
        name = path + "\\"+ str(unique_years[y]) + ".txt" #Txt File name corresponds to month_year
        save_raster = np.reshape(R_3D_years[y, :, :], (int(R_3D_years.shape[1]), int(R_3D_years.shape[2])))  # save each array (i) in its own 2D matrix,                                                                                                    # to later change to 3D array
        df_raster = pd.concat([df_head, pd.DataFrame(save_raster)], axis=0)
        # print("Save Raster: ", name)
        df_raster.to_csv(name, header=False, index=False, sep='\t', na_rep="")

#----Function 7: Calculate R Factor per month
###Function receives Data Frame with information per storm, and groups the columns by month and year, and gets the sum of EI30 (R factor)
###per month for each year to determine R factor per month for each year in the record
###Function creates a copy of df_storm in order to avoid affecting the final data frame
def RFactor(df_storm):
    storm_copy = df_storm.copy() #Save a copy of data frame, so as not to modify original one
    storm_copy['Year-Month'] = pd.to_datetime(storm_copy['1']).dt.to_period('M') #add column with Year-Month combination to the copied data frame

    df_RFactor= pd.DataFrame(storm_copy.groupby(['Year-Month'], as_index=False).EI.agg(['sum'])).reset_index()
    df_RFactor = df_RFactor.rename(columns={"Year-Month": "Year-Month", "sum": "R Factor (MJ*mm/ha*h*month)"})

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
        if i<len(Station): #Doesn't enter if you have a storm at the end of time interval, and i is greater than number of rows
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

##-----Main Function 2: Turn back to raster form-----##
###Function receives file name (which corresponds to the cell's row and column in original raster), the R Factor, per month, for each cell, and a 3D array
###Each array corresponds to a month-year, and in each array, the function substitutes the row and column with the corresponding R factor for the given month
def ThreeDArray(name, df_month, R_3D_months, R_3D_years):
    rc = re.findall("\d+", name)  # "rc[0] is the original row and rc[2] is the original column"
    k=0; #to iterate through each 3D array
    while k<R_3D_months.shape[0]: #while k counter is less than max number of arrays
        for y in range (0,len(unique_years)): #for each year to be analyzed
            for m in range (0,len(unique_months)): #for each month to be analyzed
                # From MonthYear function results, save to a date-Time object for the given combination y-m
                date = datetime.datetime.strptime(str(int(unique_years[y])) + "-" + str(int(unique_months[m])), '%Y-%m')
                #Lookup in the df_month data frame the value whose month and year correspond to "date" value.
                # The "add function is used, but there should only be  1 value per year-month combo
                # value = df_month.loc[(df_month['Year-Month']==date), 'R Factor (MJ*mm/ha*h*month)'].sum() ##This code is substituted with the one below, which works in all cases
                value = df_month.loc[(df_month['Year-Month'].dt.month == date.month) & (
                            df_month['Year-Month'].dt.year == date.year), 'R Factor (MJ*mm/ha*h*month)'].sum()
                R_3D_months[k,int(rc[0]), int(rc[2])] = value #save value to the corresponding row-column in 3D array
                k += 1
            #For each year, sum the monthly values and save it to the corresponding row-column in 3D array
            R_3D_years[y, int(rc[0]), int(rc[2])] = df_month.loc[(df_month['Year-Month'].dt.year==date.year), 'R Factor (MJ*mm/ha*h*month)'].sum()
            # print("For year ", unique_years[y], "the sum is: ", R_3D_years[y, int(rc[0]), int(rc[2])])
    return R_3D_months, R_3D_years

##--------MAIN CODE--------##

##-----USER INPUT-----##

#Storm Event Input#
time_interval= 60 #-User can input if time interval is 5 min, 10 min, 30 min or 60 min
min_6Hours= 1.27 #-User can input min precipitation value (in mm) in a 6 hour period (if 0, all storm end when, in 6 hours, the sum is 0)
min_P= 12.7 #-User can input min total precipitation in order to consider it an erosive storm (if 0, all storms are valid)
CF=True #-User decides, if interval is of 60 min, if they want to use the R factor conversion factor

#Temperature Input#
min_temp=-1 #Minimum temperature (very low temperatures indicate that all temperature values are taken into account)

#Original Raster Information
original_rows = 115
original_columns = 170
xllcorner = 350000.000000
yllcorner = 4445000.000000
cellsize = 1000

#Folder Directories
path = r'C:\Users\Oreamuno\Desktop\Banja Reservoir\RFactor_5\Test1'
save_path_storm= r'C:\Users\Oreamuno\Desktop\Banja Reservoir\RFactor_5\Test1\01_ByStorm'
save_path_month=r'C:\Users\Oreamuno\Desktop\Banja Reservoir\RFactor_5\Test1\02_ByMonth'
save_path_raster= r'C:\Users\Oreamuno\Desktop\Banja Reservoir\RFactor_5\Test1\03_ByRaster'

#-----CODE-----#
CheckInput(time_interval, min_6Hours, min_P, CF) #Checks user input to make sure they are correct

filenames=glob.glob(path+"\*.csv") #Get all the .csv files in the input folder, and save the names in a list, to iterate thru them
i=0 #to iterate in file names

#From ONE input file, determine the amount of months and years in the record data.
Station=pd.read_csv(filenames[i], delimiter=',')
unique_months, unique_years = MonthYear(Station) #get vectors with the months and years in the data record

#Check that the time interval for ONE input file coincides with user time interval input (and assume it is the same with the rest of the files)
CheckTimeInterval(time_interval, np.array(Station))

# 3D Arrays to save the monthly results in a 3D array, to create the rasters with the R factor--#
#The raster must be large enough to receive a value for each month in each year within the record
R_3D_months= np.full(((len(unique_months)*len(unique_years), original_rows, original_columns)), -9999.0)
R_3D_years = np.full(((len(unique_years), original_rows, original_columns)), -9999.0)

for file in filenames:
    Station=np.array(pd.read_csv(file, delimiter=',')) #Save data from each .csv file into a Numpy Array [assumes input file has a header row, which must be ignored)
    name = os.path.basename(filenames[i]) #Get name of the file, including file extension
    print("File: ", name)

    #Generate the R factor per storm per cell (df_storm) and R factor per month per cell (df_month)
    df_storm, df_month = StormID(Station, time_interval, min_6Hours, min_P, CF, min_temp)

    #To save data per storm and per month files in .csv form, for each raster cell
    SaveCSV(df_storm,name, save_path_storm)
    SaveCSV(df_month, name, save_path_month)

    #To save R Factor in 3D array, in order to create the Raster
    # time_3d_1=time.time()
    R_3D_months, R_3D_years = ThreeDArray(name, df_month, R_3D_months, R_3D_years)
    # print("3D array part lasted: ", time.time() -time_3d_1)

    i+=1 #Add to counter

#To save resulting rasters, one per month, in a raster-format .txt file
print("Saving raster files")
SaveRaster(R_3D_months, R_3D_years ,save_path_raster)



print('My program took ', time.time()-start_time, " to run.")