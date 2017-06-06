#!/usr/bin/env python
"""
Various tests + normalization to offline lumi
"""

import os, sys
import ROOT
import math
import pprint 
import re
sys.path.append("../Utils/")
sys.path.append("../Config/")
from xconfig import *
from fillReport import *

configFile = '../Config/detectors.ini'
fillReportFile  = "../Config/FillReport.xls"
deltaWarming = 0*60*60
files = "/scr1/RadMonLumi/2016/OfflineLumi/Radmon_normtag_BRIL/*.root"
#files = "/scr1/RadMonLumi/2016/OfflineLumi/Old/Radmon_normtag_BRIL/radmonLumi_normtag_BRIL*.root"

fillsRange = [4850, 5500]

class NormToLumi:
    def __init__(self):
        """
        Initialization
        """
        self.t = ROOT.TChain("t")
        self.t.Add(files)
        self.deltaWarming = deltaWarming
        self.fillsRange = fillsRange
        self.fillReport = FillReport(fillReportFile)
    
        self.detInfo = {}
        cfg = Config('../Config/detectors.ini')
        dummy = cfg.get_option('Detectors')
        for key in dummy.keys():
            self.detInfo[key] = dummy[key].split()
    
        #pprint.pprint(self.detInfo)
        
    def changeFillsRange(self, fillStart, fillEnd):
        """
        Change fills range
        """
        self.fillsRange = [fillStart, fillEnd]
        
    def setDeltaWarming(self, hrs):
        """
        Set warming cut (hours)
        """
        self.deltaWarming = hrs*60*60
        
    def meanFlux(self, dets, calib):
        """
        Calculate mean flux/rate for the set of detectors
        calib = 1 - flux
        calib = 0 - rate
        """
        meanflux = 0
        ndet = 0
        for det in dets:
            index = int(self.detInfo[det.lower()][0])
            if  calib ==1:
                cf = float(self.detInfo[det.lower()][2])
            else:
                cf =1.
            if self.t.rates[index] > 0:
                meanflux += self.t.rates[index] * cf
                ndet += 1
        if ndet > 0:
            meanflux /= ndet        
        return meanflux
    
    def meanFluxVsLumi(self):
        """
        mean neutron flux/rate vs Lumi
        """
        lumiUp = 16000
        nbins = 500
        
        dets = ["PFIT", "PNIT", "PNIB", "MNIB", "MNIT"]
        #dets = ["PFXT", "MFXT", "MNXT"]
        
        calib = 1

        print "Fills:", fillsRange[0], '-', fillsRange[1]
        print "deltaWarming:", deltaWarming
        print "Flux/Rate:", calib
        print "Detectors:", dets 
    
        #Booking 
        fillprofs = {}
        # Ratios flux over lumi
        fillbest = ROOT.TProfile("fillbest", "ratio mean flux over best lumi vs fill No", 
                  (fillsRange[1] - fillsRange[0]), fillsRange[0], fillsRange[1], 's')
        fillprofs["fillbest"] = fillbest
        fillplt = ROOT.TProfile("fillplt", "ratio mean flux over PLTZERO lumi vs fill No", 
                  (fillsRange[1] - fillsRange[0]), fillsRange[0], fillsRange[1], 's')
        fillprofs["fillplt"] = fillplt
        fillhf = ROOT.TProfile("fillhf", "ratio mean flux over HFOC lumi vs fill No", 
                  (fillsRange[1] - fillsRange[0]), fillsRange[0], fillsRange[1], 's')
        fillprofs["fillhf"] = fillhf       

        #Profiles flux vs lumi
        lumiprofs = {}
        rlumibest = ROOT.TProfile("rlumibest", "mean flux vs  best lumi", nbins, 0., lumiUp)
        lumiprofs["rlumibest"] = rlumibest        
        rlumihf  = ROOT.TProfile("rlumihf", "mean flux vs  HFOC lumi", nbins, 0., lumiUp)
        lumiprofs["rlumihf"] = rlumihf           
        rlumiplt  = ROOT.TProfile("rlumiplt", "mean flux vs  PLT ZERO lumi", nbins, 0., lumiUp)
        lumiprofs["rlumiplt"] = rlumiplt    
        
        rprofs = {}
        # Ratios flux over lumi  vs lumi
        rbest = ROOT.TProfile("rbest", "ratio mean flux over best lumi vs best lumi", nbins, 0., lumiUp)
        rprofs["rbest"] = rbest
        rplt = ROOT.TProfile("rplt", "ratio mean flux over PLTZERO lumi vs PLT ZERO lumi", nbins, 0., lumiUp)
        rprofs["rplt"] = rplt
        rhf = ROOT.TProfile("rhf", "ratio mean flux over HFOC lumi vs HFOC lumi", nbins, 0., lumiUp)
        rprofs["rhf"] = rhf       

        
        #Filling
        for i in range(0, self.t.GetEntries()) :
            nb = self.t.GetEntry(i)
            if nb < 0:
                continue
    
            #if i > 1000:    break
        
            if self.t.fill <  self.fillsRange[0] or self.t.fill > self.fillsRange[1]:
                continue
            if "STABLE BEAMS" not in str(self.t.beamStatus):
                continue
            if self.t.tstamp > self.t.fillEnd:
                continue
            if self.t.tstamp - self.t.fillStable < self.deltaWarming:
                continue
        
            meanflux = self.meanFlux(dets, calib)

            if self.t.lumi > 0 and meanflux>0:
                fillbest.Fill(self.t.fill, meanflux/self.t.lumi)
                rbest.Fill(self.t.lumi, meanflux/self.t.lumi)
                rlumibest.Fill(self.t.lumi, meanflux)
                if "HFOC" in self.t.lumiSource:
                    rlumihf.Fill(self.t.lumi, meanflux)
                    fillhf.Fill(self.t.fill, meanflux/self.t.lumi)
                    rhf.Fill(self.t.lumi, meanflux/self.t.lumi)                    
                if "PLTZERO" in self.t.lumiSource:
                    rlumiplt.Fill(self.t.lumi, meanflux)
                    fillplt.Fill(self.t.fill, meanflux/self.t.lumi)  
                    rplt.Fill(self.t.lumi, meanflux/self.t.lumi)
       
        print 'Ratio profiles available for', ','.join(fillprofs.keys())
        print 'Flux vs lumi profiles available for', ','.join(lumiprofs.keys())        
        return fillprofs, lumiprofs, rprofs
        
        
        
    def printFills(self):
        """
        Print list of fills in FillReport.xls 
        """
        fillsNo = []
        fills = self.fillReport.getFillCreationTime()
        for fill in fills.keys():
            if int(fill) < self.fillsRange[0] or int(fill) > self.fillsRange[1]:
                continue
            fillsNo.append(int(fill))
        
        print sorted(fillsNo)
        
    def ratio2meanExt(self):
        """
        TProfile of ratio of the internal detector rate to average rate of external
        detectors vs fill no
        """
        detRef = ["PFXT", "MFXT", "MNXT"]
        dets = ["PFIB", "PFIT",  "PNIB", "PNIT",  "MFIB", "MFIT",  "MNIB", "MNIT"]
        
        profs = {}
        for det in dets:
            try:
                del profs[det]
            except:
                pass
            profs[det] = ROOT.TProfile('r_' + det.lower(), det.upper() + "/(" + "+".join(detRef) + ")", (fillsRange[1] - fillsRange[0]), fillsRange[0], fillsRange[1], 's')
        
        #Filling
        for i in range(0, self.t.GetEntries()) :
            nb = self.t.GetEntry(i)
            if nb < 0:
                continue
    
            #if i > 10000:    break
        
            if self.t.fill <  self.fillsRange[0] or self.t.fill > self.fillsRange[1]:
                continue
            if "STABLE BEAMS" not in str(self.t.beamStatus):
                continue
            if self.t.tstamp > self.t.fillEnd:
                continue
            if self.t.tstamp - self.t.fillStable < self.deltaWarming:
                continue
        

            averef = 0
            nref = 0
            for ref in detRef:
                indRef = int(self.detInfo[ref.lower()][0])
                cfRef = float(self.detInfo[ref.lower()][2])
                if self.t.rates[indRef] > 0:
                    averef += self.t.rates[indRef] * cfRef
                    nref += 1
            if nref > 0:
                averef /= nref
        
            for det in dets:
                index = int(self.detInfo[det.lower()][0])
                cf = float(self.detInfo[det.lower()][2])

                value = 0.
        
                if averef > 0 and self.t.rates[index]>0.:    
                    value = self.t.rates[index] * cf / averef
                    
                profs[det].Fill(self.t.fill, value)        
        
        
        print 'Ratio profiles available for', ','.join(profs.keys())
        return profs

    def rateVsMeanExt(self):
        """
        TProfile of the rate of the internal detector vs  average rate of external
        detectors 
        """
        detRef = ["PFXT", "MFXT", "MNXT"]
        dets = ["PFIB", "PFIT",  "PNIB", "PNIT",  "MFIB", "MFIT",  "MNIB", "MNIT"]
        
        nbins = 400
        xup = 4000.
        
        profs = {}
        for det in dets:
            try:
                del profs[det]
            except:
                pass
            profs[det] = ROOT.TProfile('c_' + det.lower(), det.upper() + " vs (" + "+".join(detRef) + ")",  nbins, 0., xup, 's')
        
        #Filling
        for i in range(0, self.t.GetEntries()) :
            nb = self.t.GetEntry(i)
            if nb < 0:
                continue
    
            #if i > 10000:    break
        
            if self.t.fill <  self.fillsRange[0] or self.t.fill > self.fillsRange[1]:
                continue
            if "STABLE BEAMS" not in str(self.t.beamStatus):
                continue
            if self.t.tstamp > self.t.fillEnd:
                continue
            if self.t.tstamp - self.t.fillStable < self.deltaWarming:
                continue
        

            averef = 0
            nref = 0
            for ref in detRef:
                indRef = int(self.detInfo[ref.lower()][0])
                cfRef = float(self.detInfo[ref.lower()][2])
                if self.t.rates[indRef] > 0:
                    averef += self.t.rates[indRef] * cfRef
                    nref += 1
            if nref > 0:
                averef /= nref
        
            for det in dets:
                index = int(self.detInfo[det.lower()][0])
                cf = float(self.detInfo[det.lower()][2])

                value = 0.
        
                if averef > 0 and self.t.rates[index]>0.:    
                    value = self.t.rates[index] * cf 
                    
                    profs[det].Fill(averef, value)        
        
        
        print 'Profiles available for', ','.join(profs.keys())
        return profs

    def ratioVsMeanExt(self):
        """
        TProfile of the ratio of the internal detector over mean of the externals  vs  average rate of external
        detectors 
        """
        detRef = ["PFXT", "MFXT", "MNXT"]
        dets = ["PFIB", "PFIT",  "PNIB", "PNIT",  "MFIB", "MFIT",  "MNIB", "MNIT"]
        
        nbins = 400
        xup = 4000.
        
        profs = {}
        for det in dets:
            try:
                del profs[det]
            except:
                pass
            profs[det] = ROOT.TProfile('c_' + det.lower(), det.upper() + " vs (" + "+".join(detRef) + ")",  nbins, 0., xup) #, 's')
        
        #Filling
        for i in range(0, self.t.GetEntries()) :
            nb = self.t.GetEntry(i)
            if nb < 0:
                continue
    
            #if i > 10000:    break
        
            if self.t.fill <  self.fillsRange[0] or self.t.fill > self.fillsRange[1]:
                continue
            if "STABLE BEAMS" not in str(self.t.beamStatus):
                continue
            if self.t.tstamp > self.t.fillEnd:
                continue
            if self.t.tstamp - self.t.fillStable < self.deltaWarming:
                continue
        

            averef = 0
            nref = 0
            for ref in detRef:
                indRef = int(self.detInfo[ref.lower()][0])
                cfRef = float(self.detInfo[ref.lower()][2])
                if self.t.rates[indRef] > 0:
                    averef += self.t.rates[indRef] * cfRef
                    nref += 1
            if nref > 0:
                averef /= nref
        
            for det in dets:
                index = int(self.detInfo[det.lower()][0])
                cf = float(self.detInfo[det.lower()][2])

                value = 0.
        
                if averef > 0 and self.t.rates[index]>0.:    
                    value = self.t.rates[index] * cf 
                    
                    profs[det].Fill(averef, value/averef)        
        
        
        print 'Profiles available for', ','.join(profs.keys())
        return profs

