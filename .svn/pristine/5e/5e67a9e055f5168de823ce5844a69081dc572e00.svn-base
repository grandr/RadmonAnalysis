#!/usr/bin/env python
"""
Test . Various utilities
 -*- coding: UTF-8 -*-
"""

import time
from datetime import datetime
import os, sys
import glob

from dateutil import tz

def get_filelist(datadir, pattern, fromto):
    """
    Get list of files matching pattern (traversing subdirectories) in the given time interval
    """
    files = []
    good_files = []
    for (path, dirs, files) in os.walk(datadir):
        files = glob.glob(os.path.join(path,pattern))
        for file in sorted(files):
            (name, ext) = file.split('.')
            (dummy, da, tm) = name.split('_')
            ts =int(timepar2ts(da+tm))
            if ts  >= fromto[0] and  ts <= fromto[1]:
                good_files.append(file)

    return good_files
#=============================

def utc2local(ts_utc):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(os.environ['TZ'])

    utc = datetime.fromtimestamp(int(ts_utc))

    utc = utc.replace(tzinfo=from_zone)
    # Convert time zone
    local = utc.astimezone(to_zone)

    return int(time.mktime(local.timetuple())) # Get timestamp

#=============================

def local2utc(ts_local):
    utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts_local))
    return int(time.mktime(time.strptime( utc, "%Y-%m-%d %H:%M:%S")))

#=============================

def timepar2ts(t):
    """
    Convert time parameter YYMMDD[HHMMSS] to timestamp
    """
    dummy = t
    if len(t) < 6:
        print "Wrong time parameter: " + str(t)
        exit()
    else:
        for i in range(len(t), 12):
            dummy = dummy + str(0)
    datime = dummy[:2] + '-' + dummy[2:4] + '-' + dummy[4:6] + ' ' + dummy[6:8] + ':' + dummy[8:10] + ':' + dummy[10:]
    del dummy
    return datime2ts(datime)

#===================================================================
def datime2ts(dt, offset = 0):
    """
    Convert date/time to timestamp with offset in hours
    """
    date, tme = dt.split()
    year, month, day = date.split('-')
    hms =  tme.split(':')

    if len(hms) == 3:
        sec = hms[2]
    else:
        sec = '0'
    if len(hms) > 1:
        min = hms[1]
    else:
        min = '0'
    if len(hms) > 0:
        hr = hms[0]
    else:
        hr = '0'

    t = datetime(int(year), int(month), int(day), int(hr), int(min), int(sec))
    tstamp = time.mktime(t.timetuple())  + offset * 3600
    return tstamp


#===================================================================
def datime2ts(dt, offset = 0):
    """
    Convert date/time to timestamp with offset in hours
    """
    date, tme = dt.split()
    year, month, day = date.split('-')
    hms =  tme.split(':')

    if len(hms) == 3:
        sec = hms[2]
    else:
        sec = '0'
    if len(hms) > 1:
        min = hms[1]
    else:
        min = '0'
    if len(hms) > 0:
        hr = hms[0]
    else:
        hr = '0'

    t = datetime(int(year), int(month), int(day), int(hr), int(min), int(sec))
    tstamp = time.mktime(t.timetuple())  + offset * 3600
    return tstamp
#===================================================================
def int2bin(n, count=16):
    """
    returns the binary of integer n, using count number of digits
    """
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])


