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
from fillReport import *

#fills = [3976]
#
fills = [ 3960, 3962, 3965, 3971, 3974,3976, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257, 4266, 4268, 4269, 4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467,4476, 4477, 4479, 4485, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4560, 4562, 4565, 4569]

lumiFilePattern = '/home/data/OnlineLumidata/lumi__XXX__.root'
RadmonDataDir = '/home/data/RadMonData/RawData'
radmonFilePattern = 'HFRadmonData*.root'
radmonLumiFilePattern = '/home/data/RadmonLumi/radmonLumi__XXX__.root'

fillReportName = '/home/grandr/cms/Bril/Analysis/ToOnlineLumi/FillReport_1446656923991.xls'

# temporary fix (rate higher than this value means that detector is being turned on)
rateMax = 100000. 

lRange = 2.

nYbins = 1000
hrs = 4  # hours before/after fromto

nRange = [1., 1., 1., 1., 1., 6., 6., 1., 6., 6., 1., 6., 6., 1., 6., 6.]
#iRbx = [5, 6, 8, 9, 11, 12, 14, 15]
#iRacks = [4, 7, 10, 13, 0, 1, 2, 3]    

#Output branches
gROOT.ProcessLine(\
"struct FillData{\
    Int_t fill;\
    Int_t fillStart;\
    Int_t fillStable;\
    Int_t fillEnd;\
    Int_t durationStable;\
    Int_t run;\
    Int_t lsNo;\
    Int_t tstamp;\
    Int_t msecs;\
    Int_t bunchSpacing;\
    Double_t bField;\
    Double_t beamEnergy;\
};")
from ROOT import FillData

gROOT.ProcessLine(\
"struct LumiData{\
    Double_t bestLumi;\
    Double_t bestLumiErr;\
    Double_t hfLumi;\
    Double_t hfLumiErr;\
    Double_t pltLumi;\
    Double_t pltLumiErr;\
    Double_t pltZeroLumi;\
    Double_t pltZeroLumiErr;\
    Double_t bcmfLumi;\
    Double_t bcmfLumiErr;\
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
	self.fillDataList = []
	self.yMax = -100000.
	self.yMin = 1000000.
	
    def setupRanges(self):
	"""
	read file with lumi data 
	setup low edges of histograms corresponding to the beginning of lumisections
	fill array of fill  data (fill, ls, run) corresponding to the given bin
	"""
	
	lsection = -1
	
	fillData = FillData()
	fillReport = FillReport(fillReportName)
	
	#Start/End/Stable
	tsStart =  fillReport.getFillCreationTime(self.fill)
	tsEnd = fillReport.getFillEndTime(self.fill)
	tsStable = fillReport.getFillStableTime(self.fill)
	duration = fillReport.getFillDuration(self.fill)
	bField = fillReport.getFillField(self.fill)
	beamEnergy = fillReport.getFillBeamEnergy(self.fill)
	
	#Time range to look for radmon files
	self.fromto[0] = tsStart
	self.fromto[1] = tsEnd
	
	f = TFile(lumiFilePattern.replace('__XXX__', str(self.fill)))
	tree = f.Get("t")

        
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue

	    #Y range for histograms
	    if tree.bestLumi > self.yMax:
		 self.yMax = tree.bestLumi
	    if tree.bestLumi < self.yMin:
		 self.yMin = tree.bestLumi
            
	    #Low edges for histos (start of LS)
	    if tree.lsNo != lsection:
		self.xx.append(tree.lsStart + tree.lsStartMs/1000000.)
		lsection = tree.lsNo
		
		# New lumisection - Add fill data
		fillData.fill = tree.fill
		fillData.fillStart = tsStart
		fillData.fillStable = tsStable
		fillData.fillEnd = tsEnd
		fillData.durationStable = duration
		fillData.bField = bField
		fillData.beamEnergy = beamEnergy
		fillData.bunchSpacing = tree.bunchSpacing
		fillData.run = tree.run
		fillData.lsNo = tree.lsNo

		self.fillDataList.append(fillData)
	
	print "Done setting up ranges for fill", self.fill, "\tNo of bins", len(self.xx) -1
	del tree
	del f
	del fillReport
	
	return  len(self.xx) -1

	
    def bookHistos(self):
	nbins = self.setupRanges()
	
	if (nbins > 0):
            #histograms for lumi
            self.hbest = TH2D('hbest', 'BestLumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
            self.hhf = TH2D('hhf', 'HF Lumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
            self.hplt = TH2D('hplt', 'PLT Lumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
            self.hpltZero = TH2D('hpltZero', 'PLTZERO Lumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
            self.hbcmf = TH2D('hbcmf', 'BCMF Lumi', len(self.xx) - 1, self.xx, nYbins, self.yMin/lRange, self.yMax*lRange)
	

            self.hradmon = []
            for i in range(len(nRange)):
                #print i
                self.hradmon.append(TH2D('hradmon' + str(i), 'Radmon Rate', len(self.xx) - 1, self.xx, nYbins, self.yMin, self.yMax*nRange[i]))
            print "Done booking histos for fill", self.fill
            return nbins
        else:
            print "No data found for fill", self.fill 
            return nbins
        
	
    def fillLumiHistos(self):
	
	f = TFile(lumiFilePattern.replace('__XXX__', str(self.fill)))
	tree = f.Get("t")
	
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue
	    
	    self.hbest.Fill(tree.tstamp+tree.msecs/1000000., tree.bestLumi)
	    self.hhf.Fill(tree.tstamp+tree.msecs/1000000., tree.hfLumi)
	    self.hplt.Fill(tree.tstamp+tree.msecs/1000000., tree.pltLumi)
	    self.hpltZero.Fill(tree.tstamp+tree.msecs/1000000., tree.pltZeroLumi)
	    self.hbcmf.Fill(tree.tstamp+tree.msecs/1000000., tree.bcmfLumi)

	#self.hbcmf.Draw()
	#raw_input("Press enter to continue")
	print "Done filling lumi histos"
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
        
        print "Done filling radmon histos"
	del chain
	del filelist
	#self.hradmon[10].Draw()
 	#raw_input("Press enter to continue")  
 	
    def makeTProfiles(self):
	self.pbest = self.hbest.ProfileX()
	self.pplt = self.hplt.ProfileX()
	self.ppltZero = self.hpltZero.ProfileX()
	self.phf = self.hhf.ProfileX()
	self.pbcmf = self.hbcmf.ProfileX()
	
	self.pradmon = []
	for i in range(len(self.hradmon)):
	    self.pradmon.append(self.hradmon[i].ProfileX())
	
        print "Done making  profiles"
        
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
	
	fillData = FillData()
	lumiData = LumiData()
	radmonData = RadmonData()
	
	t.Branch('fillBranch', fillData, 'fill/I:fillStart/I:fillStable/I:fillEnd/I:durationStable/I:run/I:lsNo/I:tstamp/I:msecs/I:bunchSpacing/I')
	t.Branch('fillBranchD', AddressOf(fillData, 'bField'), 'bField/D:beamEnergy/D')
	t.Branch('lumiBranch',  lumiData, 'bestLumi/D:bestLumiErr/D:hfLumi/D:hfLumiErr/D:pltLumi/D:pltLumiErr/D:pltZeroLumi/D:pltZeroLumiErr/D:bcmfLumi/D:bcmfLumiErr/D')
    	t.Branch('radmonBranch',  radmonData, 'rates[16]/D:ratesErr[16]/D')
    	
    	href = self.pbest  # Reference histogram
	#self.pbcmf.Draw()
	#raw_input("Press enter to continue")
	
        print "Starting filling tree, file ", radmonLumiFilePattern.replace('__XXX__', str(self.fill))
    	for i in range(len(self.xx) - 1):
            fillData.fill = self.fillDataList[i].fill
            fillData.fillStart =  self.fillDataList[i].fillStart
            fillData.fillStable =  self.fillDataList[i].fillStable
            fillData.fillEnd =  self.fillDataList[i].fillEnd
            fillData.durationStable =  self.fillDataList[i].durationStable
            fillData.run =  self.fillDataList[i].run
            fillData.lsNo =  self.fillDataList[i].lsNo
            fillData.bunchSpacing =  self.fillDataList[i].bunchSpacing
            fillData.bField =  self.fillDataList[i].bField
            fillData.beamEnergy =  self.fillDataList[i].beamEnergy
	    fillData.tstamp = int(href.GetXaxis().GetBinCenter(i))
	    fillData.msecs = int(href.GetXaxis().GetBinCenter(i) - fillData.tstamp)
	    
	    lumiData.bestLumi = self.pbest.GetBinContent(i)
	    lumiData.bestLumiErr = self.pbest.GetBinError(i)
	    lumiData.hfLumi = self.phf.GetBinContent(i)
	    lumiData.hfLumiErr = self.phf.GetBinError(i)
	    lumiData.pltLumi = self.pplt.GetBinContent(i)
	    lumiData.pltLumiErr = self.pplt.GetBinError(i)
	    lumiData.pltZeroLumi = self.ppltZero.GetBinContent(i)
	    lumiData.pltZeroLumiErr = self.ppltZero.GetBinError(i)
	    lumiData.bcmfLumi = self.pbcmf.GetBinContent(i)
	    lumiData.bcmfLumiErr = self.pbcmf.GetBinError(i)
	    
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
        print "Processing fill", fill, "........."
	dataHandler = DataHandler(fill)
	if dataHandler.bookHistos() <= 0:
            continue
	dataHandler.fillLumiHistos()
	dataHandler.fillRadmonHistos()
	dataHandler.makeTProfiles()
	dataHandler.writeOutput()
    
	del dataHandler
#===========================================================
if __name__ == "__main__":
    main()

    
	    


