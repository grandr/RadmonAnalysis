#!/usr/bin/env python
"""
Plot lumi vs time for a given fill (Bril lumi and normalized neutron rates)
Usage
root>  TPython::LoadMacro("plotFillLumi.py");
root>  PloFillLumy p;
root> p.draw(fillno, selectedLumi = bcmf)
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


    def setupRanges(self, tree):
	self.xmin = 0.
	self.xmax = 0.
	self.ymin = 1000000.
	self.ymax = -100000.
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue
	
	    self.xmin = tree.startFill - 300
	    self.xmax = tree.endFill + 300

	    if tree.primaryLumi > self.ymax:
		 self.ymax = tree.primaryLumi
	    if tree.primaryLumi < self.ymin:
		 self.ymin = tree.primaryLumi
		 
	self.nXbins = int((self.xmax - self.xmin)/self.secsPerBin)
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
	    
	    dv1 += l/dl2
	    dv2 += 1/dl2

	meanrate = dv1/dv2
	
	return meanrate
    
    def makeHistos(self, fill):
	f = ROOT.TFile(self.filePattern.replace('__XXX__', str(fill)), 'READ')
	tree = f.Get("t")
	self.setupRanges(tree)
	
	for key in self.histokeys:
	    self.histos[key] =  ROOT.TH2D("h" + key, "Fill "+ str(fill) + " " +key + " Lumi", self.nXbins, self.xmin, self.xmax, self.nYbins, self.ymin, self.ymax)
	    self.histos[key].SetDirectory(0)
 
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue
	    
	    self.histos['bcmf'].Fill(tree.tsUtc, tree.bcmf)
	    self.histos['plt'].Fill(tree.tsUtc, tree.plt)
	    self.histos['pltZero'].Fill(tree.tsUtc, tree.pltZero)
	    self.histos['primaryLumi'].Fill(tree.tsUtc, tree.primaryLumi)
	    self.histos['hf'].Fill(tree.tsUtc, tree.hf)
	    
	    meanrate = self.getRadmonMean(tree.rates)
	    self.histos['radmon'].Fill(tree.tsUtc, meanrate)

	del tree
	del f
	
    def drawHisto(self, key, opt = ""):
	ROOT.gStyle.SetOptStat(0000);
	self.histos[key].GetXaxis().SetTimeDisplay(1)
	self.histos[key].GetXaxis().SetTimeFormat("%H:%M")
	self.histos[key].GetXaxis().SetTitle("time")
	self.histos[key].Draw(opt)
