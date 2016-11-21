#!/usr/bin/env python
"""
# Merge csv lumi info and rate info from hd5 files into one root file
# (One file per fill)
# -*- coding: UTF-8 -*-
"""

import sys, os
import re
import tables
sys.path.append("../Utils/")
from xutils import *
from fillReport import *
from ROOT import *
import numpy as np
import math


#fillReportName = '../Config/FillReport.xls'
fillReportName = '../Config/FillReportPPb_1479721242035.xls'
#csvPattern = '/scr1/RadMonLumi/2016/OfflineLumi/Brilcalc_normtag_BRIL/brilcalcLumiFill__FILL__.csv'
csvPattern = '/scr1/RadMonLumi/2016/OfflineLumi/Brilcalc_normtag_BRIL/brilcalcLumiFillNoNormtag__FILL__.csv'
hd5Pattern = '/scr1/RadmonHd5/Fills2016/radmon__FILL__.hd5'
rootFilePattern = '/scr1/RadMonLumi/2016/OfflineLumi/Radmon_normtag_BRIL/radmonLumi_NoNormtag__FILL__.root'


gROOT.ProcessLine(\
"struct RadmonLumiData{\
    Int_t fill;\
    Int_t fillStart;\
    Int_t fillStable;\
    Int_t fillEnd;\
    Int_t durationStable;\
    Int_t run;\
    Int_t lsNo;\
    Int_t tstamp;\
    Double_t bField;\
    Double_t beamEnergy;\
    Double_t lumi;\
    Double_t rates[16];\
    Double_t drates[16];\
    Double_t nibbles[16];\
    Char_t beamStatus[15];\
    Char_t lumiSource[15];\
};")
#from ROOT import RadmonLumiData


def getFilesDone(pattern):
    #Might be worth to move this to utils
    #Pattern should be   /FullPath/FileName*.ext
    name, ext = pattern.split('.')
    toReplace = name[:-1]
    
    filesDone = glob.glob(pattern)
    fillsDone = []
    for file in filesDone:
        name, ext = file.split('.')
        fillsDone.append(int(name.replace(toReplace, "")))
        
    return fillsDone

def mergeHd5Lumi():
    #Fills to do
    fillReport = FillReport(fillReportName)
    fillStarted = fillReport.getFillCreationTime()
    #Fills already processed
    fillsDone = getFilesDone(rootFilePattern.replace('__FILL__', '*'))

    nProccessed = 0
    nSkipped = 0 
    for fill in sorted(fillStarted.keys()):
        if int(fill) in fillsDone:
            print "Fill", fill, "is already processed. Skipping..."
            nSkipped += 1
            continue    
        
        #Filldata from fillreport
        fillNo = int(fill)
        fillStable = fillReport.getFillStableTime(fill)
        fillStart = fillStarted[fill]
        fillEnd = fillReport.getFillEndTime(fill)
        durationStable = fillReport.getFillDuration(fill)
        bField = fillReport.getFillField(fill)
        beamEnergy = fillReport.getFillBeamEnergy(fill)
        
        csvData = {}
        #Read csv lumi data into dictionary
        try:
	    file = open(csvPattern.replace('__FILL__', str(fill)), 'r')
	except IOError:
	    print "Cannot open file for fill", fill
	    continue
        
        print "Processing fill ", str(fill) + "..."
        nProccessed += 1
        
        for line in file.readlines():
            #Skip commments
            line = line.split('#')[0].strip() 
            if not line:
                continue
        
            data = line.split(',')
            run, fill = data[0].strip().split(':')
            lsNo, dummy = data[1].strip().split(':')
            key = str(run) + '_' + str(lsNo)
            csvData[key] = line
        del file
        
        
        #Process corresponding hd5 file
        try:
            f = tables.open_file(hd5Pattern.replace('__FILL__', str(fill)))
        except Exception as e:
            print e.__doc__
            print e.message
            continue        
    
        
        hd5rates = {}
        for leaf in f.walk_nodes(where='/',classname="Leaf"):
            if leaf.name == 'radmonraw':
                data =  f.get_node(where='/',name="radmonraw", classname="Leaf")            

                for item in data:

                    key = str(item['runnum']) + '_' + str(item['lsnum'])
                    if not key in hd5rates.keys():
                        hd5rates[key] = []
                        for i in range(16):
                            hd5rates[key].append([])                    
            
                    if len(item['rate']) == 1:   # old format
                        id = int(item['channelid']) 
                        dataOK = status2bitset(int(item['status']))[0] 
                        if dataOK:
                            hd5rates[key][id].append(float(item['rate']))
                    else:
                        for i in range(16):  
                            dataOK =  status2bitset(int(item['status'][i]))[0]
                            if dataOK:
                                hd5rates[key][i].append(float(item['rate'][i]))
                        
        try: 
            f.close()
        except: 
            print "error closing hd5 file"
            pass
        # hd5 file ends
        
        #Output
        rootFile = rootFilePattern.replace('__FILL__', str(fill))
	try:
	    fout = TFile(rootFile,'RECREATE')
	except IOError:
	    print "Cannot open file for output", rootFile
	    continue	 

	t = TTree('t', 'Combined  Lumi from Brilcalc and Radmon data')
	
	rlData = RadmonLumiData()        
        t.Branch('radmonLumiI', rlData, 'fill/I:fillStart/I:fillStable/I:fillEnd/I:durationStable/I:run/I:lsNo/I:tstamp/I')
        t.Branch('radmonLumiD', AddressOf(rlData, 'bField'), 'bField/D:beamEnergy/D:lumi/D:rates[16]/D:drates[16]/D:nibbles[16]/D')
        t.Branch('BeamStatus', AddressOf(rlData, 'beamStatus'), 'beamStatus/C')
        t.Branch('LumiSource', AddressOf(rlData, 'lumiSource'), 'lumiSource/C')        
        
        for key in sorted(csvData.keys()):
            data = csvData[key].split(',')
            run, fill = data[0].strip().split(':')
            lsNo, dummy = data[1].strip().split(':')
            
            rlData.fill = fillNo
            rlData.fillStart = fillStart
            rlData.fillStable = fillStable
            rlData.fillEnd = fillEnd
            rlData.durationStable = durationStable
            rlData.run = int(run)
            rlData.lsNo = int(lsNo)
            rlData.tstamp = int(data[2].strip())
            rlData.bField = bField
            rlData.beamEnergy = beamEnergy
            rlData.lumi = float(data[5].strip())
            rlData.beamStatus = data[3].strip()
            rlData.lumiSource = data[8].strip()

            if key not in hd5rates.keys():
                print "Key ", key, "not found in Hd5 file  for fill ", fillNo
                for i in  range(0,16):
                    rlData.rates[i] = -2.
                    rlData.drates[i] = -2.
                    rlData.nibbles[i] = -2.
            else:
                for i in  range(0,16):
                    a = np.asarray(hd5rates[key][i])
                    mean = np.mean(a)
                    std = np.std(a)
                    nibbles = len(a)
                    if np.isnan(mean):
                        mean = -1.
                        std = -1.
                        nibbles = 1
                    rlData.rates[i] = mean
                    rlData.drates[i] = std/sqrt(nibbles)
                    rlData.nibbles[i] = nibbles

            t.Fill()
            
	print "Writing", rootFile
	fout.Write()
	fout.Close()
	del fout        
    	
        del csvData
        del hd5rates
        
    print nProccessed, "fills processed"        
    print nSkipped, "fills skipped"  
    

#===========================================================
if __name__ == "__main__": 
    mergeHd5Lumi()
