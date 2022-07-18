# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 18:51:32 2022

@author: Zerui Mu
"""

import time

def local2unix(datetime):
    timeArray = time.strptime(datetime, "%d-%m-%Y %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return timestamp

def unix2local(timestamp):
    time_local = time.localtime(timestamp)
    datetime = time.strftime("%d-%m-%Y %H:%M:%S", time_local)
    return datetime

def _test_local2unix():
    print(local2unix("08-09-2021 15:44:46"))

def _test_unix2local():
    print(unix2local(1631112286))

# _test_local2unix()
# _test_unix2local()