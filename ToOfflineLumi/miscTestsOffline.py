#!/usr/bin/env python
"""
Various tests for normalization to offline lumi
"""

import os, sys
import ROOT
sys.path.append("../Utils/")
sys.path.append("../Config/")
from xconfig import *
from fillReport import *
import xutils
import math
#Get detector info (index, detector No, calib factor)
cfg = Config('../Config/detectors.ini')
dummy = cfg.get_option('Detectors')
detInfo = {}
for key in dummy.keys():
    detInfo[key] = dummy[key].split()

fillReport = FillReport("../Config/FillReport.xls")

t = ROOT.TChain("t")
t.Add("/scr1/RadMonLumi/2016/OfflineLumi/Radmon_normtag_BRIL/*.root");

#Cuts
deltaWarming = 1*60*60

def meanRackFluenceVsLumi():
    
    """
    mean neutron fluence near Racks vs offline lumi
    """
    
    fillsRange = [4850, 5400]
    dets = ["PFXT"]#, "MNXT", "MFXT"]

    nbins = 1000

    
    hflxlumi = ROOT.TH2D("hflxlumi", "mean flux vs lumi", nbins, 0., 16000., nbins, 0., 10000.)
    ROOT.SetOwnership(hflxlumi, False)
    
    tflxlumi = ROOT.TProfile("tflxlumi", "mean flux vs lumi", nbins, 0., 16000.)
    ROOT.SetOwnership(tflxlumi, False)
    tflxlumiplt = ROOT.TProfile("tflxlumiplt", "mean flux vs PLT lumi", nbins, 0., 16000.)
    ROOT.SetOwnership(tflxlumiplt, False)    
    tflxlumihf = ROOT.TProfile("tflxlumihf", "mean flux vs HF  lumi", nbins, 0., 16000.)
    ROOT.SetOwnership(tflxlumihf, False)  


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
    
#     if i > 10000:    break

        meanflux = 0
        ndet = 0
        for det in dets:
            index = int(detInfo[det.lower()][0])
            cf = float(detInfo[det.lower()][2])
            if t.rates[index] > 0:
                meanflux += t.rates[index] * cf
                ndet += 1
        if ndet > 0:
            meanflux /= ndet
    
        if t.lumi > 0 and meanflux>0:
            hflxlumi.Fill(t.lumi, meanflux)
            tflxlumi.Fill(t.lumi, meanflux)
            if t.lumiSource[:-1] == "HFOC":
                tflxlumihf.Fill(t.lumi, meanflux)
            if t.lumiSource[:-1] == "PLTZERO":
                tflxlumiplt.Fill(t.lumi, meanflux)
   
    prflxlumi = hflxlumi.ProfileX("prflxlumi", 1, -1, "s")
    ROOT.SetOwnership(prflxlumi, False)

    #return hrfill, prfill, hflxlumi, hflxplt, hflxhf
    return hflxlumi, prflxlumi, tflxlumi, tflxlumihf,  tflxlumiplt
    
    

def meanFluenceVsLumi():
    """
    mean neutron fluence vs offline lumi
    """
    
    fillsRange = [4850, 5400]
    dets = ["PFIT", "PFIB", "PNIT", "PNIB", "MNIB", "MNIT"]
    #dets = ["PFIT", "PFIB", "PNIT", "PNIB"]

    nbins = 1000

    histos = {}
    profx = {}
    
    hrfill = ROOT.TProfile("hrfill", "ratio mean flux over lumi vs fill No", 
                  (fillsRange[1] - fillsRange[0]), fillsRange[0], fillsRange[1], 's')
    histos['hrfill'] = hrfill
    ROOT.SetOwnership(hrfill, False)
    
    hrfillplt = ROOT.TProfile("hrfillplt", "ratio mean flux over PLTZERO lumi vs fill No", 
                  (fillsRange[1] - fillsRange[0]), fillsRange[0], fillsRange[1], 's')
    ROOT.SetOwnership(hrfillplt, False)
    histos['hrfillplt'] = hrfillplt
    
    hrfillhf = ROOT.TProfile("hrfillhf", "ratio mean flux over HFOC lumi vs fill No", 
                  (fillsRange[1] - fillsRange[0]), fillsRange[0], fillsRange[1], 's')
    ROOT.SetOwnership(hrfillhf, False)
    histos['hrfillhf'] = hrfillhf
    
    hflxlumi = ROOT.TProfile("hflxlumi", "mean flux vs lumi", nbins, 0., 16000.)
    ROOT.SetOwnership(hflxlumi, False)
    histos['hflxlumi'] = hflxlumi
    
    hflxplt = ROOT.TProfile("hflxplt", "mean flux vs PLT ZERO lumi", nbins, 0., 16000.)
    histos['hflxplt'] = hflxplt
    ROOT.SetOwnership(hflxplt, False)
    hflxhf = ROOT.TProfile("hflxhf", "mean flux vs HFOC lumi", nbins, 0., 16000.)
    histos['hflxhf'] = hflxhf
    ROOT.SetOwnership(hflxhf, False)

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
    
#     if i > 10000:    break

        meanflux = 0
        ndet = 0
        for det in dets:
            index = int(detInfo[det.lower()][0])
            cf = float(detInfo[det.lower()][2])
            if t.rates[index] > 0:
                meanflux += t.rates[index] * cf
                ndet += 1
        if ndet > 0:
            meanflux /= ndet
    
        if t.lumi > 0 and meanflux>0:
            hrfill.Fill(t.fill, meanflux/t.lumi)
            hflxlumi.Fill(t.lumi, meanflux)
            if t.lumiSource[:-1] == "HFOC":
                hflxhf.Fill(t.lumi, meanflux)
                hrfillhf.Fill(t.fill, meanflux/t.lumi)
            if t.lumiSource[:-1] == "PLTZERO":
                hflxplt.Fill(t.lumi, meanflux)
                hrfillplt.Fill(t.fill, meanflux/t.lumi)

    
    ##Mean flux vs hf and plt lumi
    #ROOT.gStyle.SetOptStat(0000);
    #c1 = ROOT.TCanvas("c1", "c1", 600, 400)
    #ROOT.SetOwnership(c1, False)
    #hflxplt.SetLineColor(ROOT.kRed)
    #hflxplt.SetMarkerColor(ROOT.kRed)
    #hflxplt.Draw()
    #hflxhf.SetLineColor(ROOT.kBlue)
    #hflxhf.SetMarkerColor(ROOT.kBlue)
    #hflxhf.Draw("same")

        
    ##Mean flux vs lumi
    #c2 = ROOT.TCanvas("c2", "c2", 1000, 800)
    #ROOT.SetOwnership(c2, False)
    #c2.Divide(1,2)
    #c2.cd(1)
    #hflxlumi.Draw()
    #c2.cd(2)
    #hrfill.Draw()

    print "Histograms: histos[", ','.join(histos.keys()), "]"
    return histos

def ratio2mean():
    """
    ratios of fluence for single detector to mean fluence vs fill nmber
    """
    
    fillsRange = [4850, 5400]
    detRef = ["PFIT", "PFIB", "PNIT", "PNIB", "MNIB", "MNIT"]
    print "Ratio to mean flux of ", ','.join(detRef)
    print "Warming cut =", deltaWarming/60./60., " hours"
    
    dets = ["PFXT", "PFIB", "PFIT", "PNXT", "PNIB", "PNIT", "MFXT", "MFIB", "MFIT", 
        "MNXT", "MNIB", "MNIT"]
    histos = {}
    for det in dets:
        try:
            del histos[det]
        except:
            pass
        histos[det] = ROOT.TH2D(det, det.upper() + "/(" + "+".join(detRef) + ")",
                  (fillsRange[1] - fillsRange[0]), fillsRange[0], fillsRange[1], 1000, 0., 3.)

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
    
        #     if i > 10000:    break

        averef = 0
        nref = 0
        for ref in detRef:
            indRef = int(detInfo[ref.lower()][0])
            cfRef = float(detInfo[ref.lower()][2])
            if t.rates[indRef] > 0:
                averef += t.rates[indRef] * cfRef
                nref += 1
        if nref > 0:
            averef /= nref
        
        for det in dets:
            index = int(detInfo[det.lower()][0])
            cf = float(detInfo[det.lower()][2])

            value = 0.
        
            if averef > 0 and t.rates[index]>0.:    
                value = t.rates[index] * cf / averef
            histos[det].Fill(t.fill, value)

    profx = {}
    for det in dets:
        try:
            profx[det].Delete()
        except:
            pass
        profx[det] = histos[det].ProfileX(det.lower()+"x", 1, -1, "s")
        profx[det].SetTitle(histos[det].GetTitle())
        
    print "Histos (histos[det]) and profiles (profx[det]) available for", ','.join(histos.keys())
    return histos, profx
    
def printFills():
    """
    Print list of fills in FillReport.xls 
    """
    fills = fillReport.getFillCreationTime()
        
    fillsNo = '[' + ','.join(sorted(fills.keys())) + ']'
    print fillsNo
        
##===========================================================
#if __name__ == "__main__": 
    #meanFluenceVsLumi()

    
