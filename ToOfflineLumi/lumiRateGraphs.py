#!/usr/bin/env python
"""
Make graphs with errors lumi vs neutron rate for all detectors
and fit them to the linear dependence

Usage (at root prompt)
TPython::LoadMacro("lumiRateGraphs.py");
LumiRateGraphs p;
p.makeGraphs();
p.drawGraph("pfit");
p.fitGraphs();
p.printCalibrationData();

p.setDeltaTs(2400)
p.fixP0(1);
"""
import sys, os
sys.path.append("../Utils/")
from ROOT import *
from xutils import *

#2016
#radmonLumiFilePattern = "/scr1/RadMonLumi/2016/OfflineLumi/Radmon_normtag_BRIL/*.root"
## Fills to use
##fills = [4888, 4889, 4890, 4892, 4895, 4896, 4905, 4906, 4910, 4915, 4919, 4924, 4925, 4926, 4930, 4935, 4937, 4942, 4945, 4947, 4953, 4954, 4956, 4958, 4960, 4961, 4964, 4965, 4976, 4979, 4980, 4984, 4985, 4988, 4990, 5005, 5013, 5017, 5020, 5021, 5024, 5026, 5027, 5028, 5029, 5030, 5038, 5043, 5045, 5048, 5052, 5056, 5059, 5060, 5068, 5069, 5071, 5072, 5073, 5076, 5078, 5080, 5083, 5085, 5091, 5093, 5095, 5096, 5097, 5101, 5102, 5105,  5106, 5107, 5108, 5109, 5110, 5111, 5112, 5116, 5117, 5149, 5151, 5154, 5161, 5162, 5163, 5169, 5170, 5173, 5179, 5181, 5183, 5187, 
#fills = [5194, 5196, 5197, 5198, 5199, 5205, 5206, 5209, 5210, 5211, 5213, 5219, 5222, 5223, 5229, 5246, 5247, 5251]

#2017
radmonLumiFilePattern = "/scr1/RadMonLumi/2017/OfflineLumi/Radmon_Root_normtag_BRIL/*.root"
# Fills to use
#fills = [4888, 4889, 4890, 4892, 4895, 4896, 4905, 4906, 4910, 4915, 4919, 4924, 4925, 4926, 4930, 4935, 4937, 4942, 4945, 4947, 4953, 4954, 4956, 4958, 4960, 4961, 4964, 4965, 4976, 4979, 4980, 4984, 4985, 4988, 4990, 5005, 5013, 5017, 5020, 5021, 5024, 5026, 5027, 5028, 5029, 5030, 5038, 5043, 5045, 5048, 5052, 5056, 5059, 5060, 5068, 5069, 5071, 5072, 5073, 5076, 5078, 5080, 5083, 5085, 5091, 5093, 5095, 5096, 5097, 5101, 5102, 5105,  5106, 5107, 5108, 5109, 5110, 5111, 5112, 5116, 5117, 5149, 5151, 5154, 5161, 5162, 5163, 5169, 5170, 5173, 5179, 5181, 5183, 5187, 
fills = [5698, 5699,5704, 5710, 5717, 5718, 5719, 5722, 5730, 5737, 5746, 5749, 5750, 5822, 5824, 5825, 5830, 5833, 5834, 5837]

#Luminometer used for calibration is set in the data loop
#Name - index
detectors = {'pfxt':4,'mfxt':10, 'mnxt':13, 'pfit':6, 'pnit':9, 'pfib':5, 'pnib':8, 'mnit':15, 'mfit':12, 'mnib':14, 'mfib':11}

class LumiRateGraphs:
    def __init__(self):
	print "Making root chain from files",  radmonLumiFilePattern
	self.ch = ROOT.TChain("t")
	self.ch.Add(radmonLumiFilePattern)
	
	self.deltaTs = 2400
	self.xTitle = "Lumi"
	self.selectedLumi = "lumi"
	
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
            # Magnet state
            if t.bField < 3.7:
                continue
		
	    for key in detectors.keys():
		j = detectors[key]
		
		#if t.lumiSource[:-1] != 'HFOC':
                    #continue
		if t.rates[j] > 10.:
                    n = self.graphs[key].GetN()
                    self.graphs[key].SetPoint(n, t.rates[j], t.lumi)
                    self.graphs[key].SetPointError(n, t.drates[j], 0.)
		
                    if t.rates[j] > self.xmax[key]:
                        self.xmax[key] =   t.rates[j]
                    if t.rates[j] < self.xmin[key]:
                        self.xmin[key] =   t.rates[j]
	
    def fitGraphs(self):
	
	xmx = self.xmax[max(self.xmax, key=lambda i: self.xmax[i])]
	#func = TF1('func', '[0]+[1]*x', 0., xmx)	
        func = TF1('func', '[0]+[1]*x', 10000., xmx)	
	func.SetParameters(-5., 0.5)

	if self.p0fixed == 1:
	    print "fitting graphs with p0 fixed"		
	for key in self.graphs.keys():
            print "Fitting ", key, "..."
	    if self.p0fixed == 1:
		func.SetParameter(0, 0.)
		#func.SetParLimits(0, 0., 0.)
		func.FixParameter(0, 0.)
            try:
                self.graphs[key].Fit('func', "CROBFQ", "", self.xmin[key]+100., self.xmax[key])
                self.graphs[key].GetFunction('func').SetLineWidth(3)
                p0 = self.graphs[key].GetFunction('func').GetParameter(0)
                dp0 = self.graphs[key].GetFunction('func').GetParError(0)
                p1 = self.graphs[key].GetFunction('func').GetParameter(1)
                dp1 = self.graphs[key].GetFunction('func').GetParError(1)
	    
	    except:
                p0, p1, dp0, dp1 =  0., 0., 0., 0.
	    
	    self.calibrationData[key] = (str(detectors[key]), str(p1), str(dp1), str(p0), str(dp0))
	    
		
    def drawGraph(self, key):
	gStyle.SetOptFit(1111)
	self.graphs[key].GetYaxis().SetTitle(self.xTitle)
	self.graphs[key].Draw("AP")

    def printCalibrationData(self):
	for key in self.calibrationData.keys():
	    print str(key).upper() + ":\t", "\t".join(self.calibrationData[key])
	    
