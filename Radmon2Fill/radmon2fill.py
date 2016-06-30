#!/usr/bin/env python

"""
-*- coding: UTF-8 -*-
Re-write radmon raw data into single root tree (one file per fill) + add running sums

"""
import sys, os
sys.path.append("../Utils/")
from array import array
from ROOT import *
import math
from xutils import *
from fillReport import *
import numpy as np
import glob


hrs = 4

#Minutes before/after fillStable/fillEnd
deltaMinutes = 10

fillReportName = '../Config/FillReport.xls'

RadmonDataDir = '/scr1/RadMonData/'
radmonFilePattern = 'HFRadmonData*.root'
radmonFillPattern = '/scr1/RadmonFills/2016/radmon*.root'

gROOT.ProcessLine(\
"struct FillData{\
    Int_t fill;\
    Int_t fillStart;\
    Int_t fillStable;\
    Int_t fillEnd;\
    Int_t durationStable;\
    Double_t bField;\
    Double_t beamEnergy;\
};")
from ROOT import FillData  

gROOT.ProcessLine(\
"struct RadmonData{\
    Int_t tstamp;\
    Int_t status[16];\
    Double_t rates[16];\
};")

from ROOT import RadmonData

#gROOT.ProcessLine(\
#"struct RunningSums{\
    #Double_t rsums[16*1800];\
#};")

#from ROOT import RunningSums

def radmon2fill():
    
    #Get fills already processed
    filesDone = glob.glob(radmonFillPattern)
    (toReplace, dummy) = radmonFillPattern.split('.')
    print filesDone
    fillsDone = []
    for file in filesDone:
        name, ext = file.split('.')
        fillsDone.append(int(name.replace(toReplace[0:-1], "")))
    if len(fillsDone) > 0:
        print "Fills already done", fillsDone
    
    fillReport = FillReport(fillReportName)
    #Start/End of each fill in fillReport
    fillStarted = fillReport.getFillCreationTime()
    fillDumped = fillReport.getFillEndTime()
    
    for fill in sorted(fillStarted.keys()):
        
        if int(fill) in fillsDone:
            print "Fill", fill, "is already processed. Skipping..."
            continue
        print "Processing fill", fill, "........."
        
        fillData = FillData()
        radmonData = RadmonData()
        #runningSums = RunningSums()
        
        #rsumsList = []
        for i in range(0, 16):
            #rsumsList.insert(i, [0.]*1800)
            radmonData.rates[i] = 0.
            radmonData.status[i] = 0.

            
        #Output
        rootFile = radmonFillPattern.replace("*", str(fill))
        try:
	    fout = TFile(rootFile,'RECREATE')
	except IOError:
	    print "Cannot open file for output", rootFile
	    exit	 
	t = TTree('t', 'Radmon rates')
	t.Branch('fillBranchI', fillData, 'fill/I:fillStart/I:fillStable/I:fillEnd/I:durationStable/I')
	t.Branch('fillBranchD', AddressOf(fillData, 'bField'), 'bField/D:beamEnergy/D')
	t.Branch('radmonBranchI', radmonData, 'tstamp/I:status[16]/I')
	t.Branch('radmonBranchD', AddressOf(radmonData, 'rates'), 'rates[16]/D')
	#t.Branch('radmonSums', runningSums, 'rsums[28800]/D')
	
        tsStart =  fillStarted[fill]
	tsEnd = fillDumped[fill]
	tsStable = fillReport.getFillStableTime(int(fill))
	duration = fillReport.getFillDuration(int(fill))
	bField = fillReport.getFillField(int(fill))
	beamEnergy = fillReport.getFillBeamEnergy(int(fill))
	
	fromto = [tsStart-hrs*3600, tsEnd+hrs*3600]
        filelist =  get_filelist(RadmonDataDir, radmonFilePattern, fromto)
        
        
        print "Files used:"
	chain = TChain("Rate")
        for file in filelist:
            print file
            chain.Add(file)

        fillData.fillStart = tsStart
        fillData.fillStable = tsStable
        fillData.fillEnd = tsEnd
        fillData.durationStable = duration
        fillData.bField = bField
        fillData.beamEnergy = beamEnergy
        
        for i in range(chain.GetEntries()):
            chain.GetEntry(i)    
        
            #if tsStart - chain.tstamp < 1800:
            if chain.tstamp > tsStart and chain.tstamp < tsEnd:
                radmonData.tstamp = chain.tstamp
                for j in range(0, 16):
                    #rsumsList[j].append(chain.rates[j])
                    #rsumsList[j].pop(0)
                    radmonData.rates[j] = chain.rates[j]
                    radmonData.status[j] = chain.status[j]
                
                #runningSums.rsums = np.asarray(rsumsList).ravel()
                
                #nparray = np.asarray(rsumsList).ravel()
 
                #for j in range(0, 16*1800):
                    #runningSums.rsums[j] = nparray[j]
                
                #nump2d = np.reshape(nump, (-1,1800))  (To get back to 2D)
            
            #if chain.tstamp > tsStable - deltaMinutes*60 and chain.tstamp < tsEnd + deltaMinutes*60:

                t.Fill()

        fout.Write()
        fout.Close()
        
        del chain
        del fillData
        del radmonData
        #del runningSums
        del t
        del fout
#===========================================================
if __name__ == "__main__":
    radmon2fill()
