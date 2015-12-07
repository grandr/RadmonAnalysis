#!/usr/bin/env python
"""
Plot lumi vs time for a given fill (Bril lumi and normalized neutron rates)
Usage example (at root prompt)
TPython::LoadMacro("plotFillLumi.py");
PlotFillLumy f;
f.makeHistos(4402);
f.drawHisto("bestLumi");
f.drawHisto("radmon", "same");
"""

import sys, os
#from ROOT import *
import ROOT
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
	self.pngFilePattern = cfg.get_option('Env', 'pngFilePattern')
	
	self.dets = cfg.get_option('Env', 'dets').lower().split()
	self.nYbins = int(cfg.get_option('Env', 'nYbins'))
	self.nXbins = int(cfg.get_option('Env', 'nXbins'))
	dd = cfg.get_option('Detectors')
	self.secsPerBin = int(cfg.get_option('Env', 'secsPerBin'))
	del cfg


	self.detectorData = {}
	for key in dd.keys():
	    self.detectorData[key] = dd[key].split()

	self.histokeys = ['bestLumi', 'bcmfLumi', 'hfLumi', 'pltLumi', 'pltZeroLumi', 'radmon']
	self.histos = {}

    def setupRanges(self, fill):
	self.fromto = [99999999999, -1]
	f = ROOT.TFile(self.lumiFilePattern.replace('__XXX__', str(fill)))
	
	self.fill = fill
	
	tree = f.Get("t")
	
	self.ymax = -9999999.
	self.ymin = 99999999.
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue

	    #Y range for histograms
	    #if tree.bestLumi > self.ymax:
		 #self.ymax = tree.bestLumi
	    #if tree.bestLumi < self.ymin:
		 #self.ymin = tree.bestLumi
		 
	    #Y range for histograms
	    if tree.hfLumi > self.ymax:
		 self.ymax = tree.hfLumi
	    if tree.hfLumi < self.ymin:
		 self.ymin = tree.hfLumi		 
		
	    #Setting start/end of the fill
	    if  tree.tstamp < self.fromto[0]:
		self.fromto[0] = tree.tstamp
	    if tree.tstamp > self.fromto[1]:
		self.fromto[1] = tree.tstamp
	    
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
	    #self.histos[key] =  ROOT.TH2D("h" + key, "Fill "+ str(fill) + " " +key, self.nXbins, self.fromto[0]-300, self.fromto[1]+300, self.nYbins, 0., -1.)
	    self.histos[key].SetDirectory(0)
 
	f = ROOT.TFile(self.lumiFilePattern.replace('__XXX__', str(fill)), 'READ')
	tree = f.Get("t")
	for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue
	    
	    self.histos['bcmfLumi'].Fill(tree.tstamp+tree.msecs/1000000., tree.bcmfLumi)
	    self.histos['pltLumi'].Fill(tree.tstamp+tree.msecs/1000000., tree.pltLumi)
	    self.histos['pltZeroLumi'].Fill(tree.tstamp+tree.msecs/1000000., tree.pltZeroLumi)
	    self.histos['bestLumi'].Fill(tree.tstamp+tree.msecs/1000000., tree.bestLumi)
	    self.histos['hfLumi'].Fill(tree.tstamp+tree.msecs/1000000., tree.hfLumi)

	del tree
	del f
	
	self.fromto[0] -=  14400
	self.fromto[1] +=  14400
	filelist =  get_filelist(self.RadmonDataDir, self.radmonFilePattern, self.fromto)
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
	
    def drawAll2png(self):
        
        self.c = TCanvas('c', 'Lumi', 800, 600)
        ROOT.gStyle.SetOptStat(0000);
        ROOT.gStyle.SetOptTitle(0)
        self.histos["hfLumi"].GetXaxis().SetTimeDisplay(1)
        self.histos["hfLumi"].GetXaxis().SetTimeFormat("%H:%M")
        self.histos["hfLumi"].GetXaxis().SetTitle("Time")
        
        self.histos["hfLumi"].SetLineColor(4)
        self.histos["hfLumi"].SetMarkerColor(4)
        self.histos["bestLumi"].SetLineColor(2)
        self.histos["bestLumi"].SetMarkerColor(2)
        self.histos["pltZeroLumi"].SetLineColor(3)
        self.histos["pltZeroLumi"].SetMarkerColor(3)  
        self.histos["bcmfLumi"].SetLineColor(30)
        self.histos["bcmfLumi"].SetMarkerColor(30)  
        self.histos["radmon"].SetLineColor(1)
        self.histos["radmon"].SetMarkerColor(1)          
        
        self.histos["hfLumi"].Draw()
        self.histos["pltZeroLumi"].Draw("same")
        self.histos["bestLumi"].Draw("same")
        self.histos["bcmfLumi"].Draw("same")
        self.histos["radmon"].Draw("same")
        
        self.lg = TLegend(0.6, .7, .9, .9)
        self.lg.AddEntry(self.histos["bestLumi"], "Fill " + str(self.fill) + " BestLumi", "l")
        self.lg.AddEntry(self.histos["hfLumi"], "Fill " + str(self.fill) + " HF", "l")
        self.lg.AddEntry(self.histos["pltZeroLumi"], "Fill " + str(self.fill) + " PltZero", "l")
        self.lg.AddEntry(self.histos["bcmfLumi"], "Fill " + str(self.fill) + " BCM1F", "l")
        self.lg.AddEntry(self.histos["radmon"], "Fill " + str(self.fill) + " HF Radmon", "l")
        self.lg.Draw()

        imgdump = TImageDump(self.pngFilePattern.replace('__XXX__', str(self.fill)))
        self.c.Paint()
        imgdump.Close()
