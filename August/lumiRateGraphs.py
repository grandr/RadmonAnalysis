#!/usr/bin/env python
"""
Make graphs with errors lumi vs neutron rate for all detectors
and fit them to the linear dependence

Usage (at root prompt)
TPython::LoadMacro("lumiRateGraphs.py");
LumiRateGraphs p;
p.makeGraphs();
p.drawGraph("pnit");
p.fitGraphs();
p.printCalibrationData();

p.setDeltaTs(2400)
p.fixP0(1);
p.setSelectedLumi("primaryLumi");
"""
import sys, os
from ROOT import *
from xutils import *

radmonLumiFilePattern = '/run/media/grandr/ADATA/RadMonData/RadMonLumi/radmonlumi*.root'
# Fills to use
fills = [3960, 3962, 3965, 3971, 3974, 3976, 3981, 3983, 3986, 3988, 3992, 3996, 4008]
#fills = [4201, 4220, 4224, 4225]

#Luminometer used for calibration is set in th data loop
#Name - index
detectors = {'pfxt':4,'mfxt':10, 'mnxt':13, 'pfit':6, 'pnit':9, 'pfib':5, 'pnib':8, 'mnit':15, 'mfit':12, 'mnib':14, 'mfib':11}

class LumiRateGraphs:
    def __init__(self):
	print "Making root chain from files",  radmonLumiFilePattern
	self.ch = ROOT.TChain("t")
	self.ch.Add(radmonLumiFilePattern)
	
	self.deltaTs = 2400
	self.xTitle = "primaryLumi lumi"
	self.selectedLumi = "primaryLumi"
	
	self.p0fixed = 0

    def setDeltaTs(self, delta):
	self.deltaTs = delta
	
    def setSelectedLumi(self, lumi):
	self.selectedLumi = lumi
	self.xTitle = str(lumi) + " lumi"
	
    def fixP0(self, flag):
	self.p0fixed = flag
	
    def makeGraphs(self):

	self.graphs = {}
	self.xmin = {}
	self.xmax = {}
	self.calibrationData = {}
	for key in detectors.keys():
	    self.graphs[key] = TGraphErrors()
	    self.graphs[key].SetName(key)
	    self.graphs[key].SetTitle(key.upper())
	    self.xmin[key] = 9999999999.
	    self.xmax[key] = -999999999.

	print "Using", self.selectedLumi, "for normalization"
	print "Fills used", fills
	print "deltaTs from the start of the fill=", self.deltaTs
	
	for i in range(0, t.GetEntries()) :
	    nb = t.GetEntry(i)
	    if nb < 0:
		continue
	    if t.fill not in fills:
		continue
	    if (t.tsUtc - t.startFill) <  self.deltaTs:
	    #if (t.tsUtc - t.startFill) >  self.deltaTs:
		continue
	    
	    if self.selectedLumi == "bcmf":
		yy = t.bcmf
		ey = t.bcmfErr
	    elif self.selectedLumi == "primaryLumi":
		yy = t.primaryLumi
		ey = t.primaryLumiErr		
	    else:
		print "Pick correct value for lumi"
		
	    for key in detectors.keys():
		n = self.graphs[key].GetN()
		j = detectors[key]
		self.graphs[key].SetPoint(n, t.rates[j], yy)
		self.graphs[key].SetPointError(n, t.ratesErr[j], ey)
		
		if t.rates[j] > self.xmax[key]:
		  self.xmax[key] =   t.rates[j]
		if t.rates[j] < self.xmin[key]:
		  self.xmin[key] =   t.rates[j]
	
    def fitGraphs(self):
	
	xmx = self.xmax[max(self.xmax, key=lambda i: self.xmax[i])]
	func = TF1('func', '[0]+[1]*x', 0., xmx)	
	func.SetParameters(-10, 0.6)

	if self.p0fixed == 1:
	    print "fitting graphs with p0 fixed"		
	for key in self.graphs.keys():
	    if self.p0fixed == 1:
		func.SetParameter(0, 0.)
		#func.SetParLimits(0, 0., 0.)
		func.FixParameter(0, 0.)
	    self.graphs[key].Fit('func', "CROBFQ", "", self.xmin[key]+1., self.xmax[key])
	    p0 = self.graphs[key].GetFunction('func').GetParameter(0)
	    dp0 = self.graphs[key].GetFunction('func').GetParError(0)
	    p1 = self.graphs[key].GetFunction('func').GetParameter(1)
	    dp1 = self.graphs[key].GetFunction('func').GetParError(1)
	    
	    self.calibrationData[key] = (str(detectors[key]), str(p1), str(dp1), str(p0), str(dp0))
	    
		
    def drawGraph(self, key):
	gStyle.SetOptFit(1111)
	self.graphs[key].GetYaxis().SetTitle(self.xTitle)
	self.graphs[key].Draw("AP")

    def printCalibrationData(self):
	for key in self.calibrationData.keys():
	    print str(key).upper() + ":\t", "\t".join(self.calibrationData[key])
	    