from owl.instruments import MCAM
import owl
from tqdm import tqdm
from functools import partial
print(owl.__version__)
from owl import sys_info
from pprint import pprint
import numpy as np
import serial
import time

# Output directory
save_path = r"../Data/Output"
save_dir = os.path.abspath(save_path) + '//'

if not os.path.exists(save_dir):
    # Create the directory if it does not exist
    os.makedirs(save_dir)

output_filename=r'Date_ExerpimentID_trialnumber.nc'

# check wich port the Arduino is set to right now
ser = serial.Serial('/dev/ttyUSB1', 9600)
ser.write(str.encode('0'))
time.sleep(1)

subset_bol=False
selection_slice = np.s_[0:6, 1:3] # x and y, where x goes left to right, and y goes bottom to top
minutes = 7

pprint(sys_info())
with MCAM() as mcam:
    mcam.select_center_pixels((2304, 2304), step=4)
    # mcam.select_center_pixels((3072, 3072), step=2)
    mcam.frame_rate_setpoint = 4
    mcam.exposure = 240E-3
    mcam.digital_gain=5
    mcam.analog_gain=1.5
    if abs(mcam.frame_rate - mcam.frame_rate_setpoint) > 0.01:
        raise RuntimeError("Exposure too long for desired frame rate.")
    # minutes = 0.05

    N_frames = int(mcam.frame_rate * 60 * minutes + 1)

    print(f"{mcam.maximum_datarate / 1024 ** 3:.2f} GiB/s")
    print(f"Capturing {N_frames} frames for a {minutes} minute capture at {mcam.frame_rate} fps")
    if subset_bol:
        selection = np.zeros(mcam.N_cameras, dtype=bool)
        selection[selection_slice] = True

        mcam.allocate_video_buffer(N_frames=N_frames, selection=selection, tqdm=tqdm)
        ser.write(str.encode('1'))
        time.sleep(0.5)
        ser.write(str.encode('1'))
        video_dataset = mcam.acquire_high_speed_video(N_frames, selection_slice=selection_slice, tqdm=tqdm)
    else:
        mcam.allocate_video_buffer(N_frames=N_frames, tqdm=tqdm)
        ser.write(str.encode('1'))
        time.sleep(0.5)
        ser.write(str.encode('1'))
        video_dataset = mcam.acquire_high_speed_video(N_frames=N_frames, tqdm=tqdm)

    ser.write(str.encode('0'))
    time.sleep(1)
    ser.write(str.encode('0'))
    time.sleep(1)
    ser.write(str.encode('0'))
    time.sleep(1)
    ser.write(str.encode('0'))
    time.sleep(1)
    ser.write(str.encode('0'))
    # Save the data
    tqdm_save = partial(tqdm, desc="Saving data")

    # saved_path = None

    saved_path = owl.mcam_data.save_video(video_dataset,save_dir+output_filename, tqdm=tqdm_save)

    print(f"Data saved to {saved_path}")

    # %% View the acquired data
    #quickview(mcam.dataset)