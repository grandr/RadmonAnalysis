#!/usr/bin/env python
"""
Decode FillReport*.xls file
Fields of interest
0   Fill No
1   Create time
2   Duration stable
3   Magnetic Field
11  Beginning of the stable beams 
13  End time
20  Number of colliding bunches
23  Injection scheme
24  Runs
"""

import sys, os
from xutils import *

class FillReport:
    
    def __init__(self, fileName):
        
        self.fillData = {}
        try:
            file = open(fileName, 'r')
        except:
            exit(-1)
        
        for line in file.readlines():
            
            buff = line.split('\t')
            try:
                fillNo = int(buff[0].strip())
            except ValueError:
                continue
        
            self.fillData[buff[0].strip()] = buff
        #print self.fillData.keys()
            
    def getFillCreationTime(self, fillNo = None):
        """
        Returns timestamp for fill creation time.
        If fillNo not specified returns dictionary for all fills
        """
        if fillNo is None:
            tsCreation = {}
            for fill in self.fillData.keys():
                tsCreation[key] = datime2tsDot(self.fillData[key][1].strip())
            return tsCreation
        else:
            return datime2tsDot(self.fillData[str(fillNo)][1].strip())

    def getFillStableTime(self, fillNo = None):
        """
        Returns timestamp for beginning of the Stable Beams.
        If fillNo not specified returns dictionary for all fills
        """
        if fillNo is None:
            tsStable = {}
            for fill in self.fillData.keys():
                tsStable[key] = datime2tsDot(self.fillData[key][11].strip())
            return tsStable
        else:
            return datime2tsDot(self.fillData[str(fillNo)][11].strip())
 
    def getFillEndTime(self, fillNo = None):
        """
        Returns timestamp for end of fill.
        If fillNo not specified returns dictionary for all fills
        """
        if fillNo is None:
            tsEnd = {}
            for fill in self.fillData.keys():
                tsEnd[key] = datime2tsDot(self.fillData[key][13].strip())
            return tsEnd
        else:
            return datime2tsDot(self.fillData[str(fillNo)][13].strip())
 
    def getFillDuration(self, fillNo = None):
        """
        Returns fill duration in seconds.
        If fillNo not specified returns dictionary for all fills
        """
        if fillNo is None:
            dt = {}
            for fill in self.fillData.keys():
                hours, dummy, minutes, dummy = self.fillData[key][2].strip().split()
                dt[key] = int(minutes) * 60 + int(hours) * 3600 
            return dt
        else:
            hours, dummy, minutes, dummy = self.fillData[str(fillNo)][2].strip().split()
            return int(minutes) * 60 + int(hours) * 3600 
    
    def getFillField(self, fillNo = None):
        """
        Return magnetic field
        """
        if fillNo is None:
            bfield = {}
            for fill in self.fillData.keys():
                bfield[key] = float(self.fillData[key][3].strip())
                return bfield
        else:
            return float(self.fillData[str(fillNo)][3].strip())
        
    def getFillBeamEnergy(self, fillNo = None):
        """
        Return beam energy
        """
        if fillNo is None:
            beam = {}
            for fill in self.fillData.keys():
                beam[key] = float(self.fillData[key][15].strip())
                return beam
        else:
            return float(self.fillData[str(fillNo)][15].strip())
 
    def getFillPeakInstLumi(self, fillNo = None):
        """
        Return fill instant lumi
        """
        if fillNo is None:
            instLumi = {}
            for fill in self.fillData.keys():
                try:
                    instLumi[key] = float(self.fillData[key][4].strip())
                except:
                    instLumi[key] = 0
                return instLumi
        else:
            try:
                return float(self.fillData[str(fillNo)][4].strip())
            except:
                return 0
 
    def getFillDeliveredLumi(self, fillNo = None):
        """
        Return fill instant lumi
        """
        if fillNo is None:
            delLumi = {}
            for fill in self.fillData.keys():
                try:
                    delLumi[key] = float(self.fillData[key][7].strip())
                except:
                    deltLumi[key] = 0
                return delLumi
        else:
            try:
                return float(self.fillData[str(fillNo)][7].strip())
            except:
                return 0
        