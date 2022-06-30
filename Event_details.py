# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 23:14:19 2022

@author: Zerui Mu
"""

from basic_fun import local2unix

all_EEG_events = {
    0: "setup",
    1: "baseline",
    2: "exper_video",
    3: "wildlife_video",
    4: "familiar_music",
    5: "Tchaikovsky",
    6: "break",
    7: "family_inter",
    8: "takeoff_EEG",
    9: "setup_BIS",
    10: "baseline_BIS",
    11: "familiar_music_2",
    12: "family_inter_2",
    13: "takeoff_BIS_E4"
}

class Event_time_details(object):
    def __init__(self, part_ID) -> None:
        self.ID = part_ID
        self.events_info = {}
        self.exp_date = None
        self.exp_start_time = None
        
    def set_exp_datetime(self, date, time_hms = None):
        self.exp_date = date
        if time_hms != None: # start_time for each E4 file is different
            self.exp_start_time = local2unix(date + " " + time_hms) # start_time for each EEG file is the same

    def set_event(self, event_name, start, end):
        start_timestamp = local2unix(self.exp_date + " " + start)
        end_timestamp = local2unix(self.exp_date + " " + end)
        self.events_info[event_name] = {"start": start_timestamp, "end": end_timestamp}