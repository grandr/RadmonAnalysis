#!/usr/bin/env python
"""
Make graphs with errors lumi vs neutron rate for all detectors
and fit them to the linear dependence

Usage (at root prompt)
TPython::LoadMacro("lumiRateGraphs.py");
LumiRateGraphs p;
p.makeGraphs();
p.drawGraph("pfib");
p.fitGraphs();
p.printCalibrationData();

p.setDeltaTs(2400)
p.fixP0(1);
p.setSelectedLumi("bestLumi");
"""
import sys, os
from ROOT import *
from xutils import *

radmonLumiFilePattern = '/home/data/RadmonLumi/radmonLumi*.root'
# Fills to use
fills = [ 3960, 3962, 3965, 3971, 3974,3976, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257, 4266, 4268, 4269, 4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467,4476, 4477, 4479, 4485, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4562, 4565] 
         #4560, 4569]


#Luminometer used for calibration is set in the data loop
#Name - index
detectors = {'pfxt':4,'mfxt':10, 'mnxt':13, 'pfit':6, 'pnit':9, 'pfib':5, 'pnib':8, 'mnit':15, 'mfit':12, 'mnib':14, 'mfib':11}

class LumiRateGraphs:
    def __init__(self):
	print "Making root chain from files",  radmonLumiFilePattern
	self.ch = ROOT.TChain("t")
	self.ch.Add(radmonLumiFilePattern)
	
	self.deltaTs = 2400
	self.xTitle = "bestLumi"
	self.selectedLumi = "bestLumi"
	
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
            
            #===================Cuts============================
            #Warmup
	    if (t.tstamp - t.fillStable) <  self.deltaTs:
		continue
            #Filling scheme
            if t.bunchSpacing != 25:
                continue
            # Magnet state
            if t.bField < 3.7:
                continue
	    
	    if self.selectedLumi == "bestLumi":
		yy = t.bestLumi
		ey = t.bestLumiErr
		
	    #else:
		#print "Pick correct value for lumi"
		
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
	func.SetParameters(-5., 0.5)

	if self.p0fixed == 1:
	    print "fitting graphs with p0 fixed"		
	for key in self.graphs.keys():
	    if self.p0fixed == 1:
		func.SetParameter(0, 0.)
		#func.SetParLimits(0, 0., 0.)
		func.FixParameter(0, 0.)
	    self.graphs[key].Fit('func', "CROBFQ", "", self.xmin[key]+100., self.xmax[key])
	    self.graphs[key].GetFunction('func').SetLineWidth(3)
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
	    
