# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 17:11:22 2022

@author: Zerui Mu
"""

import os
import pandas as pd
import random

from Ray.basic_info import data_folder, motor_movement_data_folder, EEG_buffer, VG_Hz
from Ray.basic_fun import unix2local
from Ray.Event_details import Event_time_details
from Ray import EEG_data, E4_data

event_details_path = os.path.join(data_folder, './event_details.csv')
exp_info_path = os.path.join(data_folder, './exp_info.csv')

def save_info_to_csv():
    EEG_files = EEG_data.read_all_VG_files()
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
            start_time = unix2local(EV_info['start']).split(' ')[1] if EV_info['start'] != None else 'None' # only need time from datetime
            end_time = unix2local(EV_info['end']).split(' ')[1] if EV_info['end'] != None else 'None' # only need time from datetime
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
        event_details_df.to_csv(f, index = False)
    with open(exp_info_path, 'w', newline='') as f:
        exp_info_df.to_csv(f, index = False)

def load_info_from_csv():
    event_details_df = pd.read_csv(event_details_path, index_col=0)
    exp_info_df = pd.read_csv(exp_info_path, index_col=0)

    part_list = list(exp_info_df.index)
    ev_details = {}

    for partID in part_list:
        ev_detail = Event_time_details(partID)
        ev_detail.set_exp_datetime(exp_info_df.loc[partID]['date'], exp_info_df.loc[partID]['exp_start'])    
        for event in event_details_df.loc[partID,].iterrows():
            start = str(event[1]['start']) if event[1]['start'] != 'None' else None
            end = str(event[1]['end']) if event[1]['end'] != 'None' else None
            ev_detail.set_event(event[1]['event'], start, end, event[1]['valid'])
        ev_details[partID] = ev_detail
    return ev_details

def set_up(isEEG = True, isE4 = True):
    # isEEG: load EEG data or not
    # isE4: load E4 data or not
    EEG_files = EEG_data.read_all_VG_files() if isEEG == True else None
    E4_files = E4_data.read_all_E4_files() if isE4 == True else None
    ev_details = load_info_from_csv()

    if isEEG == True:
        for partID, EEG in EEG_files.items():
            EEG.set_event_details(ev_details[partID])
    if isE4 == True:
        for partID, E4 in E4_files.items():
            E4.set_event_details(ev_details[partID])

    return EEG_files, E4_files

def gen_EEG_traintest_to_csv_mix(event_list, multiply, windows = 1, train_ratio = 0.9, EEG_files = None):
    # mix all partcipants data together and separate train_set and test_set by train_ratio
    if EEG_files == None:
        EEG_files, _ = set_up(isE4 = False)
    row_size, fs = 4096, VG_Hz
    channel_batch_size = {
        'Fpz-O1': row_size // 7,
        'Fpz-O2': row_size // 7,
        'Fpz-F7': row_size // 7,
        'F8-F7': row_size // 7,
        'F7-01': row_size // 7,
        'F8-O2': row_size // 7,
        'Fpz-F8': row_size - (row_size // 7) * 6,
    }
    data_label_list = []
    label_dic = {label: i for i, label in enumerate(event_list)}

    for part in EEG_files.keys():
        for event_name in event_list:
            if EEG_files[part].event_details.check_has_event(event_name) and EEG_files[part].event_details.check_event_has_start_and_end(event_name):
                data_length = (EEG_files[part].event_details.events_info[event_name]['end'] - \
                    EEG_files[part].event_details.events_info[event_name]['start'] - 2 * EEG_buffer) * fs
                for start in range(0, int(data_length - row_size // 7) - 1, fs):
                    row_data = []
                    for channel, size in channel_batch_size.items():
                        part_data = EEG_files[part].get_EEG_by_channel_and_event(channel=channel, event_name=event_name)
                        row_data.extend(part_data[start: start + size])
                    data_label_list.append((row_data, label_dic[event_name]))
                    
    random.shuffle(data_label_list)
    train_data_df = pd.DataFrame([dat[0] for dat in data_label_list[:round(len(data_label_list)*train_ratio)]]).multiply(multiply)
    test_data_df = pd.DataFrame([dat[0] for dat in data_label_list[round(len(data_label_list)*train_ratio):]]).multiply(multiply)
    train_label_df = pd.DataFrame([dat[1] for dat in data_label_list[:round(len(data_label_list)*train_ratio)]])
    test_label_df = pd.DataFrame([dat[1] for dat in data_label_list[round(len(data_label_list)*train_ratio):]])
    print(train_data_df.shape)
    print(test_data_df.shape)
    print(train_label_df.shape)
    print(test_label_df.shape)
    return train_data_df, test_data_df, train_label_df, test_label_df

def gen_EEG_traintest_to_csv_part(event_list, multiply, windows = 1, train_ratio = 0.9, EEG_files = None):
    # separate train_set and test_set by participant and the train_ratio
    if EEG_files == None:
        EEG_files, _ = set_up(isE4 = False)
    row_size, fs = 4096, VG_Hz
    train_num_per_class_limit, test_num_per_class_limit = 2000, 200
    channel_batch_size = {
        'Fpz-O1': row_size // 7,
        'Fpz-O2': row_size // 7,
        'Fpz-F7': row_size // 7,
        'F8-F7': row_size // 7,
        'F7-01': row_size // 7,
        'F8-O2': row_size // 7,
        'Fpz-F8': row_size - (row_size // 7) * 6,
    }
    label_dic = {label: i for i, label in enumerate(event_list)}
    # train and test participants list
    test_part_num = round(len(EEG_files.keys()) * (1-train_ratio))
    test_part_num = test_part_num if test_part_num != 0 else 1
    test_part_list = random.sample(list(EEG_files.keys()), test_part_num)
    train_part_list = [part for part in EEG_files.keys() if part not in test_part_list]

    # train data and labels
    train_data_label_dic = {}
    for part in train_part_list:
        for event_name in event_list:
            if label_dic[event_name] not in train_data_label_dic.keys():
                train_data_label_dic[label_dic[event_name]] = []
            if EEG_files[part].event_details.check_has_event(event_name) and EEG_files[part].event_details.check_event_has_start_and_end(event_name):
                data_length = (EEG_files[part].event_details.events_info[event_name]['end'] - \
                    EEG_files[part].event_details.events_info[event_name]['start'] - 2 * EEG_buffer) * fs
                for start in range(0, int(data_length - row_size // 7) - 1, fs):
                    if len(train_data_label_dic[label_dic[event_name]]) >= train_num_per_class_limit:
                        break
                    row_data = []
                    for channel, size in channel_batch_size.items():
                        part_data = EEG_files[part].get_EEG_by_channel_and_event(channel=channel, event_name=event_name)
                        row_data.extend(part_data[start: start + size])
                    train_data_label_dic[label_dic[event_name]].append((row_data, label_dic[event_name]))

    train_data_label = []
    for l in train_data_label_dic.values():
        train_data_label.extend(l)
                    
    # test data and labels
    test_data_label_dic = {}
    for part in test_part_list:
        for event_name in event_list:
            if label_dic[event_name] not in test_data_label_dic.keys():
                test_data_label_dic[label_dic[event_name]] = []
            if EEG_files[part].event_details.check_has_event(event_name) and EEG_files[part].event_details.check_event_has_start_and_end(event_name):
                data_length = (EEG_files[part].event_details.events_info[event_name]['end'] - \
                    EEG_files[part].event_details.events_info[event_name]['start'] - 2 * EEG_buffer) * fs
                for start in range(0, int(data_length - row_size // 7) - 1, fs):
                    if len(test_data_label_dic[label_dic[event_name]]) >= test_num_per_class_limit:
                        break
                    row_data = []
                    for channel, size in channel_batch_size.items():
                        part_data = EEG_files[part].get_EEG_by_channel_and_event(channel=channel, event_name=event_name)
                        row_data.extend(part_data[start: start + size])
                    test_data_label_dic[label_dic[event_name]].append((row_data, label_dic[event_name]))

    test_data_label = []
    for l in test_data_label_dic.values():
        test_data_label.extend(l)

    random.shuffle(train_data_label)
    random.shuffle(test_data_label)
    train_data_df = pd.DataFrame([dat[0] for dat in train_data_label]).multiply(multiply)
    test_data_df = pd.DataFrame([dat[0] for dat in test_data_label]).multiply(multiply)
    train_label_df = pd.DataFrame([dat[1] for dat in train_data_label])
    test_label_df = pd.DataFrame([dat[1] for dat in test_data_label])
    print(train_data_df.shape)
    print(test_data_df.shape)
    print(train_label_df.shape)
    print(test_label_df.shape)
    return train_data_df, test_data_df, train_label_df, test_label_df
