#!/usr/bin/env python
"""
Plot lumi/flux/rate from hd5 files

Usage (at root prompt)
TPython::LoadMacro("plothd5fill.py");
Hd5fill f;
f.setFillNo(5267);

f.plotLumi();

f.setTimeLimits(start, end)
# start/end format = "YYYY-MM-DD HH:MM"

f.fillRateGraphs();
f.plotRate(id);

f.fillFluxGraphs();
f.plotFluxAll();


"""

import sys, os
from ROOT import *
import math
import glob



sys.path.append("../Utils/")
sys.path.append("../Config/")

from xutils import *
from xconfig import *

import tables
import numpy as np
import time
from datetime import datetime
from dateutil import tz
os.environ['TZ'] = 'Europe/Zurich'


fill = 4947
dataFilePattern = '/scr1/RadmonHd5/Fills2016/radmon*.hd5'

plotColors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kPink]  

class Hd5fill:
    def __init__(self):
        self.files = []
        cfg = Config('../Config/detectors.ini')
        dummy = cfg.get_option('Detectors')
        self.indx = {}
        for key in dummy.keys():
            tmp = dummy[key].split()
            self.indx[key] = int(tmp[0])
        del dummy
        
        #Groups
        self.groups = {}
        dummy = cfg.get_option('Groups')
        for key in dummy.keys():
            self.groups[key] = dummy[key].split()
        del dummy
        del cfg
        
        self.tsStart = datime2ts('2000-01-01 00:00')
        self.tsEnd =  datime2ts('2100-01-01 00:00')
        self.fill = fill
        
        #Styles
        ROOT.gStyle.SetTitleSize(0.07)
        self.timeFormat = "%H:%M"
        #self.timeFormat = "%m-%d %H:%M"
        
    
    def setTimeLimits(self, start, end):
        self.tsStart = datime2ts(start)
        self.tsEnd =  datime2ts(end)
        
    def setFillNo(self, no):
        self.fill = no
        self.files.append(dataFilePattern.replace('*', str(no)))
        
        
        
    
    def plotPlusMinusLumi(self):
        
        minusz = []
        plusz = []
        timestamps = []
        self.gMinusZ = ROOT.TGraph()
        self.gPlusZ = ROOT.TGraph()
        
        for file in self.files:
            
            try:
                f = tables.open_file(file)
            except Exception as e:
                print e.__doc__
                print e.message
                continue
            
            for leaf in f.walk_nodes(where='/',classname="Leaf"):
                if leaf.name == 'radmonlumi':
                    data =  f.get_node(where='/',name="radmonlumi", classname="Leaf")            
            
                    for item in data:
                        ts = item['timestampsec']
                    
                        if ts < self.tsStart or ts > self.tsEnd:
                            continue
                    
                        if self.fill > 0   and  item['fillnum'] != self.fill:
                            continue
                    
                        nm = self.gMinusZ.GetN()
                        self.gMinusZ.SetPoint(nm, float(ts), float(item['minusz']))
                        np = self.gPlusZ.GetN()
                        self.gPlusZ.SetPoint(np, float(ts), float(item['plusz']))
                        
        # Plot graphs
        self.c = ROOT.TCanvas("cp", "Lumi, Fill " +   str(self.fill) , 800, 600)
        self.c.Divide(1,2)
        self.c.cd(1)
        self.gPlusZ.Draw("AL")
        self.c.cd(2)
        self.gMinusZ.Draw("AL")
        self.gPlusZ.GetXaxis().SetTimeFormat(self.timeFormat)
        self.gMinusZ.GetXaxis().SetTimeFormat(self.timeFormat)
        self.gPlusZ.GetXaxis().SetTimeDisplay(1)
        self.gMinusZ.GetXaxis().SetTimeDisplay(1)    

        self.gMinusZ.SetLineColor(ROOT.kBlue)

        # self.gMinusZ.GetXaxis().SetTitle("time")
        # self.gPlusZ.GetXaxis().SetTitle("time")
        # self.gMinusZ.GetXaxis().SetTitleOffset(0.1)
        # self.gPlusZ.GetXaxis().SetTitleOffset(0.1)

        self.gMinusZ.SetTitle("-Z Lumi, Fill " + str(fillno) )
        self.gPlusZ.SetTitle("+Z Lumi, Fill " + str(fillno) )

        #self.gMinusZ.GetXaxis().SetLabelSize(0.055)
        #self.gMinusZ.GetYaxis().SetLabelSize(0.055)
        #self.gPlusZ.GetXaxis().SetLabelSize(0.055)
        #self.gPlusZ.GetYaxis().SetLabelSize(0.055)


        self.c.Update()      
        
    def plotLumi(self):
        
        lumi = []
        timestamps = []
        self.gLumi = ROOT.TGraph()
        for file in self.files:
            try:
                f = tables.open_file(file)
            except Exception as e:
                print e.__doc__
                print e.message
                continue
            for leaf in f.walk_nodes(where='/',classname="Leaf"):
                if leaf.name == 'radmonlumi':
                    data =  f.get_node(where='/',name="radmonlumi", classname="Leaf")            
            
                    for item in data:
                        ts = item['timestampsec']
                    
                        if ts < self.tsStart or ts > self.tsEnd:
                            continue
                    
                        if self.fill > 0   and  item['fillnum'] != self.fill:
                            continue
                    
                        n = self.gLumi.GetN()
                        self.gLumi.SetPoint(n, float(ts), float(item['avg']))

                        fillno = item['fillnum']
                        
        # Plot graphs
        self.c = ROOT.TCanvas("c", "Lumi, Fill " +   str(fillno) , 800, 600)
        self.gLumi.Draw("AL")
        self.gLumi.GetXaxis().SetTimeFormat(self.timeFormat)
        self.gLumi.GetXaxis().SetTimeDisplay(1)

        self.gLumi.SetLineColor(ROOT.kBlue)

        # self.gLumi.GetXaxis().SetTitle("time")
        # self.gLumi.GetXaxis().SetTitleOffset(0.1)

        self.gLumi.SetTitle("Lumi, Fill " + str(fillno) )


        self.c.Update()    
        
    def fillRateGraphs(self):
        
        self.rateGraphs = [None]*len(self.indx)
        timestamps = []

        for i in range(len(self.indx)):
            self.rateGraphs[i] = ROOT.TGraph()
        
        for file in self.files:
            
            try:
                f = tables.open_file(file)
            except Exception as e:
                print e.__doc__
                print e.message
                continue
            
            for leaf in f.walk_nodes(where='/',classname="Leaf"):
                if leaf.name == 'radmonraw':
                    data =  f.get_node(where='/',name="radmonraw", classname="Leaf")            
            
                    for item in data:
                        ts = item['timestampsec']
                    
                        if ts < self.tsStart or ts > self.tsEnd:
                            continue
                    
                        if self.fill > 0   and  item['fillnum'] != self.fill:
                            continue
                        
                        if len(item['rate']) == 1:
                            id = item['channelid'] 
                            n = self.rateGraphs[id].GetN()
                            self.rateGraphs[id].SetPoint(n, float(ts), float(item['rate']))
                        else:
                            for i in range(len(self.indx)):  
                                n = self.rateGraphs[i].GetN()
                                self.rateGraphs[i].SetPoint(n, float(ts), float(item['rate'][i]))                            
 
    def plotRate(self, id):
        # Plot graphs
        key = (key for key,value in self.indx.items() if value == id).next() 
        
        self.c = ROOT.TCanvas("cp", "Rate " + str(key).upper() + ", Fill " +   str(self.fill) , 600, 400)
        self.rateGraphs[id].Draw("AL")
        self.rateGraphs[id].GetXaxis().SetTimeFormat(self.timeFormat)
        self.rateGraphs[id].GetXaxis().SetTimeDisplay(1)    

        self.rateGraphs[id].SetLineColor(ROOT.kBlue)

        self.rateGraphs[id].SetTitle("Rate " + str(key).upper() + ", Fill " +   str(self.fill) )

        self.c.Update()        
        
        
    def fillFluxGraphs(self):
        
        self.fluxGraphs = [None]*len(self.indx)
        timestamps = []

        for i in range(len(self.indx)):
            self.fluxGraphs[i] = ROOT.TGraph()
        
        for file in self.files:
            
            try:
                f = tables.open_file(file)
            except Exception as e:
                print e.__doc__
                print e.message
                continue
            
            for leaf in f.walk_nodes(where='/',classname="Leaf"):
                if leaf.name == 'radmonflux':
                    data =  f.get_node(where='/',name="radmonflux", classname="Leaf")            
            
                    for item in data:
                        ts = item['timestampsec']
                    
                        if ts < self.tsStart or ts > self.tsEnd:
                            continue
                    
                        if self.fill > 0   and  item['fillnum'] != self.fill:
                            continue

                        for i in range(len(self.indx)):  
                            n = self.fluxGraphs[i].GetN()
                            self.fluxGraphs[i].SetPoint(n, float(ts), float(item['data'][i]))
    
                        
    def plotFluxAll(self):
        #ROOT.gROOT.SetStyle("Plain")
        #ROOT.gStyle.SetFillColor(0)
        self.c = ROOT.TCanvas("c", "Flux, Fill " +   str(self.fill) , 800, 800)
        self.c.Divide(2,2)
        
        maxY = {}
        for key in self.groups.keys():
            maxY[key] = -1000000.
        
        
        #Max value for Y axis
        for key in self.groups.keys():
            for j in range(len(self.groups[key])):
                det = self.groups[key][j].lower()
                id = self.indx[det]
                yy = ROOT.TMath.MaxElement(self.fluxGraphs[id].GetN(),self.fluxGraphs[id].GetY());
                if yy > maxY[key]:
                    maxY[key] = yy
                
        i = 0
        for key in self.groups.keys():
            self.c.cd(i+1)
            i += 1
            for j in range(len(self.groups[key])):
                det = self.groups[key][j].lower()
                id = self.indx[det]
                self.fluxGraphs[id].SetTitle(det.upper())
                self.fluxGraphs[id].SetLineColor(plotColors[j])
                if j == 0: 
                    self.fluxGraphs[id].Draw("AL")
                else:
                    self.fluxGraphs[id].Draw("L")
                #self.fluxGraphs[id].GetYaxis().SetLimits(0, 1.2*maxY[key])
                self.fluxGraphs[id].SetMaximum(1.2*maxY[key])
                self.fluxGraphs[id].GetXaxis().SetTimeFormat(self.timeFormat)
                self.fluxGraphs[id].GetXaxis().SetTimeDisplay(1)    
                
        self.c.Update()             
