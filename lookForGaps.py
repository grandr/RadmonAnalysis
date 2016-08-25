#!/usr/bin/env python
"""
-*- coding: UTF-8 -*-
Look for non-consecutive ls/nibbles in data
"""
import os,sys
sys.path.append("../Utils/")
from xutils import *
from fillReport import *
import glob
import tables as tb
from ROOT import *

fillReportName = '../Config/FillReport_1471882399398.xls'
dataFilesPattern = '/scr1/RadmonHd5/2016/*.hd5'

rootFile = "gapsHd5.root"


gROOT.ProcessLine(\
"struct Data{\
    Int_t fill;\
    Int_t run;\
    Int_t ls;\
    Int_t nb4;\
    Int_t tstamp;\
    Int_t lsprev;\
    Int_t nb4prev;\
    Int_t delta;\
    Int_t stable;\
};")

from ROOT import Data  


previous = {
    "file" : "",
    "fill" : 0,
    "run" : 0,
    "lsNo" : 0,
    "nb4No" : 0,
    "tstamp" : 0,
    }

current = {
    "file" : "",
    "fill" : 0,
    "run" : 0,
    "lsNo" : 0,
    "nb4No" : 0,
    "tstamp" : 0,
    }



def lookForGaps():
    
    fillReport = FillReport(fillReportName)
    fillStable = fillReport.getFillStableTime()
    fillEnd = fillReport.getFillEndTime()
    
    files =  glob.glob(dataFilesPattern)
    files.sort(key=os.path.getctime)
    
    veryFirst = 1
    nTotal = 0
    nTotalStable = 0
    nGaps = 0
    nGapsStable = 0
    
    data = Data()
    fout = TFile(rootFile,'RECREATE')
    tree = TTree('t', 'Radmon gaps')
    tree.Branch('data', data, 'fill/I:run/I:ls/I:nb4/I:tstamp/I:lsprev/I:nb4prev/I:delta/I:stable/I')
    
    for filename in files:
        print "Processing", filename
        f=tb.open_file(filename,'r')
        tablelist = f.root._v_children.keys()
        for t in tablelist:
            n = f.getNode('/'+t)
            if t != 'radmonlumi': continue 
            for i in n.iterrows():
                current['fill'] = int(i['fillnum'])
                current['file'] = filename
                current['run'] = int(i['runnum'])
                current['lsNo'] = int(i['lsnum'])
                current['tstamp'] = int(i['timestampsec'])
                current['nb4No'] = int(i['nbnum'])
                
                nTotal += 1
                
                if veryFirst:
                    veryFirst = 0
                else:
                    #Within the same run number nb4No  should differ either by 4 or by -60
                    if current['run'] != previous['run']:
                        pass
                    else:
                        delta = current['nb4No'] - previous['nb4No']
                        if abs(delta) != 4 and abs(delta) != 60:
                            nGaps += 1
                            
                            data.stable = 0
                            tsUtc = local2utc(current['tstamp'])
                            try:
                                startStable = fillStable[str(current['fill'])]
                                endStable = fillEnd[str(current['fill'])]
                            except:
                                print "No fillreport data for fill", current['fill']
                                startStable = 0
                                endStable = 0
                                
                            if tsUtc > startStable and tsUtc < endStable:
                                nGapsStable += 1
                                data.stable = 1
                                #print "Stable Beams!"
                                
                            lPrevious = []
                            lPrevious.append("Previous:\t")
                            lCurrent = []
                            lCurrent.append("Current:\t")
                            for key in current.keys():
                                lCurrent.append(str(key) + ":" + str(current[key]) + ", ") 
                                lPrevious.append(str(key) + ":" + str(previous[key]) + ", ") 
                            
                            data.fill = current['fill']
                            data.run = current['run'] 
                            data.ls = current['lsNo']
                            data.nb4 = current['nb4No']
                            data.tstamp = current['tstamp']
                            data.lsprev = previous['lsNo']
                            data.nb4prev =  previous['nb4No']
                            data.delta = delta
                            
                            tree.Fill()
                            
                            #print ' '.join(lPrevious)
                            #print ' '.join(lCurrent)
                            #print "======"
                for key in current.keys():
                    previous[key] = current[key]
                
                
        
        f.close()
        del f
    
    fout.Write()
    fout.Close()
    print "=============================="
    print "Summary"
    print "No of records:\t\t", nTotal
    print "No of gaps:\t\t", nGaps
    print "Gaps in stable beam:\t", nGapsStable
                
        
    
    
    

#===========================================================
if __name__ == "__main__":
    lookForGaps()    
