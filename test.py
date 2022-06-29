# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 18:09:32 2022

@author: Zerui Mu
"""

import os, time
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from EEG_data import EEG_data_class, EEG_files, VG_Hz, EEG_buffer
from E4_data import E4_data_class, E4_files

data_folder = r'./CARE_HOME_DATA'
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
    8: 'Positiongram',
    9: 'PulseOxy Infrare',
    10: 'PulseOxy Red Hea',
    11: 'Respiration x',
    12: 'Respiration y',
    13: 'Respiration z'
}

if __name__ == '__main__':
    # Load and visualize VG data (EEG 250Hz)
    # EEG_partID, EEG_channel, EEG_event = 'VG_06', 'Fpz-O1', 'familiar_music'
    # plt.plot(EEG_files[EEG_partID].get_EEG_by_channel_and_event(EEG_channel, EEG_event))

    # Load and visualize E4 data (physiological data)
    E4_partID, E4_file, E4_event = 'VG_01', 'HR', 'exper_video'
    plt.plot(E4_files[E4_partID].get_E4_by_filename_and_event(E4_file, E4_event))






    # print(len(EEG_data[3])/VG_Hz)
    # EEG_timespan_eg = {
    #     'VG_05': {'break': (1860, 1890), 'BBC wildlife': (420, 450), 'Tchaikovsky': (1320, 1350)}, # 'familiar music': (1680, 1710)},
    #     'VG_06': {'break': (1920, 1950), 'BBC wildlife': (630, 660), 'Tchaikovsky': (1410, 1440)}, # 'familiar music': (1560, 1590)}},
    # }
    # for event, timespan in EEG_timespan_eg[EEG_partID].items():
    #     plot_EEG_data(EEG_data, 1, timespan[0] * VG_Hz, timespan[1] * VG_Hz, label = event)
    # plt.legend()
    plt.show()

    # Load and visualize E4 data (physiological data)
    # E4_partID, E4_file_name = 'VG_05', 'HR'
    # E4_data, E4_Hz = read_E4_file(E4_partID, E4_file_name)
    # E4_timespan_eg = {
    #     'VG_05': {'break': (2100, 2130), 'BBC wildlife': (630, 660), 'Tchaikovsky': (1530, 1560)}, # 'familiar music': (1890, 1920)},
    #     'VG_06': {'break': (1500, 1530), 'BBC wildlife': (210, 240), 'Tchaikovsky': (990, 1020)} # 'familiar music': (1140, 1170)}},
    # }
    # for event, timespan in E4_timespan_eg[E4_partID].items():
    #     plot_E4_data(E4_data, E4_file_name, timespan[0], timespan[1], label = event)
    # plt.legend()
    # plt.show()
