import serial # import Serial Library
import numpy as np # Import numpy
import matplotlib
import matplotlib.pyplot as plt #import matplotlib library
import time
import csv

##### Run this before starting data collection!
arduinoData = serial.Serial('/dev/tty.usbmodem14501', 9600) #Creating our serial object named arduinoData

# dataLabeled = np.append(dataArray_ALL, np.ones((dataArray_ALL.shape[0],1)), axis=1)
# field names  
fields = ['button', 'x', 'y', 'z'] 
name='lauren'
letter='M'
iterNum=1; #### TODO: update this based on most recent data number
iterStart = iterNum
numIters = 10
# name of csv file  

while iterNum < iterStart + numIters:   
    input("Press any key to begin...")

    dataArray_ALL = np.empty((1,4)) ##fixed length based on samples
    t_end = time.time() + 10

    while time.time() < t_end:
        while (arduinoData.inWaiting()==0): #Wait here until there is data
            pass #do nothing
    
        arduinoString = arduinoData.readline() #read the line of text from the serial port
        dataArray = np.array(arduinoString.decode().replace('\r\n','').split('\t')).astype(np.float)   #Split it into an array called dataArray
        print(dataArray)

        # Seperate csv for every sample, or .mat files all together
        dataArray_ALL = np.append(dataArray_ALL, dataArray.reshape(1,-1), axis=0) 
    
    filename = letter+'_'+ name + '_'+str(iterNum) + ".csv"
    np.savetxt(filename, dataArray_ALL, delimiter=',')

    print("Data saved to: ", filename)
    iterNum += 1

###### Run this after finishing data collection!
arduinoData.close()