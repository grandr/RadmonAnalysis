#!/usr/bin/env python
"""
Make TProofiles  lumi vs neutron rate for all detectors
and fit them to the linear dependence

Usage (at root prompt)
TPython::LoadMacro("lumiRateProfiles.py");
LumiRateProfiles p;
p.makeProfiles();
p.drawProfile("pfit");
p.fitProfiles();
p.printCalibrationData();

p.setDeltaTs(2400)
p.fixP0(1);
"""
import os, sys
from ROOT import *
import ROOT
sys.path.append("../Utils/")
sys.path.append("../Config/")
from xconfig import *
from fillReport import *
import xutils
import math

#2016
radmonLumiFilePattern = "/scr1/RadMonLumi/2016/OfflineLumi/Radmon_normtag_BRIL/*.root"
fillReport = FillReport("../Config/FillReport.xls")
#Everything 2016
#fillsRange = [4850, 5460]
#fillsRange = [4850, 5077]
fillsRange = [5078, 5460]
#fillsRange = [5078, 5380]
#fillsRange = [5380, 5460]

radmonLumiFilePattern = "/home/data/RadMonLumi/2017/OfflineLumi/Radmon_Root_normtag_BRIL/*.root"
fillReport = FillReport("../Config/FillReport17.xls")
fillsRange = [5690, 5840]

#deltaTs = 2*60*60/3
deltaTs = 1*60*60

nbins = 1000
#Name - index
dets = {'pfxt','mfxt', 'mnxt', 'pfit', 'pnit', 'pfib', 'pnib', 'mnit', 'mfit', 'mnib', 'mfib'}

#Max value for x -axis
xmax = {
        'pfxt': 3000,
        'mfxt': 3000, 
        'mnxt': 3000, 
        'pfit': 40000, 
        'pnit': 40000, 
        'pfib': 40000, 
        'pnib': 40000, 
        'mnit': 40000, 
        'mfit': 60000, 
        'mnib': 40000, 
        'mfib': 60000}

#Get detector info (index, detector No, calib factor)
cfg = Config('../Config/detectors.ini')
dummy = cfg.get_option('Detectors')
detInfo = {}
for key in dummy.keys():
    detInfo[key] = dummy[key].split()
    
print "Making root chain from files",  radmonLumiFilePattern
t = ROOT.TChain("t")
t.Add(radmonLumiFilePattern)

class LumiRateProfiles:
    def __init__(self):
	self.yTitle = "Lumi"
	self.xTitle = "Rate"
	self.p0fixed = 0
	self.deltaTs = deltaTs
	self.calibrationData = {}


    def setDeltaTs(self, delta):
	self.deltaTs = delta
	
    def fixP0(self, flag):
	self.p0fixed = flag
	
    def makeProfiles(self):

	self.profs = {}
	
	for det in dets:
            self.profs[det] = ROOT.TProfile(det, det.upper() +": Lumi vs rate ", nbins, 0., xmax[det]) #, 's')
            self.profs[det].GetYaxis().SetTitle(self.yTitle)
            self.profs[det].GetXaxis().SetTitle(self.xTitle)
            ROOT.SetOwnership(self.profs[det], False)

	#print "Fills used", fills
	print "deltaTs from the start of the fill=", self.deltaTs
	print "Fills range", fillsRange
	
	for i in range(0, t.GetEntries()) :
	    nb = t.GetEntry(i)
	    if nb < 0:
		continue
            
	    #if t.fill not in fills:  # TODO Add fills excluded
		#continue
		
            if t.fill <= fillsRange[0] or t.fill >= fillsRange[1]:
                continue
            
            #===================Cuts============================
            if "STABLE BEAMS" not in str(t.beamStatus):
                continue            
            #Warmup
	    if (t.tstamp - t.fillStable) <  self.deltaTs:
		continue
            
            #After the end of fill
            if (t.tstamp - t.fillEnd) > 0:
                continue
            
            # Magnet state
            if t.bField < 3.6:
                continue
		
	    for det in dets:
		index = int(detInfo[det.lower()][0])

                    
		if t.rates[index] > 0. and t.lumi > 0.:
                    self.profs[det].Fill( t.rates[index], t.lumi)

        return self.profs
	
    def fitProfiles(self):
	
	func = TF1('func', '[0]+[1]*x', 0., 60000.)	
	func.SetParameters(-5., 0.5)

	if self.p0fixed == 1:
	    print "fitting profiles with p0 fixed"		
	for key in self.profs.keys():
            print "Fitting ", key.upper(), "..."
	    if self.p0fixed == 1:
		func.SetParameter(0, 0.)
		func.FixParameter(0, 0.)
            try:
                self.profs[key].Fit('func', "CROBFQ", "") #, self.xmin[key]+100., self.xmax[key])
                self.profs[key].GetFunction('func').SetLineWidth(3)
                p0 = self.profs[key].GetFunction('func').GetParameter(0)
                dp0 = self.profs[key].GetFunction('func').GetParError(0)
                p1 = self.profs[key].GetFunction('func').GetParameter(1)
                dp1 = self.profs[key].GetFunction('func').GetParError(1)
	    
	    except:
                p0, p1, dp0, dp1 =  0., 0., 0., 0.
	    
	    self.calibrationData[key] = str(p1), str(dp1), str(p0), str(dp0)
	    
		
    def drawProfile(self, key):
	ROOT.gStyle.SetOptFit(1111)
	self.profs[key].Draw()

    def printCalibrationData(self):
	for key in self.calibrationData.keys():
	    print str(key).upper() + ":\t", "\t".join(self.calibrationData[key])
	    
