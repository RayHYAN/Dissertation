# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 21:58:32 2022

@author: Zerui Mu
"""

import os
import mne

from basic_fun import local2unix

data_folder = r'./CARE_HOME_DATA'
VG_file_paths = {
    'VG_01': r'./VG01/8921_15_52.edf',
    'VG_02': r'./VG02/7921_15_18.edf',
    'VG_03': r'./VG03/90921_12_20.edf',
    'VG_05': r'./VG05/90921_13_27.edf',
    'VG_06': r'./VG06/51021_13_40.edf',
    'VG_07': r'./VG07/51021_15_43.edf',
    'VG_08': r'./VG08/71021_10_44.edf',
    'VG_09': r'./VG09/11221_14_59.edf',
    'VG_10': r'./VG10/31221_11_24.edf',
    'VH_01': r'./VH01/61021_11_17.edf',
    'VH_02': r'./VH02/61021_14_3.edf',
    'VH_03': r'./VH03/11221_11_21.edf'
}
EEG_channels = {1:"Fpz-O1", 2:"Fpz-O2", 3:"Fpz-F7", 4:"F8-F7", 5:"F7-01", 6:"F8-O2", 7:"Fpz-F8"}
all_EEG_events = {
    0: "setup",
    1: "baseline",
    2: "exper_video",
    3: "wildlife_video",
    4: "familiar_music",
    5: "Tchaikovsky",
    6: "break",
    7: "family_inter",
    8: "takeoff"
}

VG_Hz = 250 # EEG sample rate in Hz
EEG_buffer = 30 # A uniform buffer to eliminate the noise at the start of each event, in second (S).


class EEG_data_class(object):
    def __init__(self, part_ID, data) -> None:
        self.ID = part_ID
        self.EEG_data = {EEG_channels[col]: data[col] for col in range(1,8)}
        self.event_details = EEG_time_detail(part_ID) # including date, start_time, envents_info

    def _get_event_period_by_name(self, event):
        exp_start_time = self.event_details.exp_start_time
        event_start = self.event_details.events_info[event]["start"]
        event_end = self.event_details.events_info[event]["end"]
        return event_start - exp_start_time + EEG_buffer, event_end - exp_start_time - EEG_buffer

    def get_EEG_by_channel_and_event(self, channel, event_name):
        # channel can be the name or its index
        start, end = self._get_event_period_by_name(event_name)
        if channel in EEG_channels.keys():
            return self.EEG_data[EEG_channels[channel]][int(start * VG_Hz): int(end * VG_Hz)]
        elif channel in EEG_channels.values():
            return self.EEG_data[channel][int(start * VG_Hz): int(end * VG_Hz)]
        else:
            print("The input channel ({}) is wrong!, Please check.".format(channel))


class EEG_time_detail(object):
    def __init__(self, part_id) -> None:
        self.ID = part_id
        self.events_info = {}

    def set_exp_datetime(self, date, time_hms):
        self.exp_date = date
        self.exp_start_time = local2unix(date + " " + time_hms) # start_time for each EEG file is the same

    def set_event(self, event_name, start, end):
        start_timestamp = local2unix(self.exp_date + " " + start)
        end_timestamp = local2unix(self.exp_date + " " + end)
        self.events_info[event_name] = {"start": start_timestamp, "end": end_timestamp}


def read_all_VG_files():
    return {part_ID: read_VG_file(part_ID) for part_ID in VG_file_paths.keys()}

def read_VG_file(part_ID):
    try:
        if part_ID not in VG_file_paths.keys():
            raise IndexError("The given part_ID ({}) is not included".format(part_ID))
    except RuntimeError as e:
        print("Error:", e)
    VG_file_path = os.path.join(data_folder, VG_file_paths[part_ID])
    VG_file = mne.io.read_raw_edf(VG_file_path)
    data = EEG_data_class(part_ID, VG_file.get_data())
    # print(VG_file.ch_names)
    print("Successfully loaded {} VG file (EEG data).".format(part_ID))
    return data

EEG_files = read_all_VG_files()
# VG_06 events info
EEG_files['VG_06'].event_details.set_exp_datetime("05-10-2021", "13:40:50")
EEG_files['VG_06'].event_details.set_event("familiar_music", "13:58:00", "14:04:00")


# test
# print(EEG_files['VG_06'].get_EEG_by_channel_and_event(EEG_channels[1], 'familiar_music'))
# print(EEG_files['VG_06'].get_EEG_by_channel_and_event(1, 'familiar_music'))
