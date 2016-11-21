#!/usr/bin/env python
"""
-*- coding: UTF-8 -*-
Extract fills from hd5 data (one file per fill)
Fills to be processed taken from FillReport_***.xls files
"""
import os,sys
sys.path.append("../Utils/")
from xutils import *
from fillReport import *
import glob
import tables 

dataTables = ['radmonraw', 'radmonlumi', 'radmonflux']

compressionfilters=tables.Filters(complevel=5, complib='blosc')
chunkshape=(100,)


filters = {}
filters['radmonraw'] = """(fillnum==%d)"""
filters['radmonlumi'] = """(fillnum==%d)"""
filters['radmonflux'] = """(fillnum==%d)"""


# We have about 8 hours per file. Let's double this value to be safe
hoursBefore = 16

#fillReportName = '../Config/FillReport.xls'
fillReportName = '../Config/FillReportPPb_1479721242035.xls'
fillsPattern = '/scr1/RadmonHd5/Fills2016/radmon*.hd5'
dataFilesPattern = '/scr1/RadmonHd5/2016/*.hd5'
dataFiles = {}

def mergefiles(sourcefiles, outfilename, fillnum): 
    nf = tables.open_file(outfilename,mode='w')    
    for sf in sourcefiles:
        sfile = None
        try:
            sfile = tables.open_file(sf,'r')
        except tables.exceptions.HDF5ExtError:
            print 'File open error %s'%sf
            continue
        tablelist = sfile.root._v_children.keys()  
        for t in tablelist:
            if t not in dataTables: continue
            thistab = sfile.getNode('/'+t)
            desc = thistab.description._v_colobjects.copy()  
            try:
                atab = nf.createTable('/',t,desc,filters=compressionfilters,chunkshape=chunkshape)
            except tables.exceptions.NodeError:
                pass 
            desttab = nf.getNode('/'+t)
            selection = filters[t]%fillnum            
            thistab.append_where(desttab,selection)             
        if sfile: sfile.close()    
    nf.close()


def fillExtractHd5():
    
    #Get fills already processed
    filesDone = glob.glob(fillsPattern)
    (toReplace, dummy) = fillsPattern.split('.')
    fillsDone = []
    for file in filesDone:
        name, ext = file.split('.')
        fillsDone.append(int(name.replace(toReplace[0:-1], "")))
    print "Done", fillsDone    
    # Start/stop time for fills in xls file
    fillReport = FillReport(fillReportName)
    fillStarted = fillReport.getFillCreationTime()
    fillDumped = fillReport.getFillEndTime()
    
   
    #Make dictionary with all files in dataDir. They key is filecreation timestamp(utc)
    allFiles = glob.glob(dataFilesPattern)
    for file in allFiles:
        (dummy, dtime, dummy) = file.split('_')
        tsLocal = timepar2ts(dtime)
        key = local2utc(tsLocal)
        dataFiles[key] = file
    del allFiles

    #Loop over fills in xls file
    for fill in sorted(fillStarted.keys()):
        
        if int(fill) in fillsDone:
            print "Fill", fill, "is already processed. Skipping..."
            continue
        
        filesSelected = []
        tsStart =  int(fillStarted[fill])
        tsEnd = int(fillDumped[fill])
        
        for key in sorted(dataFiles.keys()):
            if int(key) >= tsStart - 3600*hoursBefore and int(key) <= tsEnd:
                filesSelected.append(dataFiles[key])
        if len(filesSelected) <= 0:
            print "No data files found for fill", str(fill)
            continue
        print 'Processing fill', str(fill), '...'
        #print "Files used:\n", '\n'.join(filesSelected)
        outFile = fillsPattern.replace("*", str(fill))
        mergefiles(filesSelected, outFile, int(fill))
        print "Output written in", outFile
        
        del filesSelected
            
#===========================================================
if __name__ == "__main__":
    fillExtractHd5()
