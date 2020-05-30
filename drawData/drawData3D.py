##### Attempt at drawing accelerometer data 

import serial 
import numpy as np # Import numpy
import matplotlib
import matplotlib.pyplot as plt #import matplotlib library
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import style
import time

################## Draw live data ##################

# Creating our serial object named arduinoData
arduinoData = serial.Serial('/dev/tty.usbmodem14101', 9600) 

class GestureRemote:
    def __init__(self, ms_delay, alpha=.5, max_display_len=50):
        self.alpha = alpha
        self.max_display_len = max_display_len
        self.xs = [0] * max_display_len
        self.ys = [0] * max_display_len
        self.zs = [0] * max_display_len
        self.dt = ms_delay / 1000.0 # seconds
        self.prevs = {'prev_x':0,'prev_y':0,'prev_z':0,'prev_ax':0,'prev_ay':0,'prev_az':0}

    # Update xs, ys, zs, prevs incorporating new data
    def step(self):
        while (arduinoData.inWaiting()==0): #Wait here until there is data
            pass # do nothing

        bytesToRead = arduinoData.inWaiting()
        fullString = arduinoData.read(bytesToRead)
        arduinoString = fullString.splitlines()[-2] #Last full reading
        dataArray = np.array(arduinoString.decode().replace('\r\n','').split('\t')).astype(np.float)   #Split it into an array called dataArray
        buttonPressed = dataArray[0]
        print("dataArray: ", dataArray)

        if buttonPressed:
            # Get most recent measurements 
            ax, ay, az = dataArray[1], dataArray[2], dataArray[3]
            az -= .98 # zero center/account for gravity 

            # Combine current and prev measurements to help with noise 
            ax = self.alpha * ax + (1 - self.alpha) * self.prevs['prev_ax']
            ay = self.alpha * ay + (1 - self.alpha) * self.prevs['prev_ay']
            az = self.alpha * az + (1 - self.alpha) * self.prevs['prev_az']

            MIN_ACCEL_THRESH = .05 # trying this out to prevent noise around zero causing movements when there aren't any
            if abs(ax) < MIN_ACCEL_THRESH: ax = 0
            if abs(ay) < MIN_ACCEL_THRESH: ay = 0
            if abs(az) < MIN_ACCEL_THRESH: az = 0

            # Integrate acceleration to get position
            posx = np.sign(ax) * ax ** 2 / 2.0 * self.dt + self.prevs['prev_x']
            posy = np.sign(ay) * ay ** 2 / 2.0 * self.dt + self.prevs['prev_y']
            posz = np.sign(az) * az ** 2 / 2.0 * self.dt + self.prevs['prev_z']

            # Add to data points to be displayed, accounting for different coordinate systems between arduino imu and real world
            self.xs.append(posx) 
            self.ys.append(posy) 
            self.zs.append(posz)
            
            # update previous values
            self.prevs['prev_x'], self.prevs['prev_y'], self.prevs['prev_z'] = posx, posy, posz
            self.prevs['prev_ax'], self.prevs['prev_ay'], self.prevs['prev_az'] = ax, ay, az

            self.xs = self.xs[-self.max_display_len:]
            self.ys = self.ys[-self.max_display_len:]
            self.zs = self.zs[-self.max_display_len:]

        else: 
            self.xs = [] 
            self.ys = [] 
            self.zs = [] 
            self.th_x = 0
            self.th_y = 0
            self.th_z = 0
            self.prevs = {'prev_x':0,'prev_y':0,'prev_z':0,'prev_ax':0,'prev_ay':0,'prev_az':0}
 


#------------------------------------------------------------
# set up initial state and global variables
alpha = .5
# ms_delay = 100
ms_delay = 1000 # number of milliseconds  ## CHANGE: made this larger to increase dt, then all pos values
max_display_len= 50
gestureRemote = GestureRemote(ms_delay, alpha, max_display_len)


#------------------------------------------------------------
# set up figure and animation
style.use('fivethirtyeight') 
fig = plt.figure()
ax_3D = fig.add_subplot(211, projection='3d')
ax_2D = fig.add_subplot(212)

# line, = ax1.plot([],[],lw=2) # 2d
AX_LIM = .5
def init():
    ax_3D.plot([],[],[])
    ax_3D.set_xlim3d(-AX_LIM, AX_LIM)
    ax_3D.set_ylim3d(-AX_LIM, AX_LIM)
    ax_3D.set_zlim3d(-AX_LIM, AX_LIM)
    ax_3D.set_xlabel('pos_x')
    ax_3D.set_ylabel('pos_y')
    ax_3D.set_zlabel('pos_z')
    ax_2D.plot([],[])
    ax_2D.set_xlim(-AX_LIM, AX_LIM)
    ax_2D.set_ylim(-AX_LIM, AX_LIM)
    ax_2D.set_xlabel('pos_x')
    ax_2D.set_ylabel('pos_y')


    return [ax_3D, ax_2D]

def animate(i):
    global gestureRemote

    gestureRemote.step()
    xs = gestureRemote.xs
    ys = gestureRemote.ys
    zs = gestureRemote.zs

    if len(xs) == 0:
        ax_3D.clear()
        ax_2D.clear()
    else:
        ax_3D.plot(xs,ys,zs,'g')
        ax_2D.plot(ys,zs,'g')

    ax_3D.set_xlim3d(-AX_LIM, AX_LIM)
    ax_3D.set_ylim3d(-AX_LIM, AX_LIM)
    ax_3D.set_zlim3d(-AX_LIM, AX_LIM)
    ax_3D.set_xlabel('pos_x')
    ax_3D.set_ylabel('pos_y')
    ax_3D.set_zlabel('pos_z')
    ax_2D.set_xlim(-AX_LIM, AX_LIM)
    ax_2D.set_ylim(-AX_LIM, AX_LIM)
    ax_2D.set_xlabel('pos_y')
    ax_2D.set_ylabel('pos_z')

    return [ax_3D, ax_2D]

interval = 100
ani = animation.FuncAnimation(fig, animate, interval=interval, blit=True, init_func=init)
plt.show()
arduinoData.close()


