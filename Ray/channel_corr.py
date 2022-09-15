import numpy as np
import pandas as pd
from typing import Dict
from Ray.EEG_data import EEG_channels, EEG_data_class

# Nomenclature:
# cal_corr_PE_(1 or all)_(1 or all or toge)
# PE: participant & event
# first (1 or all) indicates participants num
# second (1 or all or toge) indicates events num:
#   all means seperately, toge means all events combine together as one

def cal_corr_PE_1_1(EEGdata: Dict[str, EEG_data_class], partID, event):
    print(partID, event)
    EEG_part_data = EEGdata[partID]
    if not EEG_part_data.event_details.check_has_event(event) \
        or not EEG_part_data.event_details.check_event_has_start_and_end(event):
        return
    EEG_event_data = EEG_part_data.get_EEG_by_event(event)
    EEG_all_chs = {ch: data for ch, data in zip(EEG_channels.values(), EEG_event_data)}
    corr = [[np.corrcoef(ch1, ch2)[0][1] for ch2 in  EEG_all_chs.values()] for ch1 in EEG_all_chs.values()]
    index = [(np.argsort(row)[-2]+1, np.sort(row)[-2]) for row in corr]
    corr_df = pd.DataFrame(corr).set_axis([ch for ch in EEG_channels.values()], axis=0). \
        set_axis([ch for ch in EEG_channels.values()], axis=1)

    return corr_df

def cal_corr_PE_1_all(EEGdata: Dict[str, EEG_data_class], partID, event_list):
    corr = {event: cal_corr_PE_1_1(EEGdata, partID, event) for event in event_list}
    return corr

def cal_corr_PE_1_toge(EEGdata: Dict[str, EEG_data_class], partID, event_list):
    EEG_part_data = EEGdata[partID]
    chs_data = {ch: [] for ch in EEG_channels.values()}
    for event in event_list:
        if not EEG_part_data.event_details.check_has_event(event) \
            or not EEG_part_data.event_details.check_event_has_start_and_end(event):
            continue
        event_data = EEG_part_data.get_EEG_by_event(event)
        for i, data in enumerate(event_data):
            chs_data[EEG_channels[i+1]].extend(data)
    
    corr = [[np.corrcoef(ch1, ch2)[0][1] for ch2 in  chs_data.values()] for ch1 in chs_data.values()]
    index = [(np.argsort(row)[-2]+1, np.sort(row)[-2]) for row in corr]
    corr_df = pd.DataFrame(corr).set_axis([ch for ch in EEG_channels.values()], axis=0). \
        set_axis([ch for ch in EEG_channels.values()], axis=1)

    return corr_df

def cal_corr_PE_all_all(EEG_data: Dict[str, EEG_data_class], event_list):
    corr = {part: cal_corr_PE_1_all(EEG_data, part, event_list) for part in EEG_data.keys()}
    return corr

def call_corr_PE_all_toge(EEG_data: Dict[str, EEG_data_class], event_list):
    corr = {part: cal_corr_PE_1_toge(EEG_data, part, event_list) for part in EEG_data.keys()}
    return corr