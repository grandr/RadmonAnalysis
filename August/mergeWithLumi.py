#!/usr/bin/env python

"""
-*- coding: UTF-8 -*-
Merge RadmonData & LumiData based on run/ls
"""
import sys, os
from array import array
from ROOT import *
import math
from array import array
from xutils import *

#fills = [3960, 3962, 3965, 3971, 3974, 3976, 3981, 3983, 3986, 3988, 3992, 3996]
fills = [4008, 4201, 4220, 4224, 4225]

lumiFilePattern = '/run/media/grandr/ADATA/RadMonData/BrilData/fillRoot/fill__XXX__.root'
RadmonDataDir = '/run/media/grandr/ADATA/RadMonData/RawData'
radmonFilePattern = 'HFRadmonData*.root'
radmonLumiFilePattern = '/run/media/grandr/ADATA/RadMonData/RadMonLumi/radmonlumi__XXX__.root'

# temporary fix (rate higher than this value means that detector is being turned on)
rateMax = 50000. 

lRange = 2.

nYbins = 10000
hrs = 4  # hours before/after fromto

nRange = [1., 1., 1., 1., 1., 6., 6., 1., 6., 6., 1., 6., 6., 1., 6., 6.]
#iRbx = [5, 6, 8, 9, 11, 12, 14, 15]
#iRacks = [4, 7, 10, 13, 0, 1, 2, 3]    

#Output branches
#All timestamps are in UTC!
gROOT.ProcessLine(\
"struct TimingData{\
Double_t fill;\
Double_t startFill;\
Double_t endFill;\
Double_t run;\
Double_t lsno;\
Double_t tsUtc;\
};")
from ROOT import TimingData

gROOT.ProcessLine(\
"struct LumiData{\
Double_t primaryLumi;\
Double_t primaryLumiErr;\
Double_t hf;\
Double_t hfErr;\
Double_t plt;\
Double_t pltErr;\
Double_t pltZero;\
Double_t pltZeroErr;\
Double_t bcmf;\
Double_t bcmfErr;\
};")
from ROOT import LumiData  

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
	self.td = []
	self.yMax = -100000.
	self.yMin = 1000000.
	
    def setupRanges(self):
	"""
	read file with lumi data 
	setup low edges of histograms corresponding to the beginning of lumisections
	fill array of timing  structures (fill, ls, run) corresponding to the given bin
	"""
	startOfFill = -1
	lsection = -1
	
	timingData = TimingData()
	
	f = TFile(lumiFilePattern.replace('__XXX__', str(self.fill)))
	tree = f.Get("t")
	
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue

	    #Y range for histograms
	    if tree.primaryLumi > self.yMax:
		 self.yMax = tree.primaryLumi
	    if tree.primaryLumi < self.yMin:
		 self.yMin = tree.primaryLumi
		
	    #Setting start/end of the fill
	    if  tree.secsUtc < self.fromto[0]:
		self.fromto[0] = tree.secsUtc
	    if tree.secsUtc > self.fromto[1]:
		self.fromto[1] = tree.secsUtc

	    #Low edges for histos (start of LS)
	    if tree.lsno != lsection:
		self.xx.append(tree.secsUtc + tree.msecs/1000.)
		lsection = tree.lsno
		# New lumisection - fill timing data
		timingData.fill = tree.fill
		timingData.run = tree.run
		timingData.lsno = tree.lsno
		timingData.endFill = tree.secsUtc  + tree.msecs/1000.
		if startOfFill < 0:
		    timingData.startFill = tree.secsUtc  + tree.msecs/1000.
		    startOfFill = timingData.startFill
	    
		self.td.append(timingData)
	    
	del tree
	del f

	
    def bookHistos(self):
	self.setupRanges()
	
	#histograms for lumi
	self.hprlumi = TH2D('hprlumi', 'PrimaryLumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
	self.hhf = TH2D('hhf', 'HF Lumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
	self.hplt = TH2D('hplt', 'PLT Lumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
	self.hpltZero = TH2D('pltZero', 'PLTZERO Lumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
	self.hbcmf = TH2D('hbcmf', 'BCMF Lumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
	
	self.hradmon = []
	for i in range(len(nRange)):
	    self.hradmon.append(TH2D('hradmon' + str(i), 'Radmon Rate', len(self.xx) - 1, self.xx, nYbins, self.yMin, self.yMax*nRange[i]))
	
	
    def fillLumiHistos(self):
	
	f = TFile(lumiFilePattern.replace('__XXX__', str(self.fill)))
	tree = f.Get("t")
	
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue
	    
	    self.hprlumi.Fill(tree.secsUtc+tree.msecs/1000., tree.primaryLumi)
	    self.hhf.Fill(tree.secsUtc+tree.msecs/1000., tree.hf)
	    self.hplt.Fill(tree.secsUtc+tree.msecs/1000., tree.plt)
	    self.hpltZero.Fill(tree.secsUtc+tree.msecs/1000., tree.pltZero)
	    self.hbcmf.Fill(tree.secsUtc+tree.msecs/1000., tree.bcmf)

	#self.hbcmf.Draw()
	#raw_input("Press enter to continue")
	
	del tree
	del f
	
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
		    self.hradmon[j].Fill(chain.tstamp, chain.rates[j])

	del chain
	del filelist
	#self.hradmon[10].Draw()
 	#raw_input("Press enter to continue")  
 	
    def makeTProfiles(self):
	self.pprlumi = self.hprlumi.ProfileX()
	self.pplt = self.hplt.ProfileX()
	self.ppltZero = self.hpltZero.ProfileX()
	self.phf = self.hhf.ProfileX()
	self.pbcmf = self.hbcmf.ProfileX()
	
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
	
	timingData = TimingData()
	lumiData = LumiData()
	radmonData = RadmonData()
	t.Branch('timingBranch',  timingData, 'fill/D:startFill/D:endFill/D:run/D:lsno/D:tsUtc/D')
	t.Branch('lumiBranch',  lumiData, 'primaryLumi/D:primaryLumiErr/D:hf/D:hfErr/D:plt/D:pltErr/D:pltZero/D:pltZeroErr/D:bcmf/D:bcmfErr/D')
    	t.Branch('radmonBranch',  radmonData, 'rates[16]/D:ratesErr[16]/D')
    	
    	href = self.pprlumi  # Reference histogram
	#self.pbcmf.Draw()
	#raw_input("Press enter to continue")
    	for i in range(len(self.xx) - 1):
	    timingData.fill = self.td[i].fill
	    timingData.startFill = self.td[i].startFill
	    timingData.endFill = self.td[i].endFill
	    timingData.run = self.td[i].run
	    timingData.lsno = self.td[i].lsno
	    timingData.tsUtc = href.GetXaxis().GetBinCenter(i)
	    
	    lumiData.primaryLumi = self.pprlumi.GetBinContent(i)
	    lumiData.primaryLumiErr = self.pprlumi.GetBinError(i)
	    lumiData.hf = self.phf.GetBinContent(i)
	    lumiData.hfErr = self.phf.GetBinError(i)
	    lumiData.plt = self.pplt.GetBinContent(i)
	    lumiData.pltErr = self.pplt.GetBinError(i)
	    lumiData.pltZero = self.ppltZero.GetBinContent(i)
	    lumiData.pltZeroErr = self.ppltZero.GetBinError(i)
	    lumiData.bcmf = self.pbcmf.GetBinContent(i)
	    lumiData.bcmfErr = self.pbcmf.GetBinError(i)
	    
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
	dh = DataHandler(fill)
	dh.bookHistos()
	dh.fillLumiHistos()
	dh.fillRadmonHistos()
	dh.makeTProfiles()
	dh.writeOutput()
    
	del dh
#===========================================================
if __name__ == "__main__":
    main()

    
	    


