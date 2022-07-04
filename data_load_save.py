# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 17:11:22 2022

@author: Zerui Mu
"""

import os
import pandas as pd

from basic_info import data_folder
from basic_fun import unix2local
import data_setup

event_details_path = os.path.join(data_folder, './event_details.csv')
exp_info_path = os.path.join(data_folder, './exp_info.csv')

def save_data_to_csv():
    EEG_files, _ = data_setup.set_up()
    event_details_dic = {
        'partID': [],
        'event': [],
        'start': [],
        'end': [],
        'valid': []
    }

    exp_info_dic = {
        'partID': [],
        'date': [],
        'exp_start': []
    }

    for part in EEG_files.keys():
        EEG_part = EEG_files[part]
        for Ev_name, EV_info in EEG_part.event_details.events_info.items():
            start_time = unix2local(EV_info['start']).split(' ')[1] if EV_info['start'] != None else None # only need time from datetime
            end_time = unix2local(EV_info['end']).split(' ')[1] if EV_info['end'] != None else None # only need time from datetime
            event_details_dic['partID'].append(part)
            event_details_dic['event'].append(Ev_name)
            event_details_dic['start'].append(start_time) 
            event_details_dic['end'].append(end_time)
            event_details_dic['valid'].append(EV_info['valid'])
        
        exp_info_dic['partID'].append(part)
        exp_info_dic['date'].append(EEG_part.event_details.exp_date)
        exp_info_dic['exp_start'].append(unix2local(EEG_part.event_details.exp_start_time).split(' ')[1])

    event_details_df = pd.DataFrame(event_details_dic)
    exp_info_df = pd.DataFrame(exp_info_dic)

    with open(event_details_path, 'w', newline='') as f:
        event_details_df.to_csv(f)
    with open(exp_info_path, 'w', newline='') as f:
        exp_info_df.to_csv(f)

def load_data_from_csv():
    event_details_df = pd.read_csv(event_details_path, index_col=0)
    exp_info_df = pd.read_csv(exp_info_path, index_col=0)

    # print(event_details_df.head())
    # print(exp_info_df)
    print

# save_data_to_csv()
load_data_from_csv()
