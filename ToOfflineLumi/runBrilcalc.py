#!/usr/bin/env python
"""
# Run briclac for specified fills
# -*- coding: UTF-8 -*-
"""

import sys, os
import re
sys.path.append("../Utils/")
from xutils import *
from fillReport import *

fillReportName = '../Config/FillReport17.xls'
#fillReportName = '../Config/FillReportPPb_1479721242035.xls'
normtag = '/afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_BRIL.json'
outdir = '/scr1/RadMonLumi/2017/OfflineLumi/Brilcalc_normtag_BRIL/'
fillsPattern = 'brilcalcLumiFill'
#fillsPattern = 'brilcalcLumiFillNoNormtag'
#commandPattern = "brilcalc lumi --tssec -u hz/ub --normtag __NORMTAG__ --byls -f __FILL__ -o __OUTDIR__" + fillsPattern + "__FILL__.csv"
commandPattern = "brilcalc lumi --tssec -u hz/ub  --byls -f __FILL__ -o __OUTDIR__" + fillsPattern + "__FILL__.csv"

def main():
    
    #Fills to do
    fillReport = FillReport(fillReportName)
    fillStarted = fillReport.getFillCreationTime()
    
    #Fills already processed
    toReplace = outdir + fillsPattern
    filesDone = glob.glob(toReplace + "*")
    fillsDone = []
    for file in filesDone:
        name, ext = file.split('.')
        fillsDone.append(int(name.replace(toReplace, "")))

    nProccessed = 0
    nSkipped = 0 
    for fill in sorted(fillStarted.keys()):
        if int(fill) in fillsDone:
            print "Fill", fill, "is already processed. Skipping..."
            nSkipped += 1
            continue
        #command = commandPattern.replace('__FILL__', str(fill)).replace('__NORMTAG__', normtag).replace('__OUTDIR__', outdir)
        command = commandPattern.replace('__FILL__', str(fill)).replace('__OUTDIR__', outdir)
        nProccessed += 1
        print "Processing fill " + str(fill) + "..." + "Output goes to " + outdir 
        #print command
        os.system(command)   

    print nProccessed, "fills processed"        
    print nSkipped, "fills skipped"  
    
if __name__=="__main__":
    main()
