#!/usr/bin/env python
"""
# Merge csv lumi files with offline and online normtag  into one root file
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


fillReportName = '../Config/FillReport.xls'
csvOfflinePattern = '/scr1/RadMonLumi/2016/OfflineLumi/LumiFillsCsv/brilcalcLumiFill__FILL__.csv'
csvOnlinePattern = '/scr1/RadMonLumi/2016/OfflineLumi/LumiFillsCsv/brilcalcLumiFill__FILL__.csv'

rootFilePattern = '/scr1/RadMonLumi/2016/LumiCombined/lumiCombined__FILL__.root'

collCutoff =  20
idColl = 12

gROOT.ProcessLine(\
"struct CombinedLumiData{\
    Int_t fill;\
    Int_t fillStart;\
    Int_t fillStable;\
    Int_t fillEnd;\
    Int_t durationStable;\
    Int_t run;\
    Int_t lsNo;\
    Int_t tstampOffline;\
    Int_t tstampOnline;\
    Double_t bField;\
    Double_t beamEnergy;\
    Double_t lumiOffline;\
    Double_t lumiOnline;\
    Char_t beamStatusOffline[15];\
    Char_t lumiSourceOffline[15];\
    Char_t beamStatusOnline[15];\
    Char_t lumiSourceOnline[15];\
};")
#from ROOT import CombinedLumiData


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

def mergeBrilcalc():
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
        
        csvDataOffline = {}
        #Read csv offline lumi data into dictionary
        try:
	    file = open(csvOfflinePattern.replace('__FILL__', str(fill)), 'r')
	except IOError:
	    print "Cannot open offline file for fill", fill
	    continue
        
        print "Processing offline fill ", str(fill) + "..."
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
            csvDataOffline[key] = line
        del file

        csvDataOnline = {}
        #Read csv offline lumi data into dictionary
        try:
	    file = open(csvOnlinePattern.replace('__FILL__', str(fill)), 'r')
	except IOError:
	    print "Cannot open online file for fill", fill
	    continue
        
        
        for line in file.readlines():
            #Skip commments
            line = line.split('#')[0].strip() 
            if not line:
                continue
        
            data = line.split(',')
            run, fill = data[0].strip().split(':')
            lsNo, dummy = data[1].strip().split(':')
            key = str(run) + '_' + str(lsNo)
            if key in csvDataOffline.keys():
                csvDataOnline[key] = line
        del file
                

        #Output
        rootFile = rootFilePattern.replace('__FILL__', str(fill))
	try:
	    fout = TFile(rootFile,'RECREATE')
	except IOError:
	    print "Cannot open file for output", rootFile
	    continue	 

	t = TTree('t', 'Combined Lumi from Brilcalc and Radmon data')
	
	rlData = CombinedLumiData()        
        t.Branch('lumiI', rlData, 'fill/I:fillStart/I:fillStable/I:fillEnd/I:durationStable/I:run/I:lsNo/I:tstampOffline/I:tstampOnline/I')
        t.Branch('lumiD', AddressOf(rlData, 'bField'), 'bField/D:beamEnergy/D:lumiOffline/D:lumiOnline/D')
        t.Branch('BeamStatusOffline', AddressOf(rlData, 'beamStatusOffline'), 'beamStatusOffline/C')
        t.Branch('LumiSourceOffline', AddressOf(rlData, 'lumiSourceOffline'), 'lumiSourceOffline/C')        
        t.Branch('BeamStatusOnline', AddressOf(rlData, 'beamStatusOnline'), 'beamStatusOnline/C')
        t.Branch('LumiSourceOnline', AddressOf(rlData, 'lumiSourceOnline'), 'lumiSourceOnline/C')    
        
        for key in sorted(csvDataOffline.keys()):
            data = csvDataOffline[key].split(',')
            run, fill = data[0].strip().split(':')
            lsNo, dummy = data[1].strip().split(':')
            
            rlData.fill = fillNo
            rlData.fillStart = fillStart
            rlData.fillStable = fillStable
            rlData.fillEnd = fillEnd
            rlData.durationStable = durationStable
            rlData.run = int(run)
            rlData.lsNo = int(lsNo)
            rlData.tstampOffline = int(data[2].strip())
            rlData.bField = bField
            rlData.beamEnergy = beamEnergy
            rlData.lumiOffline = float(data[5].strip())
            rlData.beamStatusOffline = data[3].strip()
            rlData.lumiSourceOffline = data[8].strip()

            if key not in csvDataOnline.keys():
                print "Key ", key, "not found in online for fill ", fillNo
                continue
            
            del data
            
            data = csvDataOnline[key].split(',')
            rlData.tstampOnline = int(data[2].strip())
            rlData.lumiOnline = float(data[5].strip())
            rlData.beamStatusOnline = data[3].strip()
            rlData.lumiSourceOnline = data[8].strip()

            t.Fill()
            
	print "Writing", rootFile
	fout.Write()
	fout.Close()
	del fout        
    	
        del csvDataOffline
        del csvDataOnline
        
    print nProccessed, "fills processed"        
    print nSkipped, "fills skipped"  
    

#===========================================================
if __name__ == "__main__": 
    mergeBrilcalc()
