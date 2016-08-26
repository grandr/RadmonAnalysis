#!/usr/bin/env python

"""
-*- coding: UTF-8 -*-
Check time between 2 reads in root files

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

gROOT.ProcessLine(\
"struct Data{\
    Int_t fill;\
    Int_t tstamp;\
    Int_t delta;\
    Int_t stable;\
};")
from ROOT import Data  

fillReportName = '../Config/FillReport_1471882399398.xls'
dataFilesPattern = '/scr1/RadmonFills/2016/radmon*.root'
rootFile = "rootDelta.root"

def rootDelta():
    fillReport = FillReport(fillReportName)
    fillStable = fillReport.getFillStableTime()
    fillEnd = fillReport.getFillEndTime()
    
    files =  glob.glob(dataFilesPattern)
    files.sort(key=os.path.getctime)
    
    veryFirst = 1    
    tsprev = 0
    tstamp = 0
    
    data = Data()
    fout = TFile(rootFile,'RECREATE')
    t = TTree('t', 'Radmon delta read')
    t.Branch('data', data, 'fill/I:tstamp/I:delta/I:stable/I')
    #t.SetDirectory(0)
    
    for filename in files:
        print "Processing", filename
        f = TFile(filename)
        tree = f.Get("t")
        for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue    
            
            if veryFirst:
                veryFirst = 0
            else:
                data.fill = tree.fill
                data.tstamp = tree.tstamp
                data.delta = tree.tstamp - tsprev
                if tree.tstamp > tree.fillStable and tree.tstamp < tree.fillEnd:
                    data.stable = 1
                else:
                    data.stable = 0
                t.Fill()
            tsprev = tree.tstamp
        del tree
    fout.Write()
    fout.Close()
    
#===========================================================
if __name__ == "__main__":
    rootDelta()     
