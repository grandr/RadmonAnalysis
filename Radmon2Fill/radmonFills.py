#!/usr/bin/env python
"""
Plot radmon rates for particular fill
Try various operations with running sums
Usage (at root prompt)
TPython::LoadMacro("radmonFills.py");
RadmonFills f;
f.initFill(4947);
f.drawRate(12);
"""

import sys, os
#from ROOT import *
import ROOT
import math
sys.path.append("../Utils/")
from xutils import *
from xconfig import *

from fillReport import *
import numpy as np

from dateutil import tz
os.environ['TZ'] = 'Europe/Zurich'


totalMinutes = 30

class RadmonFills:
    
    def __init__(self):
        pass

    
    def initFill(self, fill):
        
        self.fill = fill
        #radmonFillPattern = '/home/data/RadMonData/RadmonFills/radmon__XXX__.root'
        radmonFillPattern = '/scr1/RadmonFills/2016/radmon__XXX__.root'
        fillReportName = '../Config/FillReport.xls'
        
        self.secsPerBin = 10
        self.minutesMargin = 10

        
        fillReport = FillReport(fillReportName)
        self.tsStable = fillReport.getFillStableTime(fill)
        self.tsEnd = fillReport.getFillEndTime(fill)
        
        del fillReport
  
        self.binsY = 200
        self.binsX = int( (self.tsEnd + 2*self.minutesMargin*60 - self. tsStable)/self.secsPerBin ) 
        self.xmin = float(self. tsStable - self.minutesMargin*60)
        self.xmax = float(self.tsEnd +  self.minutesMargin*60)
        
        self.f = ROOT.TFile(radmonFillPattern.replace('__XXX__', str(fill)))
        
        
    #def setSecsPerBin(self, secs):
        #self.secsPerBin = secs
        
    #def setminutsMargin(self, minutes):
        #self.minutesMargin = minutes
        
    def drawRate(self, indx):
        
        #Book 2D histo
        self.hrate = ROOT.TH2D("hrate" + str(indx), "Rate for index " + str(indx) + ", fill " + str(self.fill), self.binsX, self.xmin, self.xmax, self.binsY, 0., 0.)
        #self.hrate = ROOT.TH2D("hrate" + str(indx), "Rate for index " + str(indx) + ", fill " + str(self.fill), self.binsX, 0., 0., self.binsY, 0., 0.)
        self.hrate.GetXaxis().SetTimeDisplay(1)
        self.hrate.GetXaxis().SetTimeFormat("%H:%M")
        self.hrate.SetBit(ROOT.TH1.kCanRebin)
        

        tree = self.f.Get("t")
        for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue
            self.hrate.Fill(tree.tstamp, tree.rates[5])
        
        #xaxis = self.hrate.GetXaxis()
        #nlabels = 20
        #j = 1
        #for i in range(1, self.binsX):
            #if i == j*self.binsX/nlabels:
                #t = xaxis.GetBinCenter(i)
                #xaxis.SetBinLabel(i, ts2datime(t, 0, "%H:%M"))
                #j += 1
        #xaxis.LabelsOption("h")
        #xaxis.SetTickSize(0.01)
        self.hrate.Draw()
    
    def drawRunningSum (self, indx, minutes):
        
        #Book 2D histo
          
        self.hrsum = ROOT.TH2D("hrsum" + str(indx), "Running sum for index " + str(indx) + ", minutes " + str(minutes) + " , fill " + str(self.fill), self.binsX, self.xmin, self.xmax, self.binsY, 0., 0.)
        self.hrsum.GetXaxis().SetTimeDisplay(1)
        self.hrsum.GetXaxis().SetTimeFormat("%H:%M")
        self.hrsum.SetBit(ROOT.TH1.kCanRebin)
        
        tree = self.f.Get("t")
        for i in range(0, tree.GetEntries()) :
	    nb = tree.GetEntry(i)
	    if nb < 0:
		continue
            nump1d = np.array(tree.rsums)
            nump2d = np.reshape(nump1d, (-1,1800))
            start = 1800 - minutes*60
            buff = nump2d[5][start:1800]
            self.hrsum.Fill(tree.tstamp, np.sum(buff))
        self.hrsum.Draw()
    
           
    
        

