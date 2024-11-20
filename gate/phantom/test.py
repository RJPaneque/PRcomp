import numpy as np
activity = 1e9

SIZE = [201]*3
STEP = [0.003]*3

NXM, NYM, NZM = SIZE[0]//2+1, SIZE[1]//2+1, SIZE[2]//2+1
xx, yy, zz = np.meshgrid(np.arange(-NXM+1, NXM)*STEP[0],
                        np.arange(-NYM+1, NYM)*STEP[1],
                        np.arange(-NZM+1, NZM)*STEP[2])

###source activity geometry
POS = (0.0, 0.0, 0.0)    #cm

# spherical (punctual if RADIUS=0)
RADIUS = 0.0          #cm
bool_vol = np.sqrt((xx-POS[0])**2 + (yy-POS[1])**2 + (zz-POS[2])**2) <= RADIUS
bool_vol.astype(np.uint16).tofile('ACTIVITY.i33', format="%d")

MATERIAL = np.ones(SIZE)
MATERIAL[xx<0] = 5
MATERIAL[xx>=0] = 5
MATERIAL.astype(np.uint16).tofile('MATERIAL.i33', format="%d")


