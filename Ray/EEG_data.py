# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 21:58:32 2022

@author: Zerui Mu
"""

import os
from typing import Dict
import mne

from Ray.basic_info import data_folder, VG_file_paths, VG_Hz, EEG_buffer
from Ray.Event_details import Event_time_details

EEG_channels = {1:"Fpz-O1", 2:"Fpz-O2", 3:"Fpz-F7", 4:"F8-F7", 5:"F7-01", 6:"F8-O2", 7:"Fpz-F8"}

class EEG_data_class(object):
    def __init__(self, part_ID, data) -> None:
        self.ID = part_ID
        self.EEG_data = {EEG_channels[col]: data[col] for col in range(1,8)}
        self.event_details = None # need to be set after init

    def set_event_details(self, event_details: Event_time_details):
        self.event_details = event_details # including date, start_time, events_info

    def _get_event_period_by_name(self, event):
        # return the period of time with 2 buffers (initially 30 sec)
        exp_start_time = self.event_details.exp_start_time
        event_start = self.event_details.events_info[event]["start"]
        event_end = self.event_details.events_info[event]["end"]
        return event_start - exp_start_time + EEG_buffer, event_end - exp_start_time - EEG_buffer

    def get_EEG_by_channel_and_event(self, channel, event_name):
        # channel can be the name or its index
        # print(channel, event_name)
        start, end = self._get_event_period_by_name(event_name)
        if channel in EEG_channels.keys():
            return self.EEG_data[EEG_channels[channel]][int(start * VG_Hz): int(end * VG_Hz)]
        elif channel in EEG_channels.values():
            return self.EEG_data[channel][int(start * VG_Hz): int(end * VG_Hz)]
        else:
            print("The input channel ({}) is wrong!, Please check.".format(channel))

    def get_EEG_by_event(self, event_name, channel_list = [k for k in EEG_channels.keys()]):
        # get all 7 EEG channels data
        event_data = []
        for channel in channel_list:
            channel_data = self.get_EEG_by_channel_and_event(channel, event_name)
            event_data.append(channel_data)
        return event_data

    def get_event_duration(self, event_name):
        if event_name not in self.event_details.events_info.keys():
            return None
        start = self.event_details.events_info[event_name]['start']
        end = self.event_details.events_info[event_name]['end']
        if start == None or end == None:
            return None
        return end - start

def read_all_VG_files() -> Dict[str, EEG_data_class]:
    return {part_ID: read_VG_file(part_ID) for part_ID in VG_file_paths.keys()}

def read_VG_file(part_ID, exclude_channels = []) -> EEG_data_class:
    try:
        if part_ID not in VG_file_paths.keys():
            raise IndexError("The given part_ID ({}) is not included".format(part_ID))
    except RuntimeError as e:
        print("Error:", e)
    VG_file_path = os.path.join(data_folder, VG_file_paths[part_ID])
    VG_file = mne.io.read_raw_edf(VG_file_path, exclude = exclude_channels)
    data = EEG_data_class(part_ID, VG_file.get_data())
    # print(VG_file.ch_names)
    print("Successfully loaded {} VG file (EEG data).".format(part_ID))
    return data

def read_all_VG_to_Raw():
    return {part_ID: read_VG_to_Raw(part_ID) for part_ID in VG_file_paths.keys()}

def read_VG_to_Raw(part_ID):
    exclude_channels = ['Accelero Norm', 'Positiongram', 'PulseOxy Infrare', 'PulseOxy Red Hea', 'Respiration x', 'Respiration y', 'Respiration z']
    VG_file_path = os.path.join(data_folder, VG_file_paths[part_ID])
    raw = mne.io.read_raw_edf(VG_file_path, exclude=exclude_channels, preload = True)
    return raw
