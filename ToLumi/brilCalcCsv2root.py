#!/usr/bin/env python

"""
-*- coding: UTF-8 -*-
Convert selected entries from bricalc csv file to root ntuple
"""
import sys, os
from array import array
from ROOT import *
import math

import re
sys.path.append("../Utils/")
from xutils import *
from fillReport import *

#
fillReportName = '../Config/FillReport17.xls'
csvFilePattern = '/scr1/RadMonLumi/2017/OfflineLumi/Brilcalc_normtag_BRIL/brilcalcLumiFill__XXX__.csv'
rootFilePattern = '/scr1/RadMonLumi/2017/OfflineLumi/Brilcalc_normtag_BRIL_Root/brilcalcLumiFill__XXX__.root'


gROOT.ProcessLine(\
"struct LumiData{\
    Int_t fill;\
    Int_t run;\
    Int_t lsNo;\
    Int_t tstamp;\
    Double_t beamEnergy;\
    Double_t lumi;\
    Char_t beamStatus[15];\
    Char_t lumiSource[15];\
};")

#from ROOT import LumiData

def brilCalc2root():
    #ROOT.gRoot.Reset()
    #Fills to do
    fillReport = FillReport(fillReportName)
    fillStarted = fillReport.getFillCreationTime()
    fills = sorted(fillStarted.keys())
    
    for fill in fills:
	print "Processing fill", fill
	file = csvFilePattern.replace('__XXX__', str(fill))
	rootFile = rootFilePattern.replace('__XXX__', str(fill))
	
	try:
	    fin = open(file, 'r')
	except IOError:
	    print "Cannot open file", file
	    continue
		
	try:
	    fout = TFile(rootFile,'RECREATE')
	except IOError:
	    print "Cannot open file for output", rootFile
	    continue
        
        t = TTree('t', 'Fill CSV data')
	lumiData = LumiData()
        t.Branch('LumiData',  lumiData, 'fill/I:run/I:lsNo/I:tstamp/I:beamEnergy/D:lumi/D')
        t.Branch('BeamStatus', AddressOf(lumiData, 'beamStatus'), 'beamStatus/C')
        t.Branch('LumiSource', AddressOf(lumiData, 'lumiSource'), 'lumiSource/C')
        
        for line in fin.readlines():
            line = line.split('#')[0].strip() 
        
            if not line:
                continue
        
            data = line.split(',')
            run, fill = data[0].strip().split(':')
            
            lumiData.fill = int(fill)
            lumiData.run = int(run)
            
            lsNo, dummy = data[1].strip().split(':')
            lumiData.lsNo = int(lsNo)
            
            lumiData.tstamp = int(data[2].strip())
            lumiData.beamEnergy = float(data[4].strip())
            lumiData.lumi = float(data[5].strip())
            
            lumiData.beamStatus = data[3].strip()
            lumiData.lumiSource = data[8].strip()
            
            t.Fill()
            del data
        del fin
 	print "Writing", rootFile
	fout.Write()
	fout.Close()
	del fout       
        
#===========================================================
if __name__ == "__main__": 
    brilCalc2root()
            
        
        
        
        
       
