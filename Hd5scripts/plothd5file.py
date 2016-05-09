#!/usr/bin/env python
"""
Plot lumi/flux/rate from hd5 files

Usage (at root prompt)
TPython::LoadMacro("plothd5file.py");
Hd5file f;
f.plotLumi()

f.setTimeLimits(start, end)
# start/end format = "YYYY-MM-DD HH:MM"

f.fillRateGraphs()
f.plotRate(id)

f.fillFluxGraphs();
f.plotFluxAll()


"""

import sys, os
from ROOT import *
import math

sys.path.append("../Utils/")
sys.path.append("../Config/")

from xutils import *
from xconfig import *

import tables
import numpy as np
import datetime as dt
import time

## Fill
#filesDefault = ['/home/data/RadMonData/RadmonHd5/2016/7ce07db4-aff7-41f1-8124-21ae4741c468_1604222046_6.hd5',
                #'/home/data/RadMonData/RadmonHd5/2016/7ce07db4-aff7-41f1-8124-21ae4741c468_1604221208_5.hd5'
                #]
                ##Fill 4861
#filesDefault = ['/scr1/RadmonHd5/2016/7ce07db4-aff7-41f1-8124-21ae4741c468_1604241600_11.hd5',
                #'/scr1/RadmonHd5/2016/7ce07db4-aff7-41f1-8124-21ae4741c468_1604250039_12.hd5'
                #]
                #Fill 4879
#filesDefault = ['/scr1/RadmonHd5/2016/7ce07db4-aff7-41f1-8124-21ae4741c468_1604281749_23.hd5',
                #'/scr1/RadmonHd5/2016/7ce07db4-aff7-41f1-8124-21ae4741c468_1604290227_24.hd5'
                #]
filesDefault = ['/scr1/RadmonHd5/2016/022d7b58-1509-455f-90ff-90526090a267_1605061909_0.hd5',
                '/scr1/RadmonHd5/2016/022d7b58-1509-455f-90ff-90526090a267_1605070336_1.hd5',
                '/scr1/RadmonHd5/2016/022d7b58-1509-455f-90ff-90526090a267_1605071202_2.hd5',
                '/scr1/RadmonHd5/2016/022d7b58-1509-455f-90ff-90526090a267_1605072027_3.hd5',
                '/scr1/RadmonHd5/2016/022d7b58-1509-455f-90ff-90526090a267_1605080453_4.hd5',
                '/scr1/RadmonHd5/2016/022d7b58-1509-455f-90ff-90526090a267_1605081319_5.hd5',
                '/scr1/RadmonHd5/2016/022d7b58-1509-455f-90ff-90526090a267_1605082145_6.hd5',
                
                ]


plotColors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kPink]  

class Hd5file:
    def __init__(self):
        self.files = filesDefault
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
        self.fill = -1
        self.files = filesDefault
        
        #Styles
        ROOT.gStyle.SetTitleSize(0.07)
        self.timeFormat = "%H:%M"
        #self.timeFormat = "%m-%d %H:%M"
        
    
    def setTimeLimits(self, start, end):
        self.tsStart = datime2ts(start)
        self.tsEnd =  datime2ts(end)
        
    def setFilNo(no):
        self.fill = no
        
    
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
                    
                        if self.fill > 0   and  item['fillnum'] != self.fillno:
                            continue
                    
                        nm = self.gMinusZ.GetN()
                        self.gMinusZ.SetPoint(nm, float(ts), float(item['minusz']))
                        np = self.gPlusZ.GetN()
                        self.gPlusZ.SetPoint(np, float(ts), float(item['plusz']))

                        fillno = item['fillnum']
                        
        # Plot graphs
        self.c = ROOT.TCanvas("cp", "Lumi, Fill " +   str(fillno) , 800, 600)
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
                    
                        if self.fill > 0   and  item['fillnum'] != self.fillno:
                            continue
                    
                        n = self.gLumi.GetN()
                        self.gLumi.SetPoint(n, float(ts), float(item['avg']))

                        fillno = item['fillnum']
                        
        # Plot graphs
        self.c = ROOT.TCanvas("c", "Lumi, Fill " +   str(fillno) , 800, 600)
        self.gLumi.Draw("AL")
        self.gLumi.GetXaxis().SetTimeFormat(self.timeFormat)
        self.gLumi.GetXaxis().SetTimeFormat(self.timeFormat)

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
                    
                        if self.fill > 0   and  item['fillnum'] != self.fillno:
                            continue
                        
                        id = item['channelid'] 
                        n = self.rateGraphs[id].GetN()
                        self.rateGraphs[id].SetPoint(n, float(ts), float(item['rate']))
                        self.fillno = item['fillnum']
                        
 
    def plotRate(self, id):
        # Plot graphs
        key = (key for key,value in self.indx.items() if value == id).next() 
        
        self.c = ROOT.TCanvas("cp", "Rate " + str(key).upper() + ", Fill " +   str(self.fillno) , 600, 400)
        self.rateGraphs[id].Draw("AL")
        self.rateGraphs[id].GetXaxis().SetTimeFormat(self.timeFormat)
        self.rateGraphs[id].GetXaxis().SetTimeDisplay(1)    

        self.rateGraphs[id].SetLineColor(ROOT.kBlue)

        self.rateGraphs[id].SetTitle("Rate " + str(key).upper() + ", Fill " +   str(self.fillno) )

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
                    
                        if self.fill > 0   and  item['fillnum'] != self.fillno:
                            continue

                        for i in range(len(self.indx)):  
                            n = self.fluxGraphs[i].GetN()
                            self.fluxGraphs[i].SetPoint(n, float(ts), float(item['data'][i]))
    
                        self.fillno = item['fillnum']
                        
    def plotFluxAll(self):
        #ROOT.gROOT.SetStyle("Plain")
        #ROOT.gStyle.SetFillColor(0)
        self.c = ROOT.TCanvas("c", "Flux, Fill " +   str(self.fillno) , 800, 800)
        self.c.Divide(2,2)
        
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
                self.fluxGraphs[id].GetXaxis().SetTimeFormat(self.timeFormat)
                self.fluxGraphs[id].GetXaxis().SetTimeDisplay(1)    
                
        self.c.Update()             
