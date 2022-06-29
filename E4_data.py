# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 18:04:32 2022

@author: Zerui Mu
"""

import os
import pandas as pd

from basic_fun import local2unix

data_folder = r'./CARE_HOME_DATA'
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
E4_file_names = ['ACC', 'BVP', 'EDA', 'HR', 'IBI', 'TEMP'] # physiological data, tags.csv not included

E4_buffer = 30 # A uniform buffer to eliminate the noise at the start of each event, in second (S).


class E4_data_class(object):
    def __init__(self, part_ID, data) -> None:
        self.ID = part_ID
        self.E4_data = data # each file including: start_time, Hz, data
        self.event_details = E4_time_detail(part_ID)

    def _get_event_period_by_name(self, file_name, event_name):
        exp_start_time = float(self.E4_data[file_name]['time'])
        event_start = self.event_details.events_info[event_name]["start"]
        event_end = self.event_details.events_info[event_name]["end"]
        return event_start - exp_start_time + E4_buffer, event_end - exp_start_time - E4_buffer

    def get_E4_by_filename_and_event(self, file_name, event_name):
        start, end = self._get_event_period_by_name(file_name, event_name)
        Hz = self.E4_data[file_name]['Hz']
        return self.E4_data[file_name]['data'].iloc[int(start * Hz): int(end * Hz),:]


class E4_time_detail(object):
    def __init__(self, part_ID) -> None:
        self.ID = part_ID
        self.events_info = {}
        
    def set_exp_date(self, date):
        self.exp_date = date

    def set_event(self, event_name, start, end):
        start_timestamp = local2unix(self.exp_date + " " + start)
        end_timestamp = local2unix(self.exp_date + " " + end)
        self.events_info[event_name] = {"start": start_timestamp, "end": end_timestamp}


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

E4_files = read_all_E4_files()
# VG_01 events info
E4_files['VG_01'].event_details.set_exp_date("08-09-2021")
E4_files['VG_01'].event_details.set_event("exper_video", "16:02:00", "16:10:00")

# test
# print(E4_files['VG_01'].get_E4_by_filename_and_event('HR', 'exper_video'))
# print(E4_files['VG_01'].E4_data['HR']['data'])