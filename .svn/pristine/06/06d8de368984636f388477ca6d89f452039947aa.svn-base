#!/usr/bin/env python

"""
Draw ratio rate/lumi and study beginning of the fill
Usage (at root prompt)
TPython::LoadMacro("radmonAnaW.py");
RadmonAnaW f;
f.processFill(4448)
f.draw('h', 'pfib')
ipython notebook --no-browser --ip=188.184.70.168 --port=8888

"""

import sys, os
import ROOT
import math
from xutils import *
from xconfig import *
import math

from fillReport import *

#fills = [4243, 4538]
#Excluded fills   3976, 4266, 4268, 4269, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513

fills = [  3960, 3962, 3965, 3971, 3974, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257,  4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467,4476, 4477, 4479, 4485, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4560, 4562, 4565, 4569]

output = "/afs/cern.ch/work/g/grandr/Bril/Data/warmingByFill.root"


class RadmonAnaW:
    def __init__(self):
        cfg = Config('radmonAnaW.ini')
        self.secsPerBin = int(cfg.get_option('Env', 'secsPerBin'))
        self.minutes = int(cfg.get_option('Env', 'minutes'))
        #self.binsY = int(cfg.get_option('Env', 'binsY')) 
        self.lumiFilePattern = cfg.get_option('Env', 'lumiFilePattern')
        self.radmonFilePattern = cfg.get_option('Env', 'radmonFilePattern')
        self.fillReport = FillReport(cfg.get_option('Env', 'fillReport'))
        self.minDura = int(cfg.get_option('Env', 'minDura'))

        #Calbraition factors for detectors
        dd = cfg.get_option('Detectors')
        
        #Fit parameters
        self.p0set = [float(x) for x in cfg.get_option('Fit', 'p0set').split()]
        self.p1set = [float(x) for x in cfg.get_option('Fit', 'p1set').split()]       
        self.p2set = [float(x) for x in cfg.get_option('Fit', 'p2set').split()] 
        self.maxsecs = float(cfg.get_option('Fit', 'maxsecs'))
        
        del cfg 
        
        self.detectorData = {}
	for key in dd.keys():
	    self.detectorData[key] = dd[key].split()
	    
        self.p0 = [-1000.]*16
        self.p0Err = [-1000.]*16
        self.p1 = [-1000.]*16
        self.p1Err = [-1000.]*16
        self.p2 = [-1000.]*16
        self.p2Err = [-1000.]*16
        
        
        self.hlumi = 0
        self.hradmon = {}

    def processFill(self, fill):  
        
        self.fill = fill
        
        print "Fill", str(fill) + '...'
        self.tsStable = float(self.fillReport.getFillStableTime(fill))
        self.tsColl = 0

        #Check duration of the fill
        if int(self.fillReport.getFillDuration(self.fill)) < self.minDura * 60:
            print "Short fill ", int(self.fillReport.getFillDuration(self.fill))/60, "minutes"
            return -1
        
        # Histo X limits and binsX

        peakInstLumi = self.fillReport.getFillPeakInstLumi(fill)
        yMax =  peakInstLumi * 1.3

        if yMax == 0:
            print "Zero peak instant lumi"
            return -1
        
        #Read lumi file and find start of the collisions
        # Let it be the tstamp whn instant lumi > 0.5 of peakInstLumi
        lumiFile = ROOT.TFile(self.lumiFilePattern.replace('__XXX__', str(fill)), 'READ')        
        treeLumi = lumiFile.Get("t")
        for i in range(0, treeLumi.GetEntries()):
            nb = treeLumi.GetEntry(i)
	    if nb < 0:
		continue
            if treeLumi.bestLumi > 0.5*peakInstLumi:
                self.tsColl =  treeLumi.tstamp
                break

        tsStart = -1 * self.minutes*60
        tsEnd = float(self.fillReport.getFillEndTime(fill) - self.tsColl + self.minutes*60)
        self.binsX = int((tsEnd - tsStart)/self.secsPerBin)

        # Override number of bins in Y
        self.binsY = int(yMax/3.)
        
        print "Secs per bin", self.secsPerBin
        
        #Lumi histogramm
        self.hlumi = ROOT.TH2D("hlumi", "Lumi, Fill " + str(fill), self.binsX, tsStart, tsEnd, self.binsY, 0., yMax)
        #self.hlumi.SetBit(ROOT.TH1.kCanRebin)
        self.hlumi.SetDirectory(0)
 
        # Filling Lumi
        for i in range(0, treeLumi.GetEntries()):
            nb = treeLumi.GetEntry(i)
	    if nb < 0:
		continue
            self.hlumi.Fill(treeLumi.tstamp  - self.tsColl, treeLumi.bestLumi)


        del treeLumi       

        # Radmon histograms
        self.hradmon = {}
        #print binsX, tsStart, tsEnd
        for key in self.detectorData.keys():
            self.hradmon[key] = ROOT.TH2D("h" + key, "Normalized rate " + key.upper() + ", Fill " + str(fill), self.binsX, tsStart, tsEnd, self.binsY, 0., yMax)
            self.hradmon[key].SetDirectory(0)
            #self.hradmon[key].SetBit(ROOT.TH1.kCanRebin)        
        radmonFile = ROOT.TFile(self.radmonFilePattern.replace('__XXX__', str(fill)),  "READ")
        treeRadmon = radmonFile.Get("t")
        #Filling normalized radmon rates
        for i in range(0, treeRadmon.GetEntries()):
            nb = treeRadmon.GetEntry(i)
	    if nb < 0:
		continue        
        
            for key in self.detectorData.keys():
                indx = int(self.detectorData[key][0])
                p1 = float(self.detectorData[key][1])
                p0 = float(self.detectorData[key][3])
                nRate = treeRadmon.rates[indx] * p1 + p0
                self.hradmon[key].Fill(treeRadmon.tstamp - self.tsColl, nRate)
            

        del treeRadmon
        
        return 0

    def makeProfiles(self):
        self.plumi = self.hlumi.ProfileX()
        self.plumi.SetName('plumi')
        self.pradmon = {}
        for key in self.detectorData.keys():
            self.pradmon[key] = self.hradmon[key].ProfileX()
            self.pradmon[key].SetName('p' + key)
        
    def setFitLimits(self):
        #Use lumi profile to find start and end of fit function and create function itsef
        yMax = self.fillReport.getFillPeakInstLumi(self.fill) * 0.7
        self.fitStart = -40000.
        nbins =  self.plumi.GetSize()-2
        for i in range(0, nbins):
            if self.plumi.GetBinContent(i) > yMax:
                self.fitStart = self.plumi.GetBinCenter(i)
                break
        
        xlast = self.plumi.GetBinCenter(nbins)
        if xlast > self.fitStart + self.maxsecs:
            self.fitEnd = self.fitStart + self.maxsecs
        else:
            self.fitEnd = xlast
        
        #Make function
        self.func = ROOT.TF1('func', '[0]*(1-([1]*exp(-1*x/[2] )))', self.fitStart, self.fitEnd)
        
        print "Fit limits", self.fitStart, self.fitEnd
    

    def makeRatios(self):
        self.rradmon = {}
        for key in self.detectorData.keys():
            self.rradmon[key] = ROOT.TGraphErrors()
            self.rradmon[key].SetTitle(key + "/Lumi")
            self.rradmon[key].SetName('r' + key)
            
            for i in range(1, self.binsX):
                x = self.plumi.GetBinCenter(i)
                lumi = self.plumi.GetBinContent(i)
                lumiErr = self.plumi.GetBinError(i)
                rate = self.pradmon[key].GetBinContent(i)
                rateErr = self.pradmon[key].GetBinError(i)
                if lumi == 0:
                    y = 0
                    rLumi = 0
                else:
                    y = rate/lumi
                    rLumi = lumiErr/lumi
                
                if rate == 0:
                    rRate = 0
                else:
                    rRate = rateErr/rate
                
                dy = y * math.sqrt(rLumi*rLumi + rRate*rRate)
                
                pointNo = self.rradmon[key].GetN()
                self.rradmon[key].SetPoint(pointNo, x, y)
                self.rradmon[key].SetPointError(pointNo, 0, dy)

            #if key == 'pfib':
                #self.rradmon[key].Draw('AP')
                #print self.rradmon[key].GetName()
                #raw_input()
                
    def fitRatio(self, key):
        
        self.func.SetParameters(self.p0set[0], self.p1set[0], self.p2set[0])
        self.func.SetParLimits(0, self.p0set[1], self.p0set[2])
        self.func.SetParLimits(1, self.p1set[1], self.p1set[2])
        self.func.SetParLimits(2, self.p2set[1], self.p2set[2])
        
        self.rradmon[key].Fit('func', "CROBFQS", "", self.fitStart, self.fitEnd)	
        #self.rradmon[key].Fit('func', "CROBFS", "", self.fitStart, self.fitEnd)	
        
        pp0 = self.rradmon[key].GetFunction('func').GetParameter(0)
        pp0Err = self.rradmon[key].GetFunction('func').GetParError(0)
        pp1 = self.rradmon[key].GetFunction('func').GetParameter(1)
        pp1Err = self.rradmon[key].GetFunction('func').GetParError(1)        
        pp2 = self.rradmon[key].GetFunction('func').GetParameter(2)
        pp2Err = self.rradmon[key].GetFunction('func').GetParError(2) 
        
        return (pp0, pp0Err, pp1, pp1Err, pp2, pp2Err)
        
    def fitAllRatios(self):
        for key in self.detectorData.keys():
            indx = int(self.detectorData[key][0])
            (self.p0[indx], self.p0Err[indx], self.p1[indx], self.p1Err[indx], self.p2[indx], self.p2Err[indx]) = self.fitRatio(key)
            #print key, pp0, pp1, pp2
            
        return (self.p0, self.p0Err, self.p1, self.p1Err, self.p2, self.p2Err)
        
    
    def getUndercount(self, hrs):
        underCount = [-10000.]*16
        totalCount = [-10000.]*16
        
        start = self.fitStart
        end = start + 3600*hrs
        for i in range(0, 16):
            if self.p0[i] != -1000.:
                underCount[i] = self.p0[i]*self.p1[i]*self.p2[i]*(math.exp(-1*start/self.p2[i]) - math.exp(-1*end/self.p2[i]) )
                totalCount[i] = self.p0[i]*(end - start)
        return totalCount, underCount
                                                                                              
    
    def printList(self):
        print "2D histograms:"
        print "hlumi,", ",".join(self.hradmon.keys())
        
    #def draw(self, mode, key, opt = ""):
        #ROOT.gROOT.cd()
        #if mode.lower() != 'h' and mode.lower() != 'r' and mode.lower() != 'p':
            #print "Wrong mode. Possilble modes are:"
            #print "\"h\" for 2D histogram"
            #print "\"p\" for TProfile"
            #print "\"r\" for Ratio"
        
        #c= ROOT.TCanvas("c", "Data")
        #c.cd()
        #name = str(mode.strip() + key.strip())
        #ROOT.gROOT.FindObjectAny(name).Draw(opt.strip())
        ##c.Update()
        
    def draw(self, mode, key, opt = ""):
        c= ROOT.TCanvas("c", "Data")
        if key.strip() == 'lumi' and mode.strip() == 'h':
            self.hlumi.Draw(opt.strip())
        elif key.strip() == 'lumi' and mode.strip() == 'p':
            self.plumi.Draw(opt.strip())
        else:
            if mode == 'h':
                self.hradmon[key].Draw(opt.strip())
            elif mode == 'p':
                self.pradmon[key].Draw(opt.strip())
            elif mode == 'r':
                self.rradmon[key].Draw(opt.strip())
            else:
                print "Wrong mode for radmon plot"
        c.cd()
        #ROOT.gROOT.FindObjectAny(name).Draw(opt)
        #c.Update()
        
    def getFillData(self):
        tsStart = int(self.fillReport.getFillCreationTime(self.fill))
        tsStable = int(self.fillReport.getFillStableTime(self.fill))
        tsEnd  = int(self.fillReport.getFillEndTime(self.fill))
        duration = int(self.fillReport.getFillDuration(self.fill))
        bField = float(self.fillReport.getFillField(self.fill))
        beamEnergy = float(self.fillReport.getFillBeamEnergy(self.fill))
        peakLumi = float(self.fillReport.getFillPeakInstLumi(self.fill))
        
        return (tsStart, self.tsColl, tsStable, tsEnd, duration, bField, beamEnergy, peakLumi)
        
    
def radmonAnaw():
    
    ROOT.gROOT.ProcessLine(\
"struct FillData{\
    Int_t fill;\
    Int_t fillStart;\
    Int_t fillColl;\
    Int_t fillStable;\
    Int_t fillEnd;\
    Int_t durationStable;\
    Double_t bField;\
    Double_t beamEnergy;\
    Double_t peakLumi;\
};")
    from ROOT import FillData
    
    ROOT.gROOT.ProcessLine(\
"struct FitData{\
    Double_t p0[16];\
    Double_t p0Err[16];\
    Double_t p1[16];\
    Double_t p1Err[16];\
    Double_t p2[16];\
    Double_t p2Err[16];\
};")  
    from ROOT import FitData
    
    ROOT.gROOT.ProcessLine(\
"struct UcountData{\
    Double_t tcount1[16];\
    Double_t ucount1[16];\
    Double_t tcount2[16];\
    Double_t ucount2[16];\
    Double_t tcount4[16];\
    Double_t ucount4[16];\
};")  
    
    from ROOT import UcountData
    
    fillData = FillData()
    fitData = FitData()
    ucountData = UcountData()
    
    fout = ROOT.TFile(output, 'RECREATE')
    
    
    t = ROOT.TTree('t', 'Warming by fills')
    t.Branch('fillBranchI', fillData, 'fill/I:fillStart/I:fillColl/I:fillStable/I:fillEnd/I:durationStable/I')
    t.Branch('fillBranchD', ROOT.AddressOf(fillData, 'bField'), 'bField/D:beamEnergy/D:peakLumi/D')    
    t.Branch('fitBranch', fitData, 'p0[16]/D:p0err[16]/D:p1[16]/D:p1err[16]/D:p2[16]/D:p2err[16]/D')
    t.Branch('ucountBranch', ucountData, 'tcount1[16]/D:ucount1[16]/D:tcount2[16]/D:ucount2[16]/D:tcount4[16]/D:ucount4[16]/D')
    
    
    for fill in fills:
        f = RadmonAnaW()
        
       
        status = f.processFill(fill)
        if status < 0:
            continue
        
        (fillData.fillStart, fillData.fillColl, fillData.fillStable, fillData.fillEnd, fillData.durationStable, fillData.bField, fillData.beamEnergy, fillData.peakLumi) = f.getFillData()
        f.makeProfiles()
        f.makeRatios()
        f.setFitLimits()
        fillData.fill = fill

    ##f.draw('r', 'pfib')
        #(fitData.p0, fitData.p0Err, fitData.p1, fitData.p1Err, fitData.p2, fitData.p2Err) = f.fitAllRatios()
        #ucountData.ucount = f.getUndercount()
        
        (p0, p0Err, p1, p1Err, p2, p2Err) = f.fitAllRatios()
        for i in range(0, 16):
            fitData.p0[i] = p0[i]
            fitData.p0Err[i] = p0Err[i]
            fitData.p1[i] = p1[i]
            fitData.p1Err[i] = p1Err[i]        
            fitData.p2[i] = p2[i]
            fitData.p2Err[i] = p2Err[i]

        tcount, ucount = f.getUndercount(1)
        for i in range(0, 16):
            ucountData.ucount1[i] = ucount[i]
            ucountData.tcount1[i] = tcount[i]

        tcount, ucount = f.getUndercount(2)
        for i in range(0, 16):
            ucountData.ucount2[i] = ucount[i]
            ucountData.tcount2[i] = tcount[i]            

        tcount, ucount = f.getUndercount(4)
        for i in range(0, 16):
            ucountData.ucount4[i] = ucount[i]
            ucountData.tcount4[i] = tcount[i]


            
        t.Fill()
        del f

    fout.Write()
    fout.Close()
    
if __name__ == "__main__":
    radmonAnaw()
