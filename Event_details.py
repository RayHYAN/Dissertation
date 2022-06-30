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
        # Note: self.exp_start_time is for EEG file, since different E4 files have different start_timestamp
        self.ID = part_ID
        self.events_info = {}
        self.exp_date = None # need to be set after init
        self.exp_start_time = None # need to be set after init
        
    def set_exp_datetime(self, date, time_hms):
        self.exp_date = date
        self.exp_start_time = local2unix(date + " " + time_hms)

    def set_event(self, event_name, start, end, validation = True):
        # validation: if False, means the time is estimated, without verification
        if event_name not in all_EEG_events.values():
            print("The event ({}) is not in the event list. Please check!".format(event_name))
            return
        start_timestamp = local2unix(self.exp_date + " " + start) if start != None else None
        end_timestamp = local2unix(self.exp_date + " " + end) if end != None else None
        self.events_info[event_name] = {"start": start_timestamp, "end": end_timestamp}