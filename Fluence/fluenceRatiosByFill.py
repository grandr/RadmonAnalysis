#!/usr/bin/env python
"""
Make stustical distributions of neutrons per ub^1

Usage (at root prompt)
TPython::LoadMacro("fluenceRatiosByFill.py");
FluenceRatios p;
p.fillHistos();
p.drawHisto("mfit")

"""

import sys, os
sys.path.append("../Utils/")
from ROOT import *
from xutils import *
from xconfig import *
from fillReport import *
import time
from datetime import datetime
from dateutil import tz
os.environ['TZ'] = 'Europe/Zurich'

#2015
radmonFilePattern = '/home/data/RadMonData/RadmonFills/2015/radmon__XXX__.root'
# Fills to use
fills = [ 3960, 3962, 3965, 3971, 3974,3976, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257, 4266, 4268, 4269, 4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467,4476, 4477, 4479, 4485, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4562, 4565] 
         #4560, 4569]
fillReportFile = '../Config/FillReport_1446656923991.xls'
         
##2016
#radmonFilePattern = '/home/data/RadMonData/RadmonFills/2016/radmon__XXX__.root'
## Fills to use
#fills = [4888, 4889, 4890, 4892, 4895, 4896, 4905, 4906, 4910, 4915, 4919, 4924, 4925, 4926, 4930, 4935, 4937, 4942, 4945, 4947, 4953, 4954, 4956, 4958, 4960, 4961, 4964, 4965, 4976, 4979, 4980, 4984, 4985, 4988, 4990, 5005, 5013, 5017, 5020, 5021, 5024, 5026, 5027, 5028, 5029, 5030, 5038, 5043, 5045, 5048, 5052]

#fills = [4990, 5024, 5026, 5027,]
#fillReportFile = '../Config/FillReport.xls'

nBins = 100
xmax = 0.

minPeakInstLumi = 10.
minBfield = 3.6
deltaT = 2400

rateOn = 100000  # Cut for detector turned on
rateColl = 100   # collisions


class FluenceRatios:
    
    def __init__(self):
       
        cfg = Config('../Config/detectors.ini')
        dummy = cfg.get_option('Detectors')
        self.indx = {}
        self.calib = {}
        for key in dummy.keys():
            if 'XX' in key.upper():
                continue
            tmp = dummy[key].split()
            self.indx[key] = int(tmp[0])
            self.calib[key] = float(tmp[2])
        del dummy
        
        self.fillReport = FillReport(fillReportFile)
        
        #Book histos
        self.histos = {}
        for key in self.indx.keys():
            self.histos[key] = ROOT.TH1D(key, key.upper(), nBins, 0., xmax)
            
    def fillHistos(self):
        
        for fill in fills:
                # Fill cuts
            if self.fillReport.getFillPeakInstLumi(fill) < minPeakInstLumi:
                print "Low FillPeakInstLumi for fill", fill
                continue
            if self.fillReport.getFillField(fill) < minBfield:
                print "Low magnetic field for fill", fill
                continue       
            if self.fillReport.getFillDuration(fill) < deltaT:
                print "Short fill", fill
                continue
            
            tsEnd = self.fillReport.getFillEndTime(fill)
            tsStable = self.fillReport.getFillStableTime(fill)
            

            inputFile = radmonFilePattern.replace('__XXX__', str(fill))
            try:
                fin = ROOT.TFile(inputFile,'READ')
            except IOError:
                print "Cannot open file", inputFile
                continue

            t = fin.Get("t")             
            print "Processing fill", fill
            
            tsPrev = -1000
            
            sums = {}
            for key in  self.indx.keys():
                sums[key] = 0.
            
            for i in range(0, t.GetEntries()) :
                nb = t.GetEntry(i)
                if nb < 0:
                    continue
            
                if tsPrev < 0:
                    tsPrev = t.tstamp
                    continue
            
                if  t.tstamp < tsStable:
                    continue
                
                if t.tstamp > tsEnd:
                    break
            
                for key in self.indx.keys():
                    sums[key] += t.rates[self.indx[key]] * (t.tstamp - tsPrev)
                
                
            
            lumi = self.fillReport.getFillDeliveredLumi(fill)
            for key in self.indx.keys():
                self.histos[key].Fill(sums[key]*self.calib[key]/lumi)
                
            del inputFile
            del fin
            del t

    def drawHisto(self, key):
        #detector = str(key).lower()
        print key
        self.histos[key.lower()].Draw()
        
