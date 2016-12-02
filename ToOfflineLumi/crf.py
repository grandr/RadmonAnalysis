#!/usr/bin/env python
"""
Studies with pPb data
(crf ratio etc)
"""

import os, sys
import ROOT
sys.path.append("../Utils/")
sys.path.append("../Config/")
from xconfig import *
from fillReport import *
import xutils
import math
import pprint

detInfo = {}
fillReport = FillReport("../Config/FillReportPPb_1479721242035.xls")
t = ROOT.TChain("t")

filePattern = "/scr1/RadMonLumi/2016/OfflineLumi/Radmon_normtag_BRIL/radmonLumi_NoNormtag__FILL__.root"

nTimeBins = 10000

deltaWarming = 1*60*60
fills = []

def init():
    """
    Some initialization
    """
    #Get detector info (index, detector No, calib factor)
    cfg = Config('../Config/detectors.ini')    
    dummy = cfg.get_option('Detectors')    
    for key in dummy.keys():
        detInfo[key] = dummy[key].split()
        
    lfills = sorted(fillReport.getFillCreationTime().keys())
    for fill in lfills:
        t.Add(filePattern.replace('__FILL__', str(fill)))
    
    for index, item in enumerate(lfills):
        fills.append(int(item))
    
    print "Fills used:", fills

def lumiVsFill():
    """
    Mean lumi vs fill and vs time
    """
    init()
    
    nbins = fills[-1] + 1 - fills[0]
    plfill = ROOT.TProfile("plfill", "Lumi vs fill", nbins, int(fills[0]), int(fills[-1]) + 1)
    
    tsStart = fillReport.getFillCreationTime(fills[0])
    tsEnd = fillReport.getFillEndTime(fills[-1]) + 1000
    pltime = ROOT.TProfile("pltime", "Lumi vs time", nTimeBins, tsStart, tsEnd)
    
    # Filling
    
    for i in range(0, t.GetEntries()) :
        nb = t.GetEntry(i)
        if nb < 0:
            continue
        #if t.beamStatus[:-1] != "STABLE BEAMS":
            #continue
        #if t.tstamp > t.fillEnd:
            #continue
        #if t.tstamp - t.fillStable < deltaWarming:
            #continue
        plfill.Fill(t.fill, t.lumi)
        pltime.Fill(t.tstamp, t.lumi)
        pltime.GetXaxis().SetTimeDisplay(1)
        pltime.GetXaxis().SetTimeFormat("%m-%d") 
        
    return plfill, pltime
    
    
def pfcr2pfxtRatio():
    """
    Ratio of flux near totem rack and PFXT
    """
    init()
    
    pfcr = "MNXT"
    pfxt = "PFXT"
    
    nbins = 100
    hr = ROOT.TH1D("hr", "PFCR/PFXT", nbins, 0., 20.)
    
    cfPfcr = float(detInfo[pfcr.lower()][2])
    indPfcr = int(detInfo[pfcr.lower()][0])
    cfPfxt = float(detInfo[pfxt.lower()][2])
    indPfxt = int(detInfo[pfxt.lower()][0])

    # Filling
    for i in range(0, t.GetEntries()) :
        nb = t.GetEntry(i)
        if nb < 0:
            continue
    
    
        if t.beamStatus[:-1] != "STABLE BEAMS":
            continue
        if t.tstamp > t.fillEnd:
            continue
        
        if t.tstamp - t.fillStable < deltaWarming:
            continue
        
        if t.lumi < 0.2:
            continue
            
        if t.rates[indPfxt] > 0.:
            ratio = cfPfcr*t.rates[indPfcr]/cfPfxt/t.rates[indPfxt]
            hr.Fill(ratio)
    
    #hr.Draw()
    return hr
    
    
    
    
    
