# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 23:14:19 2022

@author: Zerui Mu
"""

import json
from Ray.basic_fun import local2unix
from Ray.basic_info import EEG_buffer

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
    # 9: "break2",
    # 10: "setup_BIS",
    # 11: "baseline_BIS",
    # 12: "familiar_music_2",
    # 13: "family_inter_2",
    # 14: "takeoff_BIS_E4"
}

class Event_time_details(object):
    def __init__(self, part_ID) -> None:
        # Note: self.exp_start_time is for EEG file, since different E4 files have different start_timestamp
        self.ID = part_ID
        self.events_info = {} # with the actual event name and its start and end time (without buffer)
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
        self.events_info[event_name] = {"start": start_timestamp, "end": end_timestamp, 'valid': validation}

    def check_has_event(self, event_name) -> bool:
        return event_name in self.events_info.keys()

    def check_event_has_start_and_end(self, event_name) -> bool:
        return (self.events_info[event_name]['start'] != None and self.events_info[event_name]['end'] != None)

    def save_event_window_to_json(self, event_name, json_path, windows = 1):
        exp_start = self.exp_start_time
        start = int(self.events_info[event_name]['start'] - exp_start)
        end = int(self.events_info[event_name]['end'] - exp_start)
        spindles = [{'start': start*1.0, 'end': start + 1.0} \
            for start in range(start+EEG_buffer, end-EEG_buffer, windows)]
        with open(json_path, 'w') as f:
            json.dump(spindles ,f)