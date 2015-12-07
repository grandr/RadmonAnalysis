#!/usr/bin/env python

"""
-*- coding: UTF-8 -*-
Check LS start/ends and compare fill parameters from fillReport file and DB

"""
import sys, os
from array import array
from ROOT import *
import math
from array import array
from xutils import *
from fillReport import *

fills = [4505, 4540]

fillReportName = '/home/grandr/cms/Bril/Analysis/ToOnlineLumi/FillReport_1446656923991.xls'
lumiFilePattern = '/home/data/OnlineLumidata/lumi__XXX__.root'

def main():
    
    fillReport = FillReport(fillReportName)
    
    for fill in fills:
        f = TFile(lumiFilePattern.replace('__XXX__', str(fill)))
	tree = f.Get("t")
	
        for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    
	    lsPrevious = 0
            for i in range(0, tree.GetEntries()) :
                lsStart = tree.lsStart + tree.lsStartMs/1000000.
                lsEnd = tree.lsEnd + tree.lsEndMs/1000000.
                #if i>0:
                    #print lsStart - lsPrevious
                lsPrevious = lsEnd
                print tree.fillStart - fillReport.getFillCreationTime(fill)
#===========================================================
if __name__ == "__main__":
    main()
    