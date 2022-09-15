# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 18:51:32 2022

@author: Zerui Mu
"""

import random
import time

def local2unix(datetime):
    timeArray = time.strptime(datetime, "%d-%m-%Y %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return timestamp

def unix2local(timestamp):
    time_local = time.localtime(timestamp)
    datetime = time.strftime("%d-%m-%Y %H:%M:%S", time_local)
    return datetime

def gen_train_test_valid(data, test_ratio = 0.2, val_ratio = 0.2):
    if test_ratio + val_ratio > 0.5:
        print("Too much test & validation data!")
        return None, None, None
    part_num = len(data.keys())
    if test_ratio == 0.0:
        test_part_num = 0
    elif round(part_num * test_ratio) != 0:
        test_part_num = round(part_num * test_ratio)
    else: 
        test_part_num = 1
    if val_ratio == 0.0:
        val_part_num = 0
    elif round(part_num * val_ratio) != 0:
        val_part_num = round(part_num * val_ratio)
    else:
        val_part_num = 1
    # test_part_num = round(part_num * test_ratio) if round(part_num * test_ratio) != 0 else 1
    # val_part_num = round(part_num * val_ratio) if round(part_num * val_ratio) != 0 else 1

    test_part_list = random.sample(list(data.keys()), test_part_num)
    rest_part = [part for part in data.keys() if part not in test_part_list]
    val_part_list = random.sample(rest_part, val_part_num)
    train_part_list = [part for part in rest_part if part not in val_part_list]
    return train_part_list, test_part_list, val_part_list

def _test_local2unix():
    print(local2unix("08-09-2021 15:44:46"))

def _test_unix2local():
    print(unix2local(1631112286))

# _test_local2unix()
# _test_unix2local()