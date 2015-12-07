#!/usr/bin/env python

"""
-*- coding: UTF-8 -*-
Re-write radmon raw data into single root tree (one file per fill) + add running sums

"""
import sys, os
from array import array
from ROOT import *
import math
from array import array
from xutils import *
from fillReport import *
import numpy as np

hrs = 4

#Minutes before/after fillStable/fillEnd
deltaMinutes = 10

#fills = [4565]
#
fills = [ 3960, 3962, 3965, 3971, 3974,3976, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257, 4266, 4268, 4269, 4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467,4476, 4477, 4479, 4485, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4560, 4562, 4565, 4569]

RadmonDataDir = '/home/data/RadMonData/RawData'
radmonFilePattern = 'HFRadmonData*.root'
radmonFillPattern = '/home/data/RadMonData/RadmonFills/radmon__XXX__.root'

fillReportName = '/home/grandr/cms/Bril/Analysis/ToOnlineLumi/FillReport_1446656923991.xls'

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
    
    fillReport = FillReport(fillReportName)
    
    for fill in fills:
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
        rootFile = radmonFillPattern.replace('__XXX__', str(fill))
        try:
	    fout = TFile(rootFile,'RECREATE')
	except IOError:
	    print "Cannot open file for output", rootFile
	    exit	 
	t = TTree('t', 'Radmon rates')
	t.Branch('fillBranchI', fillData, 'fill/I:fillStart/I:fillStable/I:fillEnd/I:durationStable/I')
	t.Branch('fillBranchD', AddressOf(fillData, 'bField'), 'bField/D:beamEnergy/D')
	t.Branch('radmonBranchI', radmonData, 'tstamp/I:status[16]/I')
	t.Branch('radmonRates', AddressOf(radmonData, 'rates'), 'rates[16]/D')
	#t.Branch('radmonSums', runningSums, 'rsums[28800]/D')
	
        tsStart =  fillReport.getFillCreationTime(fill)
	tsEnd = fillReport.getFillEndTime(fill)
	tsStable = fillReport.getFillStableTime(fill)
	duration = fillReport.getFillDuration(fill)
	bField = fillReport.getFillField(fill)
	beamEnergy = fillReport.getFillBeamEnergy(fill)
	
	fromto = [tsStart-hrs*3600, tsEnd+hrs*3600]
        filelist =  get_filelist(RadmonDataDir, radmonFilePattern, fromto)
	chain = TChain("Rate")
        for file in filelist:
            chain.Add(file)

        for i in range(chain.GetEntries()):
            chain.GetEntry(i)    
        
            #if tsStart - chain.tstamp < 1800:
            if chain.tstamp > tsStart and chain.tstamp < tsEnd:
                for j in range(0, 16):
                    #rsumsList[j].append(chain.rates[j])
                    #rsumsList[j].pop(0)
                    radmonData.rates[j] = chain.rates[j]
                
                #runningSums.rsums = np.asarray(rsumsList).ravel()
                
                #nparray = np.asarray(rsumsList).ravel()
 
                #for j in range(0, 16*1800):
                    #runningSums.rsums[j] = nparray[j]
                
                #nump2d = np.reshape(nump, (-1,1800))  (To get back to 2D)
            
            #if chain.tstamp > tsStable - deltaMinutes*60 and chain.tstamp < tsEnd + deltaMinutes*60:
                radmonData.tstamp = chain.tstamp
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
