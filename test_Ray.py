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
from Ray import data_load_save
from Ray.data_load_save import gen_EEG_traintest_to_csv_mix, gen_EEG_traintest_to_csv_part
from Ray.basic_info import motor_movement_data_folder

E4_file_names = ['ACC', 'BVP', 'EDA', 'HR', 'IBI', 'TEMP'] # physiological data, tags.csv not included
EEG_channels = {1:"Fpz-O1", 2:"Fpz-O2", 3:"Fpz-F7", 4:"F8-F7", 5:"F7-01", 6:"F8-O2", 7:"Fpz-F8"}

def gen_EEG_train_test_to_csv(event_list, multiply, func, windows = 1, train_ratio = 0.9, EEG_data = None):
    """
    func: (mix OR part)
      mix: mix all partcipants data together and separate train_set and test_set by train_ratio
      part: separate train_set and test_set by participant and the train_ratio
    """

    if func == 'mix':
        train_data, test_data, train_label, test_label = gen_EEG_traintest_to_csv_mix(event_list, multiply, windows, train_ratio, EEG_data)
    elif func == 'part':
        train_data, test_data, train_label, test_label = gen_EEG_traintest_to_csv_part(event_list, multiply, windows, train_ratio, EEG_data)
    else:
        print("Please check the function! (mix, part)")
        return None
    
    print("Generating EEG train and test dataset for EEG-DL repository!")
    train_data.to_csv(os.path.join(motor_movement_data_folder, './Ray/training_set.csv'), header=None, index=None)
    test_data.to_csv(os.path.join(motor_movement_data_folder, './Ray/test_set.csv'), header=None, index=None)
    train_label.to_csv(os.path.join(motor_movement_data_folder, './Ray/training_label.csv'), header=None, index=None)
    test_label.to_csv(os.path.join(motor_movement_data_folder, './Ray/test_label.csv'), header=None, index=None)
    return (train_data, test_data, train_label, test_label)


if __name__ == '__main__':
    # Load EEG and E4 (physiological data)
    EEG_files, E4_files = data_load_save.set_up(isEEG=True, isE4=True)

    # Visualize VG data (EEG 250Hz)
    EEG_partID, EEG_channel, EEG_event = 'VG_06', 'Fpz-O1', 'familiar_music'
    plt.plot(EEG_files[EEG_partID].get_EEG_by_channel_and_event(EEG_channel, EEG_event))

    # Visualize E4 data (physiological data)
    E4_partID, E4_file, E4_event = 'VG_01', 'HR', 'exper_video'
    plt.plot(E4_files[E4_partID].get_E4_by_filename_and_event(E4_file, E4_event))

    plt.show()

    # Generate train and test dataset for EEG_DL repository
    event_list_EEGDL = ["familiar_music", "wildlife_video", "family_inter", "Tchaikovsky"]
    gen_EEG_train_test_to_csv(event_list_EEGDL, multiply=10000, func='part', EEG_data=EEG_files)
