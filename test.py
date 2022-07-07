# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 18:09:32 2022

@author: Zerui Mu
"""

import os, time
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# import data_setup
import data_load_save

E4_file_names = ['ACC', 'BVP', 'EDA', 'HR', 'IBI', 'TEMP'] # physiological data, tags.csv not included
VG_file_names = { # 1&5, 2&6, 3&4 similar, EEG data (1-7)
    0: 'Accelero Norm',
    1: 'EEG Fpz-O1',
    2: 'EEG Fpz-O2',
    3: 'EEG Fpz-F7',
    4: 'EEG F8-F7',
    5: 'EEG F7-01',
    6: 'EEG F8-O2',
    7: 'EEG Fpz-F8',
    8: 'Positiongram', # not exist in VG_01, VG_02, VG_03, VG_05; in these files, we need to change index (9-13) to (8-12)
    9: 'PulseOxy Infrare',
    10: 'PulseOxy Red Hea',
    11: 'Respiration x',
    12: 'Respiration y',
    13: 'Respiration z'
}

if __name__ == '__main__':
    # Load EEG and E4 (physiological data)
    EEG_files, E4_files = data_load_save.set_up()
    #plt.plot(EEG_files[''])

    # Visualize VG data (EEG 250Hz)
    # EEG_partID, EEG_channel, EEG_event = 'VG_06', 'Fpz-O1', 'familiar_music'
    #plt.plot(EEG_files[EEG_partID].get_EEG_by_channel_and_event(EEG_channel, EEG_event))
    # X = EEG_files[EEG_partID].get_EEG_by_channel_and_event(EEG_channel, EEG_event)
    channels = [1,2,3,4,5,6,7]
    EEG_partID = 'VG_01'
    EEG_event = 'familiar_music'

    persons = ['VG_01', 'VG_02', 'VG_03', 'VG_05', 'VG_06', 'VG_07', 'VG_08','VG_09', 'VG_10', 'VH_01', 'VH_02', 'VH_03']
    EEG_data_person =[]
    for person in persons:
        for channel in channels:
            channel_data = EEG_files[EEG_partID].get_EEG_by_channel_and_event(channel, EEG_event)
            EEG_data_person.append(channel_data)
        
    EEG_data_person = np.array(EEG_data_person)
    print(EEG_data_person)
    print(EEG_data_person.shape)
    print(type(EEG_data_person))


    # # Visualize E4 data (physiological data)
    # E4_partID, E4_file, E4_event = 'VG_01', 'HR', 'exper_video'
    # plt.plot(E4_files[E4_partID].get_E4_by_filename_and_event(E4_file, E4_event))

    #plt.show()    