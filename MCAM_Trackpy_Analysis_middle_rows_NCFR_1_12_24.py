
from __future__ import division, unicode_literals, print_function  # for compatibility with Python 2 and 3

import matplotlib as mpl
import matplotlib.pyplot as plt

import os
from pathlib import Path
import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience

import pims
import trackpy as tp

import sys

from owl.instruments import MCAM
import owl
from tqdm import tqdm
from functools import partial
print(owl.__version__)
from owl import sys_info
from pprint import pprint

# owl.mcam_data.load(directory: Path, *, delayed=None, progress=True, scheduler='threading', update=True, **_kwargs)
from owl import mcam_data

## 1) Parameters governing loading and tracking
############################################

data_path = r"../Data/12_29_23"
root_directory = os.path.abspath(data_path) + '//'

data_filename=r'Date_ExerpimentID_trialnumber.nc'


date='12_29_23'

trial_n=1

analyze_subset = True  # if this is True, it will only analyze frames starting at frames_to_analyze_start
# going to frames_to_analyze_end. Check in the image sequence if there was any moving of the chamber at beginning or end.

frames_to_analyze_start = 1  # first frame to analyze
frames_to_analyze_end = 1200 # last frame to analyze

minimal_mass_base = 150  # threshold to use for mass (total brightness of an particle= number of pixels * their intensities)
# so for example, a 3x3 pixel sized volvox with each of a max intensity of 255 (8bit) would have a mass of 9*255=2295

Volvox_pixel_size_estimate = 9  # err on the larger side

link_distance_pixels = 10  # number of pixels to try link trajectories between frames (=distance Volvox move between frames)
# need only be larger than 10 if we are undersampling. the larger this distance, the longer the analysis takes.

link_memory = 5  # number of frames to try link trajectories (=number of frames Volvox could disappear in frames)
# need only be larger than 5 for partial illumination conditions like the fixed and random series, but 5 should work too
# again,  the higher this value, the longer the analysis takes, and very large values will actually cause an error

## 2) Parameters governing filtering trajectories by various characteristics
#########################################################################

filter_stubs_size = 1  # filter out trajctories of things that only appear of x number of frames

# for mass and size, look at plot and imagej
minimal_mass = 150  # threshold to use for mass (total brightness of an particle= number of pixels * their intensities)

filter_by_size = False  # True or False to filter by size
min_size = 1
max_size = 3

filter_by_ecc = False  # True or False to filter by eccentricity (non circular shape)
max_ecc = 0.5

filter_by_stds = True  # True or False to filter by how much variation you would expect in position in x
# This filters out non-moving objects.
filter_std = 2

filter_by_frame_count = False  # True or False to filter by how many frames are contained in one trajectory
# This filters out Volvox that disappeared, but also removes broken up trajectories (i.e. if the linking failed)
filter_frame_count = 50

## 3) Parameters for counting and plotting
#########################################################################

#new sensor dimension is 2304x2304
# midpoint_x = 1152  # midpoint in pixel x coordinates of the chamber width in the original, uncompressed image
# midpoint_y = 1152  # midpoint in pixel x coordinates between the 2 chambers in the original, uncompressed image

# howeever, after binning with 4, dimension is 576x576
midpoint_x = 288  # midpoint in pixel x coordinates of the chamber width in the original, uncompressed image
midpoint_y = 288  # midpoint in pixel x coordinates between the 2 chambers in the original, uncompressed image

quartiles = False  # if True, is counts volvox in quartile ends of the chamber instead of halfs for more prounced bias counts

chamber_width = 1500  # chamber width in pixels of the chamber in the original, uncompressed image
chamber_height = 780  # chamber height in pixels of the chamber in the original, uncompressed image

save_plots = True  # Do you want to save the plots?

gaussian_smooth = True  # True or False for gaussian smoothing of the Volvox count graph over time
sigma = 15  # frames to average over for gaussian smoothing

fps = 4  # frames per second of video taking (as in what was your framerate during acquisition)

plot_1st_chamber = True  # True or False to plot the left-right bias counts
plot_2nd_chamber = True  # True or False to plot the top-bottom bias counts


dataset = mcam_data.load(root_directory+data_filename)


sub_folder_name = date+'_trial_'+str(trial_n)
subfolder_path = root_directory +sub_folder_name +'/'

if not os.path.isdir(subfolder_path):
    os.makedirs(subfolder_path)

#From left to right
column_light_conditions_top=['Switching s - Top', 'Switching 1-s - Top', 'Fixed 1Hz', 'Random', 'Fixed 1Hz', 'Fixed 2Hz']
column_light_conditions_bottom=['Switching s - Bottom', 'Switching 1-s - Bottom','Random', 'Fixed 1Hz', 'Fixed 2Hz', 'Fixed 1Hz']

# from bottom to top (y direction of sensors)
row_conditions=['Control', 'Pattern']

# Left-Right Media Conditions
left_right_media_condition2=['Normal','Continuous']
left_right_media_condition1=['Fixed','Random']


df_mean_Vnum=pd.DataFrame(index=None, columns=['Date', 'Trial', 'Light Condition Top','Light Condition Bottom','Row Condition','Media Condition','Average Number Volvox Top','Average Number Volvox Bottom'], dtype=None, copy=None)

cameras_to_process_y=[0,1]
cameras_to_process_x=[0,1,2,3,4,5]

for camera_y in cameras_to_process_y:
    for camera_x in cameras_to_process_x:

        camera_position_x=camera_x
        camera_position_y=camera_y

        camera_name='Camera_x_'+str(camera_position_x)+'_y_'+str(camera_position_y)

        # Labels for the individual stimulation condtions (light pattern, anode/cathode side etc.)
        label_left_chamber_top = "Left Chamber - " + column_light_conditions_top[camera_position_x]
        label_left_chamber_bottom = "Left Chamber - " + column_light_conditions_bottom[camera_position_x]
        label_right_chamber_top = "Right Chamber - " + column_light_conditions_top[camera_position_x]
        label_right_chamber_bottom = "Right Chamber - " + column_light_conditions_bottom[camera_position_x]

        frames_xarray=dataset['images'][:, camera_position_x, camera_position_y]
        frames= np.asarray(frames_xarray)
        f = tp.locate(frames[frames_to_analyze_start], int(33), invert=False)
        f.head()

        tp.annotate(f, frames[frames_to_analyze_start]);

        directory_new=root_directory

        graph_folder=subfolder_path+'Graphs/'
        data_folder=subfolder_path+'Data/'

        if not os.path.isdir(data_folder):
            os.makedirs(data_folder)
        if not os.path.isdir(graph_folder):
            os.makedirs(graph_folder)

        textfile = open(data_folder+ camera_name+'_print_output.txt', "a")


        if analyze_subset:
            f = tp.batch(frames[frames_to_analyze_start:frames_to_analyze_end], int(Volvox_pixel_size_estimate),
                         minmass=minimal_mass_base, invert=False);
        else:
            f = tp.batch(frames, int(Volvox_pixel_size_estimate), minmass=minimal_mass, invert=False);


        f.to_csv(data_folder+ camera_name+'_frames.csv')
        print(f.columns)


        t = tp.link_df(f, link_distance_pixels, memory=link_memory)

        t.to_csv(data_folder+ camera_name+'_trajectories_raw.csv')

        t.head()
        t1 = tp.filter_stubs(t, filter_stubs_size)
        plt.figure()

        tp.mass_size(t1.groupby('particle').mean());  # convenience function -- just plots size vs. mass

        import math

        if filter_by_size:
            if filter_by_ecc:
                t2 = t1[
                    ((t1['mass'] > minimal_mass) & (t1['size'] > min_size) & (t1['size'] < max_size) & (t1['ecc'] < max_ecc))]
            else:
                t2 = t1[((t1['mass'] > minimal_mass) & (t1['size'] > min_size) & (t1['size'] < max_size))]
        else:
            if filter_by_ecc:
                t2 = t1[((t1['mass'] > minimal_mass) & (t1['ecc'] < max_ecc))]
            else:
                t2 = t1[((t1['mass'] > minimal_mass))]
        print('particles filter by size/mass/ecc =', len((list(set(t1.particle))))- len((list(set(t2.particle)))), 'out of',
              len((list(set(t1.particle)))), file=textfile)

        if filter_by_stds:

            t2p5 = t2.copy()
            std = t2.groupby(['particle']).std()
            std.reset_index(level=0, inplace=True)

            list_set = set(t2.particle)
            unique_list = (list(list_set))
            unique_list.sort()
            for i in unique_list:
                std_x = float(std.loc[std.particle == i, 'x'])
                if std_x < filter_std:
                    t2p5 = t2p5[t2p5['particle'] != i]
                elif math.isnan(std_x):
                    t2p5 = t2p5[t2p5['particle'] != i]

            len((list(set(t2p5.particle))))
            print('particles filter by stds =', len((list(set(t2.particle)))) - len((list(set(t2p5.particle)))), 'out of',
                  len((list(set(t2.particle)))), file=textfile)
            t2 = t2p5.copy()

        t3 = t2.copy()

        if filter_by_frame_count:
            list_set = set(t3.frame)
            unique_list = (list(list_set))
            unique_list.sort()
            for i in unique_list:
                t3i = t3[t3.frame == i]
                if t3i.frame.count() < filter_frame_count:
                    t3 = t3[t3['frame'] != i]

            print('particles filter by frame count =', len((list(set(t2.particle)))) - len((list(set(t3.particle)))), 'out of',
                  len((list(set(t2.particle)))), file=textfile)

        plt.figure()
        tp.annotate(t3[t3['frame'] == frames_to_analyze_start], frames[frames_to_analyze_start]);
        fig = plt.figure(figsize=(7, 4))
        tp.plot_traj(t3);

        if save_plots:
            save_path = graph_folder+ camera_name+ '_Volvox_trajectories_graph.png'
            fig.savefig(save_path, bbox_inches='tight')


        t4 = t3.copy()

        t4.to_csv(data_folder+ camera_name+ '_trajectories_filtered.csv')

        list_set = set(t4.frame)
        unique_list = (list(list_set))
        unique_list.sort()

        lt = np.zeros(len(unique_list))
        lb = np.zeros(len(unique_list))

        rt = np.zeros(len(unique_list))
        rb = np.zeros(len(unique_list))

        # print(unique_list)
        ii = 0
        for i in unique_list:
            t5 = t4.loc[t4.frame == i]

            t_left_top= t5.loc[(t5.y < midpoint_y+1) & (t5.x > midpoint_x)]
            t_left_bottom = t5.loc[(t5.y < midpoint_y+1) & (t5.x < midpoint_x+1)]

            t_right_top = t5.loc[(t5.y > midpoint_y) & (t5.x > midpoint_x)]
            t_right_bottom = t5.loc[(t5.y > midpoint_y) & (t5.x < midpoint_x+1)]

            lt[ii] = t_left_top.shape[0]
            lb[ii] = t_left_bottom.shape[0]

            rt[ii] = t_right_top.shape[0]
            rb[ii] = t_right_bottom.shape[0]

            ii = ii + 1

        print('mean # left top ('+label_left_chamber_top+') : ', lt.mean(), file=textfile)
        print('mean # left bottom ('+label_left_chamber_bottom+') : ', lb.mean(), file=textfile)

        print('mean # right top ('+label_right_chamber_top+') : ', rt.mean(), file=textfile)
        print('mean # right bottom ('+label_right_chamber_bottom+') : ', rb.mean(), file=textfile)

        if camera_y==0:
            left_right_media_condition=left_right_media_condition1
        elif camera_y==1:
            left_right_media_condition = left_right_media_condition2
        data_line_left = pd.DataFrame([{'Date': date, 'Trial': trial_n,
                                            'Light Condition Top': column_light_conditions_top[camera_position_x],
                                            'Light Condition Bottom': column_light_conditions_bottom[camera_position_x],
                                            'Row Condition': row_conditions[camera_position_y],
                                            'Media Condition': left_right_media_condition[0],
                                            'Average Number Volvox Top':lt.mean(), 'Average Number Volvox Bottom':lb.mean()}])
        data_line_right = pd.DataFrame([{'Date': date, 'Trial': trial_n,
                                            'Light Condition Top': column_light_conditions_top[camera_position_x],
                                            'Light Condition Bottom': column_light_conditions_bottom[camera_position_x],
                                            'Row Condition': row_conditions[camera_position_y],
                                            'Media Condition': left_right_media_condition[1],
                                            'Average Number Volvox Top':rt.mean(), 'Average Number Volvox Bottom':rb.mean()}])


        df_mean_Vnum = pd.concat([df_mean_Vnum, data_line_left,data_line_right], ignore_index=True)


        import scipy as sp

        if gaussian_smooth:
            l = sp.ndimage.gaussian_filter1d(lt, sigma)
            r = sp.ndimage.gaussian_filter1d(lb, sigma)
            t = sp.ndimage.gaussian_filter1d(rt, sigma)
            b = sp.ndimage.gaussian_filter1d(rb, sigma)

        unique_list_time = np.array(unique_list) / fps

        fig = plt.figure(figsize=(7, 4))

        if plot_1st_chamber:
            ax = plt.plot(unique_list_time, lt, "-b", label=label_left_chamber_top)
            ax = plt.plot(unique_list_time, lb, "--b", label=label_left_chamber_bottom)

        if plot_2nd_chamber:
            ax = plt.plot(unique_list_time, rt, "-r", label=label_right_chamber_top)
            ax = plt.plot(unique_list_time, rb, "--r", label=label_right_chamber_bottom)
        ax = plt.legend(bbox_to_anchor=(1, 1), loc="upper left")
        ax = plt.xlabel('time (in s)')
        ax = plt.ylabel('number of Volvox')
        #plt.show()

        if quartiles:
            save_path = graph_folder+ camera_name+'_Volvox_counts_line_graph_quartiles.png'
        else:
            save_path = graph_folder+ camera_name+ '_Volvox_counts_line_graph.png'

        if save_plots:
            fig.savefig(save_path, bbox_inches='tight')

        textfile.close()

df_mean_Vnum.to_csv(subfolder_path+'Average_Volvox_numbers_all_cameras')