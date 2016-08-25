#!/usr/bin/env python
"""
# Run brillogreader for specified range of /var/log/rcms/lumipro/Logs_lumipro.xml.*.gz files
# -*- coding: UTF-8 -*-
"""

import sys, os
import re
#sys.path.append("../Utils/")
#from xutils import *
#from fillReport import *

#fillReportName = '../Config/FillReport.xls'
#normtag = '/afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json'
outfile  = 'radmonprocessor160823.log'
logPattern = '/var/log/rcms/lumipro/Logs_lumipro.xml.__XXX__.gz'
commandPattern = "python ~brilpro/brillogreader.py  --app=radmon __FILELIST__" 

maxNumber = 185

def main():
    
    files = []
    for i in range(maxNumber, 0, -1):
        files.append(logPattern.replace('__XXX__', str(i)))
    
    filelist = ','.join(files)
    command = commandPattern.replace("__FILELIST__", filelist) + " > "  + outfile

    os.system(command)   
    
if __name__=="__main__":
    main()
