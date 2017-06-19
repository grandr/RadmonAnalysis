#!/usr/bin/env python
"""
# Merge csv lumi info and rate info from hd5 files into one root file
# (One file per fill)
# -*- coding: UTF-8 -*-
"""

import sys, os
import re
from array import array
sys.path.append("../Utils/")
from xutils import *
from fillReport import *
#from ROOT import *
import ROOT
import numpy as np
import math

nDets = 16
rateMax = 40000

fillReportName = '../Config/FillReport17.xls'
csvPattern = '/scr1/RadMonLumi/2017/OfflineLumi/Brilcalc_normtag_BRIL/brilcalcLumiFill__FILL__.csv'
radmonPattern = '/scr1/RadmonFills/2017/radmon__FILL__.root'
outputPattern = '/scr1/RadMonLumi/2017/OfflineLumi/Radmon_Root_normtag_BRIL/radmonLumiRoot_normtag_BRIL___FILL__.root'

ROOT.gROOT.ProcessLine(\
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
from ROOT import RadmonLumiData

class DataHandler:
    
    def __init__(self, fill):
	self.fill = fill
        self.xx = array("d", [])
        
    
    def setFillInfo(self,  fillStart, fillStable, fillEnd, durationStable, bField, beamEnergy):
        """
        add information from fill fillReport
        """
        self.fillStart = fillStart
        self.fillStable = fillStable
        self.fillEnd = fillEnd
        self.durationStable = durationStable
        self.bField = bField
        self.beamEnergy = beamEnergy
        
        
    def readLumiData(self):
        """
        read csv file with brilcalc data
        """
        
        self.csvData = {}
        #Read csv lumi data into dictionary
        try:
	    file = open(csvPattern.replace('__FILL__', str(self.fill)), 'r')
	except IOError:
	    print "Cannot open lumi data file for fill", self.fill
	    return 0
        
        print "Reading Lumi data for fill", self.fill
        
        for line in file.readlines():
            #Skip commments
            line = line.split('#')[0].strip() 
            if not line:
                continue
        
            data = line.split(',')
            key = int(data[2])    # Key is timestamp
            self.xx.append(float(key))
            self.csvData[key] = line
        del file
        return 1
               
    def readRadmonData(self):
        """
        read corresonding root file and fill TProfiles with le's corresponding to the LS starts
        """
        if os.path.exists(radmonPattern.replace('__FILL__', str(self.fill))):
            f = ROOT.TFile(radmonPattern.replace('__FILL__', str(self.fill)))
        else:
            print "Cannot open radmon data file for fill", self.fill
            return 0         

        print "Reading Radmon data for fill", self.fill

        self.hradmon = []
        for i in range(nDets):
	    self.hradmon.append(ROOT.TProfile('hradmon' + str(i), 'Radmon Rate ' + str(i), len(self.xx) - 1, self.xx))
	    self.hradmon[i].SetDirectory(0)
                
        t = f.Get("t")

        for i in range(0, t.GetEntries()):
            nb = t.GetEntry(i)
            if nb < 0:
                continue  
            
            #Convert utc tstamp to local
            tstamp = utc2local(t.tstamp)
            for j in range(len(self.hradmon)):
		if t.rates[j] < rateMax:
		    self.hradmon[j].Fill(float(tstamp), t.rates[j])
		    
        del f
        return 1
		            

    def writeOutput(self):
        """
        Write combine radmon and lumi data
        """
        
        rootFile = outputPattern.replace('__FILL__', str(self.fill))
	try:
	    fout = ROOT.TFile(rootFile,'RECREATE')
	except IOError:
	    print "Cannot open file for output", rootFile
	    return 0	 

	t = ROOT.TTree('t', 'Combined  Lumi from Brilcalc and Radmon data')
	
	rlData = RadmonLumiData()        
        t.Branch('radmonLumiI', rlData, 'fill/I:fillStart/I:fillStable/I:fillEnd/I:durationStable/I:run/I:lsNo/I:tstamp/I')
        t.Branch('radmonLumiD', ROOT.AddressOf(rlData, 'bField'), 'bField/D:beamEnergy/D:lumi/D:rates[16]/D:drates[16]/D:nibbles[16]/D')
        t.Branch('BeamStatus', ROOT.AddressOf(rlData, 'beamStatus'), 'beamStatus/C')
        t.Branch('LumiSource', ROOT.AddressOf(rlData, 'lumiSource'), 'lumiSource/C')        
        
        

        
        #nBins = self.hradmon[0].GetNBinsX()
        for i in range(len(self.xx)):
            key = int(self.xx[i])
            
            #Fill data
            rlData.fill = int(self.fill)
            rlData.fillStart = self.fillStart
            rlData.fillStable = self.fillStable
            rlData.fillEnd = self.fillEnd
            rlData.durationStable = self.durationStable
            rlData.bField = self.bField
            rlData.beamEnergy = self.beamEnergy     
            
            

            #Radmon data
            for j in range(nDets):
		rlData.rates[j] = self.hradmon[j].GetBinContent(i+1)
		rlData.drates[j] = self.hradmon[j].GetBinError(i+1)
		rlData.nibbles[j] = 0.
            
            rlData.tstamp = key
            rlData.tstamp = self.hradmon[0].GetBinCenter(i+1)
            
            #Lumi data
            if key in self.csvData.keys():
                data = self.csvData[key].split(',')
                run, fill = data[0].strip().split(':')
                lsNo, dummy = data[1].strip().split(':')
                rlData.run = int(run)
                rlData.lsNo = int(lsNo)
                rlData.lumi = float(data[5].strip())
                rlData.beamStatus = data[3].strip()
                rlData.lumiSource = data[8].strip()                
            else:
                print "Cannot find lumi data "
                rlData.run = -1
                rlData.lsNo = -1
                rlData.lumi = -1
                rlData.beamStatus = "None"
                rlData.lumiSource = "None"
            
            t.Fill()
        
        print "Writing", rootFile
	fout.Write()
	fout.Close()
	del fout   

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

def main():
    #Fills to do
    fillReport = FillReport(fillReportName)
    fillStarted = fillReport.getFillCreationTime()
    #Fills already processed
    fillsDone = getFilesDone(outputPattern.replace('__FILL__', '*'))

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

        dh = DataHandler(fill)
        dh.setFillInfo( fillStart, fillStable, fillEnd, durationStable, bField, beamEnergy)
        if not dh.readLumiData():  
            continue
        if not dh.readRadmonData():
            continue
        dh.writeOutput()
    
        del dh
        
#===========================================================
if __name__ == "__main__":
    main()

    
	        
        
        
