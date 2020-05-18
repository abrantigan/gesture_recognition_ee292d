##### Attempt at drawing accelerometer data 

import serial 
import numpy as np # Import numpy
import matplotlib
import matplotlib.pyplot as plt #import matplotlib library
import matplotlib.animation as animation
from matplotlib import style
import time


################## Draw live data ##################
style.use('fivethirtyeight') 

# Initialize figure
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

# Creating our serial object named arduinoData
arduinoData = serial.Serial('/dev/tty.usbmodem14101', 9600) 

# Initialize program variables 
prevs = {'prev_x':0,'prev_y':0,'prev_z':0,'prev_ax':0,'prev_ay':0,'prev_az':0}
xs = []
ys = []
alpha = .5
ms_delay = 100 # number of milliseconds between graph update
dt = ms_delay / 1000.0 # time passed between position updates in seconds
max_display_len = 50 



def animate(i):
    while (arduinoData.inWaiting()==0): #Wait here until there is data
        pass # do nothing
    
    arduinoString = arduinoData.readline() #read the line of text from the serial port
    dataArray = np.array(arduinoString.decode().replace('\r\n','').split('\t')).astype(np.float)   #Split it into an array called dataArray
    print(dataArray)

    buttonPressed = dataArray[0]

    if buttonPressed:
    	# Get most recent measurements 
        ax, ay, az = dataArray[1], dataArray[2], dataArray[3]
        ay *= -1 # did this because my Arduino is facing backwards. might not need it
        az -= .98 # zero center/account for gravity

        # Combine current and prev measurements to help with noise 
        ax = alpha * ax + (1 - alpha) * prevs['prev_ax']
        ay = alpha * ay + (1 - alpha) * prevs['prev_ay']
        az = alpha * az + (1 - alpha) * prevs['prev_az']

        # Integrate acceleration to get position
        posx = np.sign(ax) * ax ** 2 / 2.0 * dt + prevs['prev_x']
        posy = np.sign(ay) * ay ** 2 / 2.0 * dt + prevs['prev_y']
        posz = np.sign(az) * az ** 2 / 2.0 * dt + prevs['prev_z']

        # Add to data points to be displayed, accounting for different coordinate systems between arduino imu and real world
        xs.append(posy) 
        ys.append(posz) 
        
        # update previous values
        prevs['prev_x'], prevs['prev_y'], prevs['prev_z'] = posx, posy, posz
        prevs['prev_ax'], prevs['prev_ay'], prevs['prev_az'] = ax, ay, az
        ax1.clear()

        # wanted to only draw most recent 50 samples, but this needs to be improved
        ax1.plot(xs[min(0, len(xs)-max_display_len):], ys[min(0, len(ys)-max_display_len):])

    else:
        # Todo: Erase data to only show data from current sample
        # prevs['prev_x'], prevs['prev_y'], prevs['prev_z'] = 0, 0, 0
        # prevs['prev_ax'], prevs['prev_ay'], prevs['prev_az'] = 0, 0, 0
        ax1.clear()



def main():
    ani = animation.FuncAnimation(fig, animate, interval=ms_delay)
    plt.show()

    arduinoData.close()


if __name__ == "__main__":
    main()


