#!/usr/bin/env python

"""
-*- coding: UTF-8 -*-
Convert selected entries from bricalc csv file to root ntuple
"""
import sys, os
from array import array
from ROOT import *
import math
from xutils import *

fills = [3960, 3962, 3965, 3971, 3974, 3976, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257, 4266, 4268, 4269, 4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467, 4476, 4477, 4479, 4485, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4560, 4562, 4565, 4569]

#Book
csvFilePattern = '/run/media/grandr/BDATA/RadMonData/BrilCalcData/FillCsv/fill__XXX__.csv'
rootFilePattern = '/run/media/grandr/BDATA/RadMonData/BrilCalcData/FillRoot/fill__XXX__.root'

##lxplus
#csvFilePattern = '/afs/cern.ch/work/g/grandr/Bril/Brilcalc/FillCsv/fill__XXX__.csv'
#rootFilePattern = '/afs/cern.ch/work/g/grandr/Bril/Brilcalc/FillRoot/fill__XXX__.root'

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
            
        
        
        
        
       
