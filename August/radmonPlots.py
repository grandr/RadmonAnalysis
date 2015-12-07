#!/usr/bin/env python
"""

"""

#
pattern = "HFRadmonData_*.root"
datadir = "/home/grandr/remote/pccms223/scr1/RadMonData/2015/"

import sys, os
from ROOT import *
from xutils import *


class RadmonPlots:
    def __init__ (self):
	print "Creating class RadmonPlots"
	self.start = "2015-07-14 06:50"
	self.stop = "2015-07-14 11:10"
	self.cut = ""
	self.ch =  ROOT.TChain("Rate")
	self.histo = 0
	self.hid = ""

    def SetTimeLimits(self, start, stop):
	self.start = start
	self.stop = stop

    def SetTimeStampCut(self, cut):
	self.cut = cut

    #def SetDateTimeCut(self, tsmin, tsmax):
	#self.tsmin = string(datime2ts(self.start)tsmin
	#self.tsmax = tsmax
	
    def SetHisto(self, hid):
	self.hid = hid
	
    def BookTimeHisto2(self, hid, title, xbins, start, stop, ybins, ymin, ymax):
	self.hid = hid
	xmin = float(datime2ts(start))
	xmax = float(datime2ts(stop))
	self.histo = TH2D(hid, title, xbins, xmin, xmax, ybins, ymin, ymax)

    def MakeChain(self):
	fromto = [None]*2
	fromto[0] = datime2ts(self.start) - 7200
	fromto[1] = datime2ts(self.stop) + 7200
	files = get_filelist(datadir, pattern, fromto)
	for file in files:
	    self.ch.Add(file)
	    
    def Draw(self, exp):
	if self.histo:
	    print exp + ">>" + str(self.hid)
	    self.ch.Draw(exp + ">>" + str(self.hid), self.cut)
	else:
	    self.ch.Draw(exp, self.cut)
