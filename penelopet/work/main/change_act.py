import numpy as np
activity = 1e3*1e3

make_new_act=False
if make_new_act:
    SIZE = [51]*3
    STEP = [0.15]*3

    NXM, NYM, NZM = SIZE[0]//2+1, SIZE[1]//2+1, SIZE[2]//2+1
    xx, yy, zz = np.meshgrid(np.arange(-NXM+1, NXM)*STEP[0],
                            np.arange(-NYM+1, NYM)*STEP[1],
                            np.arange(-NZM+1, NZM)*STEP[2])
    
    ###source activity geometry
    POS = (0.0, 0.0, 0.0)    #cm

    # spherical (punctual if RADIUS=0)
    RADIUS = 1.0          #cm
    bool_vol = np.sqrt((xx-POS[0])**2 + (yy-POS[1])**2 + (zz-POS[2])**2) <= RADIUS
    ACTIVITY = activity * bool_vol.astype(np.float32)
    ACTIVITY.tofile('source.raw', format="%f")

with open("source.raw", 'rb') as f:
    raw_data = np.fromfile(f, dtype='float32')
#raw_data[raw_data>0] = activity
print("Actividad total: %.4e" % np.sum(raw_data))
raw_data.tofile("source.raw", format="%f")
