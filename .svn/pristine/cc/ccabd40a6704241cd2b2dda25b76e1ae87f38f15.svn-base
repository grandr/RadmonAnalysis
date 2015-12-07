#!/usr/bin/env python
"""
Plot lumi vs time for a given fill (Bril lumi and normalized neutron rates)
Usage example (at root prompt)
TPython::LoadMacro("plotFillLumi.py");
PlotFillLumy f;
f.makeHistos(3996);
f.drawHisto("primaryLumi");
f.drawHisto("radmon", "same");
"""

import sys, os
from ROOT import *
import math
from xutils import *
from xconfig import *


class PlotFillLumy:
    def __init__(self):
	cfg = Config('lumiCalibration.ini')
	self.filePattern = cfg.get_option('Env', 'filePattern')
	self.lumiFilePattern = cfg.get_option('Env', 'lumiFilePattern')
	self.RadmonDataDir = cfg.get_option('Env', 'RadmonDataDir')	
	self.radmonFilePattern = cfg.get_option('Env', 'radmonFilePattern')
	
	self.dets = cfg.get_option('Env', 'dets').lower().split()
	self.nYbins = int(cfg.get_option('Env', 'nYbins'))
	self.nXbins = int(cfg.get_option('Env', 'nXbins'))
	dd = cfg.get_option('Detectors')
	self.secsPerBin = int(cfg.get_option('Env', 'secsPerBin'))
	del cfg


	self.detectorData = {}
	for key in dd.keys():
	    self.detectorData[key] = dd[key].split()

	self.histokeys = ['primaryLumi', 'bcmf', 'hf', 'plt', 'pltZero', 'radmon']
	self.histos = {}

    def setupRanges(self, fill):
	self.fromto = [99999999999, -1]
	f = ROOT.TFile(self.lumiFilePattern.replace('__XXX__', str(fill)))
	tree = f.Get("t")
	
	self.ymax = -9999999.
	self.ymin = 99999999.
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue

	    #Y range for histograms
	    if tree.primaryLumi > self.ymax:
		 self.ymax = tree.primaryLumi
	    if tree.primaryLumi < self.ymin:
		 self.ymin = tree.primaryLumi
		
	    #Setting start/end of the fill
	    if  tree.secsUtc < self.fromto[0]:
		self.fromto[0] = tree.secsUtc
	    if tree.secsUtc > self.fromto[1]:
		self.fromto[1] = tree.secsUtc
	    
	del tree
	del f
	self.nXbins = int((self.fromto[1] - self.fromto[0])/self.secsPerBin)
	self.ymin /=  1.3
	self.ymax *=  1.3

    def getRadmonMean(self, rates):
	dv1 = 0
	dv2 = 0
	for dt in self.dets:
	    i = int(self.detectorData[dt][0])
	    p1 = float(self.detectorData[dt][1])
	    dp1 = float(self.detectorData[dt][2])
	    p0 = float(self.detectorData[dt][3])
	    dp0 = float(self.detectorData[dt][4])
	    
	    l = p1*rates[i] + p0
	    dl2 = rates[i]*rates[i]*dp1*dp1 +dp0*dp0
	    
	    if dl2 != 0:
		dv1 += l/dl2
		dv2 += 1/dl2

	if dv2 == 0.:
	    meanrate = 0.
	else:
	    meanrate = dv1/dv2
	
	
	return meanrate
    
    def makeHistos(self, fill):

	self.setupRanges(fill)
	
	for key in self.histokeys:
	    self.histos[key] =  ROOT.TH2D("h" + key, "Fill "+ str(fill) + " " +key, self.nXbins, self.fromto[0]-300, self.fromto[1]+300, self.nYbins, self.ymin, self.ymax)
	    self.histos[key].SetDirectory(0)
 
	f = ROOT.TFile(self.lumiFilePattern.replace('__XXX__', str(fill)), 'READ')
	tree = f.Get("t")
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue
	    
	    self.histos['bcmf'].Fill(tree.secsUtc+tree.msecs/1000., tree.bcmf)
	    self.histos['plt'].Fill(tree.secsUtc+tree.msecs/1000., tree.plt)
	    self.histos['pltZero'].Fill(tree.secsUtc+tree.msecs/1000., tree.pltZero)
	    self.histos['primaryLumi'].Fill(tree.secsUtc+tree.msecs/1000., tree.primaryLumi)
	    self.histos['hf'].Fill(tree.secsUtc+tree.msecs/1000., tree.hf)

	del tree
	del f
	
	self.fromto[0] -=  14400
	self.fromto[1] +=  14400
	filelist =  get_filelist(self.RadmonDataDir, self.radmonFilePattern, self.fromto)
	print filelist[0],  filelist[1]
	chain = TChain("Rate")
        for file in filelist:
            chain.Add(file)
        
        for i in range(chain.GetEntries()):
            chain.GetEntry(i)
		    
	    meanrate = self.getRadmonMean(chain.rates)
	    self.histos['radmon'].Fill(chain.tstamp, meanrate)

	del chain
	del filelist
	
    def drawHisto(self, key, opt = ""):
	ROOT.gStyle.SetOptStat(0000);
	self.histos[key].GetXaxis().SetTimeDisplay(1)
	self.histos[key].GetXaxis().SetTimeFormat("%H:%M")
	self.histos[key].GetXaxis().SetTitle("time")
	self.histos[key].Draw(opt)
