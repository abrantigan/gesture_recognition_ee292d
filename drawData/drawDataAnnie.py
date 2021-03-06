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
fig2 = plt.figure()
#ax1 = fig.add_subplot(1,1,1)

#Draw three subplots, one for x, y, z position
ax1 = fig.add_subplot(3,1,1)
ax2 = fig.add_subplot(3,1,2)
ax3 = fig.add_subplot(3,1,3)

# Creating our serial object named arduinoData
arduinoData = serial.Serial('/dev/tty.usbmodem14101', 9600) 

# Initialize program variables 
prevs = {'prev_x':0,'prev_y':0,'prev_z':0,'prev_ax':0,'prev_ay':0,'prev_az':0}
alpha = .5
ms_delay = 50 # number of milliseconds between graph update
dt = ms_delay / 1000.0 # time passed between position updates in seconds
max_display_len = 50 
xs = [0] * max_display_len
ys = [0] * max_display_len
zs = [0] * max_display_len
t = range(max_display_len)


def animate(i, xs, ys, zs, prevs):
    while (arduinoData.inWaiting()==0): #Wait here until there is data
        pass # do nothing
    
    # arduinoString = arduinoData.readline() #read the line of text from the serial port
    # dataArray = np.array(arduinoString.decode().replace('\r\n','').split('\t')).astype(np.float)   #Split it into an array called dataArray
    # print(dataArray)

    bytesToRead = arduinoData.inWaiting()
    fullString = arduinoData.read(bytesToRead)
    #print(fullString.splitlines())
    arduinoString = fullString.splitlines()[-2] #Last full reading
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
        xs.append(posx) 
        ys.append(posy) 
        zs.append(posz)

        #t.append(dt.datetime.now().strftime('%H:%M:%S.%f')) 
        
        # update previous values
        prevs['prev_x'], prevs['prev_y'], prevs['prev_z'] = posx, posy, posz
        prevs['prev_ax'], prevs['prev_ay'], prevs['prev_az'] = ax, ay, az
        ax1.clear()
        ax2.clear()
        ax3.clear()

        xs = xs[-max_display_len:]
        print(len(xs)-max_display_len)
        ys = ys[-max_display_len:]
        zs = zs[-max_display_len:]
        #t = range(max_display_len)

        # wanted to only draw most recent 50 samples, but this needs to be improved
        #ax1.plot(xs[min(0, len(xs)-max_display_len):], ys[min(0, len(ys)-max_display_len):])
        ax1.plot(t,xs,color='b')
        ax2.plot(t,ys,color='b')
        ax3.plot(t,zs,color='b')
        ax1.set_ylim(-2, 2)
        ax2.set_ylim(-2, 2)
        ax3.set_ylim(-2, 2)
    else:
        # Todo: Erase data to only show data from current sample
        # prevs['prev_x'], prevs['prev_y'], prevs['prev_z'] = 0, 0, 0
        # prevs['prev_ax'], prevs['prev_ay'], prevs['prev_az'] = 0, 0, 0
        ax1.clear()
        ax2.clear()
        ax3.clear()
        xs = [0] * max_display_len
        ys = [0] * max_display_len
        zs = [0] * max_display_len
        # ax1.plot(t,xs,color='b')
        # ax2.plot(t,ys,color='b')
        # ax3.plot(t,zs,color='b')
        prevs = {'prev_x':0,'prev_y':0,'prev_z':0,'prev_ax':0,'prev_ay':0,'prev_az':0}


    arduinoData.flushInput()


while (arduinoData.inWaiting()==0): #Wait here until there is data
        pass # do nothing


def main():
    ani = animation.FuncAnimation(fig, animate, fargs = (xs, ys, zs, prevs), interval=ms_delay)
    plt.show()

    arduinoData.close()


if __name__ == "__main__":
    main()


