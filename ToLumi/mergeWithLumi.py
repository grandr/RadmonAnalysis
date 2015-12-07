#!/usr/bin/env python

"""
-*- coding: UTF-8 -*-
Merge RadmonData & LumiData based on run/ls
"""
import sys, os
from array import array
from ROOT import *
import datetime
import math
from xutils import *
from fillReport import *

#fills = [3960, 3962, 3965, 3971, 3974, 3976, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257, 4266, 4268, 4269, 4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467, 4476, 4477, 4479, 4485, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4560, 4562, 4565, 4569]

fills = [4393]

dataRoot = '/home/data'
if not os.environ.has_key('DATA_ROOT'):
    os.environ['DATA_ROOT'] = dataRoot

fillReportName = '/home/grandr/cms/Bril/Analysis/ToLumi/FillReport_1446656923991.xls'

lumiFilePattern = '/home/data/RadMonData/BrilCalcData/FillRoot/fill__XXX__.root'
RadmonDataDir = '/home/data/RadMonData/RawData'
radmonFilePattern = 'HFRadmonData*'
radmonLumiFilePattern = '/home/data/RadMonData/RadMonLumiOffline/radmonlumi__XXX__.root'

# temporary fix (rate higher than this value means that detector is being turned on)
rateMax = 50000. 

lRange = 2.

nYbins = 10000  # Y bins for 2D histogram
hrs = 4  # hours before/after fromto

# yMax for radmon rate 2D histograms (RX and Racks)
nRange = [1., 1., 1., 1., 1., 6., 6., 1., 6., 6., 1., 6., 6., 1., 6., 6.]
#iRbx = [5, 6, 8, 9, 11, 12, 14, 15]
#iRacks = [4, 7, 10, 13, 0, 1, 2, 3]    

#Output Structures
# by LS data (filled during the first pass)
gROOT.ProcessLine(\
"struct LsData{\
    Int_t fill;\
    Int_t fillStart;\
    Int_t fillStable;\
    Int_t fillEnd;\
    Int_t durationStable;\
    Int_t run;\
    Int_t lsNo;\
    Int_t lsDuration;\
    Int_t tstamp;\
    Double_t lumi;\
    Double_t bField;\
    Double_t beamEnergy;\
    Char_t beamStatus[15];\
    Char_t lumiSource[15];\
};")
from ROOT import LsData


gROOT.ProcessLine(\
"struct RadmonData{\
    Double_t rates[16];\
    Double_t ratesErr[16];\
};")
from ROOT import RadmonData

class DataHandler:
    
    def __init__(self, fill):
	self.fill = fill
	# Time range
	self.fromto = [99999999999, -1]
	# low edges for histograms
	self.xx = array("d", [])
	# ByLS-data stored in list on the first pass
	self.lsDataList = []
	self.yMax = -100000.
	self.yMin = 1000000.
	self.lsDuration = []

	
    def setupRanges(self):
	"""
	read file with lumi data 
	setup low edges of histograms corresponding to the beginning of lumisections
	fill array of timing  structures (fill, ls, run etc) corresponding to the given bin
	"""
		
	f = TFile(lumiFilePattern.replace('__XXX__', str(self.fill)))
	tree = f.Get("t")
	
	tsPrev = 0
	
	# Data from fill report file
        fillReport = FillReport(fillReportName)
	
	for i in range(0, tree.GetEntries()) :
            lsDataEntry = LsData()
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue

	    #Y range for histograms
	    if tree.lumi > self.yMax:
		 self.yMax = tree.lumi
	    if tree.lumi < self.yMin:
		 self.yMin = tree.lumi
		
	    #Setting start/end of the fill
	    if  tree.tstamp < self.fromto[0]:
		self.fromto[0] = tree.tstamp
	    if tree.tstamp > self.fromto[1]:
		self.fromto[1] = tree.tstamp

	    #Low edges for histos (start of the LS)

            
            if i > 0:
                self.lsDuration.insert(i-1, tree.tstamp - tsPrev)
                # Found negative duration of LS
                if self.lsDuration[i-1] < 0:
                    continue
            tsPrev = tree.tstamp
            self.xx.append(tree.tstamp)
            
            fill = int(tree.fill)
            # fill by-LS  data
            lsDataEntry.fill = fill
            lsDataEntry.fillStart = fillReport.getFillCreationTime(fill)
            lsDataEntry.fillStable = fillReport.getFillStableTime(fill)
            lsDataEntry.fillEnd = fillReport.getFillEndTime(fill)
            lsDataEntry.durationStable = fillReport.getFillDuration(fill)
            lsDataEntry.bField = fillReport.getFillField(fill)
            lsDataEntry.beamEnergy = tree.beamEnergy
            lsDataEntry.run = tree.run
            lsDataEntry.lsNo = tree.lsNo
            lsDataEntry.lsDuration = 0  # will be overwritten later
            lsDataEntry.tstamp = tree.tstamp
            lsDataEntry.lumi = tree.lumi # will be scaled on the second pass
            lsDataEntry.beamStatus = tree.beamStatus
            lsDataEntry.lumiSource = tree.lumiSource
            
            self.lsDataList.append(lsDataEntry)
            del lsDataEntry
	del tree
	del f

    def scaleLumi(self):
        """
        Calculate average instant lumi per ls and overwrite lsDuration
        """
        
        for i in range(0, len(self.lsDataList)-1) :
            self.lsDataList[i].lsDuration = self.lsDuration[i]
            if self.lsDuration[i]>0:
                self.lsDataList[i].lumi /=  self.lsDuration[i]
            else:
                self.lsDataList[i].lumi = -1.

                
    def bookRadmonHistos(self):
	self.setupRanges()
	self.scaleLumi()
	
	self.hradmon = []
        #for i in range(0, len(self.xx)-1):
            #if self.xx[i+1] - self.xx[i] < 0.:
                ##print self.xx[i+1] - self.xx[i], i, self.xx[i+1], self.xx[i]
                #print "==="
                #print datetime.fromtimestamp(int(self.xx[i])).strftime('%Y-%m-%d %H:%M:%S')
                #print datetime.fromtimestamp(int(self.xx[i+1])).strftime('%Y-%m-%d %H:%M:%S')
                #print "==="
	for i in range(len(nRange)):
	    self.hradmon.append(TH2D('hradmon' + str(i), 'Radmon Rate ' + str(i), len(self.xx) - 1, self.xx, nYbins, self.yMin/24., self.yMax*nRange[i]/24.))

	#self.hradmon[10].Draw()
 	#raw_input("Press enter to continue") 
 	
    def fillRadmonHistos(self):
	self.fromto[0] -=  hrs*3600
	self.fromto[1] +=  hrs*3600
	filelist =  get_filelist(RadmonDataDir, radmonFilePattern, self.fromto)
	chain = TChain("Rate")
        for file in filelist:
            chain.Add(file)
        
        for i in range(chain.GetEntries()):
            chain.GetEntry(i)    
            
            for j in range(len(self.hradmon)):
		if chain.rates[j] < rateMax:
		    self.hradmon[j].Fill(float(chain.tstamp), chain.rates[j])
		    
	#self.hradmon[6].Draw()
 	#raw_input("Press enter to continue")
	del chain
	del filelist
  
 	
    def makeTProfiles(self):
	self.pradmon = []
	for i in range(len(self.hradmon)):
	    self.pradmon.append(self.hradmon[i].ProfileX())
	
	#self.pradmon[6].Draw()
 	#raw_input("Press enter to continue")

    def writeOutput(self):
	
	rootFile = radmonLumiFilePattern.replace('__XXX__', str(self.fill))
	try:
	    fout = TFile(rootFile,'RECREATE')
	except IOError:
	    print "Cannot open file for output", rootFile
	    exit	 

	t = TTree('t', 'Combined Lumi and Radmon data')
	
	lsData = LsData()
	radmonData = RadmonData()

	t.Branch('IntBranch',  lsData, 'fill/I:fillStart/I:fillStable/I:fillEnd/I:durationStable/I:run/I:lsNo/I:lsDuration/I:tstamp/I')
	t.Branch('DoubleBranch', AddressOf(lsData, 'lumi'), 'lumi/D:bField/D:beamEnergy/D')
        t.Branch('BeamStatus', AddressOf(lsData, 'beamStatus'), 'beamStatus/C')
        t.Branch('LumiSource', AddressOf(lsData, 'lumiSource'), 'lumiSource/C')        
    	t.Branch('RadmonBranch',  radmonData, 'rates[16]/D:ratesErr[16]/D')
    	
    	href = self.pradmon[0]  # Reference histogram (to get bin center)

    	for i in range(len(self.xx) - 1):
            lsData.fill = self.lsDataList[i].fill
            lsData.fillStart = self.lsDataList[i].fillStart
            lsData.fillStable = self.lsDataList[i].fillStable
            lsData.fillEnd = self.lsDataList[i].fillEnd
            lsData.durationStable = self.lsDataList[i].durationStable
            lsData.run = self.lsDataList[i].run
            lsData.lsNo = self.lsDataList[i].lsNo
            lsData.lsDuration = self.lsDataList[i].lsDuration
            #lsData.tstamp = self.lsDataList[i].tstamp
            lsData.lumi = self.lsDataList[i].lumi
            lsData.bField = self.lsDataList[i].bField
            lsData.beamEnergy = self.lsDataList[i].beamEnergy
            lsData.beamStatus = self.lsDataList[i].beamStatus
            lsData.lumiSource = self.lsDataList[i].lumiSource

            # move tstamp to the middle of LS
            lsData.tstamp = int(href.GetXaxis().GetBinCenter(i))
            #lsData.tstamp = self.lsDataList[i].tstamp

	    for j in range(len(self.pradmon)):
		radmonData.rates[j] = self.pradmon[j].GetBinContent(i)
		radmonData.ratesErr[j] = self.pradmon[j].GetBinError(i)
		
	    t.Fill()
	print "Writing", rootFile
	fout.Write()
	fout.Close()
	del fout
	    
def main():
    
    for fill in fills:
        print "Processing fill#", fill
	dh = DataHandler(fill)
	dh.bookRadmonHistos()
	dh.fillRadmonHistos()
	dh.makeTProfiles()
	dh.writeOutput()
    
	del dh
#===========================================================
if __name__ == "__main__":
    main()

    
	    


