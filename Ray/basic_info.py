# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 23:59:34 2022

@author: Zerui Mu
"""

data_folder = r'../data/CARE_HOME_DATA/'
motor_movement_data_folder = r'../data/EEG-Motor-Movement-Imagery-Dataset/'
E4_file_paths = {
    'VG_01': r'./VG01/E4_8921_15_44/',
    # 'VG_02': None,
    'VG_03': r'./VG03/E4_9921_12_16/',
    'VG_05': r'./VG05/E4_9921_13_24/',
    'VG_06': r'./VG06/E4_51021_13_33/',
    'VG_07': r'./VG07/E4_51021_15_39/',
    'VG_08': r'./VG08/E4_71021_10_42/',
    'VG_09': r'./VG09/E4_11221_14_46/',
    'VG_10': r'./VG10/E4_31221_11_17/',
    'VH_01': r'./VH01/E4_61021_11_03/',
    'VH_02': r'./VH02/E4_61021_13_59/',
    'VH_03': r'./VH03/E4_11221_11_22/'
}

VG_file_paths = {
    'VG_01': r'./VG01/8921_15_52.edf',
    'VG_02': r'./VG02/7921_15_18.edf',
    'VG_03': r'./VG03/90921_12_20.edf',
    'VG_05': r'./VG05/90921_13_27.edf',
    'VG_06': r'./VG06/51021_13_40.edf',
    # 'VG_07': r'./VG07/51021_15_43.edf',
    'VG_08': r'./VG08/71021_10_44.edf',
    'VG_09': r'./VG09/11221_14_59.edf',
    'VG_10': r'./VG10/31221_11_24.edf',
    'VH_01': r'./VH01/61021_11_17.edf',
    'VH_02': r'./VH02/61021_14_3.edf',
    'VH_03': r'./VH03/11221_11_21.edf'
}

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

VG_Hz = 250 # EEG sample rate in Hz
EEG_buffer = 30 # A uniform buffer to eliminate the noise at the start of each event, in second (S).
E4_buffer = 30 # A uniform buffer to eliminate the noise at the start of each event, in second (S).