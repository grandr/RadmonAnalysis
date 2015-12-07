#!/usr/bin/env python

"""
-*- coding: UTF-8 -*-
Convert selected entries from fillcsv file to root ntuple
"""
import sys, os
from array import array
from ROOT import *
import math
from xutils import *

fills = [3960, 3962, 3965, 3971, 3974, 3976, 3981, 3983, 3986, 3988, 3992, 3996]
#fills = [4008, 4201, 4220, 4224, 4225]
csvFilePattern = '/run/media/grandr/ADATA/RadMonData/BrilData/fillcsv/Fill__XXX__.csv'
rootFilePattern = '/run/media/grandr/ADATA/RadMonData/BrilData/fillRoot/fill__XXX__.root'

os.environ['TZ'] =  'Europe/Zurich' # to convert local timestamp to UTC

gROOT.ProcessLine(\
"struct LumiData{\
Double_t fill;\
Double_t run;\
Double_t lsno;\
Double_t nb4;\
Double_t secs;\
Double_t secsUtc;\
Double_t msecs;\
Double_t deadfrac;\
Double_t primaryLumi;\
Double_t hf;\
Double_t hfRaw;\
Double_t plt;\
Double_t pltRaw;\
Double_t pltZero;\
Double_t pltZeroRaw;\
Double_t bcmf;\
Double_t bcmfRaw;\
};")
from ROOT import LumiData  

def main():
    gROOT.Reset()
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
	t.Branch('numBranch',  lumiData, 'fill/D:run/D:lsno/D:nb4/D:secs/D:secsUtc/D:msecs/D:deadfrac/D:primaryLumi/D:hf/D:hfRaw/d:plt/D:pltRaw/D:pltZero/D:pltZeroRaw/D:bcmf/D:bcmfRaw/D')

	first = 1 # to skip the header
	
	for line in fin.readlines():
	    #Skip header
	    if first:
		first = 0
		continue
	    
	    data = line.split(',')
	    
	    lumiData.fill = float(data[0].replace('FILL', ''))
	    lumiData.run = float(data[1])
	    lumiData.lsno = float(data[2])
	    lumiData.nb4 = float(data[3])
	    lumiData.secs = float(data[5])
	    lumiData.secsUtc = float(local2utc(int(data[5])))
	    lumiData.msecs = float(data[6])
	    lumiData.deadfrac = float(data[7])
	    lumiData.primaryLumi = float(data[9])
	    lumiData.hf = float(data[10])
	    lumiData.hfRaw = float(data[11])
	    lumiData.plt = float(data[12])
	    lumiData.pltRaw = float(data[3])
	    lumiData.pltZero = float(data[14])
	    lumiData.pltZeroRaw = float(data[15])
	    lumiData.bcmf = float(data[16])
	    lumiData.bcmfRaw = float(data[17])

	    t.Fill()
	    del data
	del fin

	print "Writing", rootFile
	fout.Write()
	fout.Close()
	del fout
	
#===========================================================
if __name__ == "__main__":
    main()

    
	
    