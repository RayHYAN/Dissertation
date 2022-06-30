# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 18:04:32 2022

@author: Zerui Mu
"""

import os
import pandas as pd

from basic_info import data_folder, E4_file_paths, E4_buffer
from Event_details import Event_time_details

E4_file_names = ['ACC', 'BVP', 'EDA', 'HR', 'IBI', 'TEMP'] # physiological data, tags.csv not included

class E4_data_class(object):
    def __init__(self, part_ID, data) -> None:
        self.ID = part_ID
        self.E4_data = data # each file including: start_time, Hz, data
        self.event_details = Event_time_details(part_ID)

    def _get_event_period_by_name(self, file_name, event_name):
        exp_start_time = float(self.E4_data[file_name]['time'])
        event_start = self.event_details.events_info[event_name]["start"]
        event_end = self.event_details.events_info[event_name]["end"]
        return event_start - exp_start_time + E4_buffer, event_end - exp_start_time - E4_buffer

    def get_E4_by_filename_and_event(self, file_name, event_name):
        start, end = self._get_event_period_by_name(file_name, event_name)
        Hz = self.E4_data[file_name]['Hz']
        return self.E4_data[file_name]['data'].iloc[int(start * Hz): int(end * Hz),:]


def read_all_E4_files():
    return {part_ID: read_E4_file(part_ID) for part_ID in E4_file_paths.keys()}

def read_E4_file(part_ID):
    try:
        if part_ID not in E4_file_paths.keys():
            raise IndexError("The given part_ID ({}) is not included".format(part_ID))
    except RuntimeError as e:
        print("Error:", e)
    data = {}
    for file_name in E4_file_names:
        E4_file_path = os.path.join(data_folder, E4_file_paths[part_ID], file_name + '.csv')
        E4_file = pd.read_csv(E4_file_path)
        data[file_name] = {
            'time': E4_file.columns[0],
            'Hz': E4_file.iloc[0,0], # The first row is the sample rate expressed in Hz.
            'data': E4_file[1:].reset_index(drop = True)
        }
    E4_part_data = E4_data_class(part_ID, data)
    print("Successfully loaded {} E4 file (physiological data)".format(part_ID))
    return E4_part_data


# E4_files = read_all_E4_files()
# # VG_01 events info
# E4_files['VG_01'].event_details.set_exp_datetime("08-09-2021")
# E4_files['VG_01'].event_details.set_event("exper_video", "16:02:00", "16:10:00")

# test
# print(E4_files['VG_01'].get_E4_by_filename_and_event('HR', 'exper_video'))
# print(E4_files['VG_01'].E4_data['HR']['data'])
# print(E4_files['VG_01'].event_details.exp_start_time)