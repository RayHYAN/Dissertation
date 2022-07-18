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
EEG_channels = {1:"Fpz-O1", 2:"Fpz-O2", 3:"Fpz-F7", 4:"F8-F7", 5:"F7-01", 6:"F8-O2", 7:"Fpz-F8"}

if __name__ == '__main__':
    # Load EEG and E4 (physiological data)
    EEG_files, E4_files = data_load_save.set_up()

    for part in EEG_files.keys():
        EEG_event, window = 'familiar_music', 3
        _json_path = f'./data/dosed/edf_json/{window}s/{part}_{EEG_event}_{window}s.json'
        EEG_files[part].event_details.save_event_window_to_json(EEG_event, _json_path, window)

    # EEG_partID, EEG_event = 'VG_01', 'familiar_music'
    # _json_path = f'./data/dosed/edf_json/{EEG_partID}_{EEG_event}_3s.json'
    # EEG_files[EEG_partID].event_details.save_event_window_to_json(EEG_event, _json_path, 3)

    # Visualize VG data (EEG 250Hz)
    EEG_partID, EEG_channel, EEG_event = 'VG_06', 'Fpz-O1', 'familiar_music'
    plt.plot(EEG_files[EEG_partID].get_EEG_by_channel_and_event(EEG_channel, EEG_event))

    # Visualize E4 data (physiological data)
    E4_partID, E4_file, E4_event = 'VG_01', 'HR', 'exper_video'
    plt.plot(E4_files[E4_partID].get_E4_by_filename_and_event(E4_file, E4_event))

    plt.show()
