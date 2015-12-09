#!/usr/bin/env python

"""
Add running sum 

"""

import sys, os
import ROOT
import math

fills = [4538]

#fills = [  3960, 3962, 3965, 3971, 3974, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257,  4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467,4476, 4477, 4479, 4485, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4560, 4562, 4565, 4569]

inputPattern = '/afs/cern.ch/work/g/grandr/Bril/Data/RadMonData/RadmonFills/radmon__XXX__.root'
outputPattern = '/afs/cern.ch/work/g/grandr/Bril/Data/RadMonData/RadmonFillsRunningSums/radmonSums__XXX__.root'

refIndx = 5   # PFIB used to find beginning of the collisions
rateCut = 10.  # If rate higher than this value, collisions started 

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
};")
from ROOT import FillData  

ROOT.gROOT.ProcessLine(\
"struct RadmonData{\
    Int_t tstamp;\
    Int_t status[16];\
    Double_t rates[16];\
    Double_t rsums15[16];\
    Double_t rsums30[16];\
    Double_t rsums60[16];\
};")

from ROOT import RadmonData

def addRunningSum():
    
    for fill in fills:
        
        inputFile = inputPattern.replace('__XXX__', str(fill))
        try:
            fin = ROOT.TFile(inputFile,'READ')
            print "Processing fill", fill
        except IOError:
            print "Cannot open file", inputFile
            continue
        
        inputTree = fin.Get('t')
        
       
        outfile = outputPattern.replace('__XXX__', str(fill))
        try:
	    fout = ROOT.TFile(outfile,'RECREATE')
	except IOError:
	    print "Cannot open file for output", outfile
	    continue       
        
        #Output tree
        fillData = FillData()
        radmonData = RadmonData()
        t = ROOT.TTree('t', "Radmon rates + runnning sums ")
	t.Branch('fillBranchI', fillData, 'fill/I:fillStart/I:fillColl/I:fillStable/I:fillEnd/I:durationStable/I')
	t.Branch('fillBranchD', ROOT.AddressOf(fillData, 'bField'), 'bField/D:beamEnergy/D')
	t.Branch('radmonBranchI', radmonData, 'tstamp/I:status[16]/I')
	t.Branch('radmonRates', ROOT.AddressOf(radmonData, 'rates'), 'rates[16]/D:rsums15[16]/D:rsums30[16]/D:rsums60[16]/D')

        rsums15 = [0.]*16
        rsumsPrev15 = [0.]*16
        rsums30 = [0.]*16
        rsumsPrev30 = [0.]*16
        rsums60 = [0.]*16
        rsumsPrev60 = [0.]*16
        
        # First pass is to find beginning of the collisions
        tsColl = -100000
        
        for i in range(0, inputTree.GetEntries()):
            nb = inputTree.GetEntry(i)
	    if nb < 0:
		continue
            
            if inputTree.rates[refIndx] > rateCut:
                tsColl = inputTree.tstamp
                break
        
        for i in range(0, inputTree.GetEntries()):
            nb = inputTree.GetEntry(i)
	    if nb < 0:
		continue
            
            #Copy data to a new tree
            fillData.fill = inputTree.fill
            fillData.fillStart = inputTree.fillStart
            fillData.fillColl = tsColl
            fillData.fillStable = inputTree.fillStable
            fillData.fillEnd = inputTree.fillEnd
            fillData.durationStable = inputTree.durationStable
            fillData.bField = inputTree.bField
            fillData.beamEnergy = inputTree.beamEnergy
            
            radmonData.tstamp = inputTree.tstamp
            
            for j in range(0, 16):
                radmonData.status[j] = inputTree.status[j]
                radmonData.rates[j] = inputTree.rates[j]
                
                #Running sums (c) AK
                # 15 minutes
                if i+1 < 15*60:
                    rsums15[j] += inputTree.rates[j]
                    radmonData.rsums15[j] = rsums15[j]
                    rsumsPrev15[j] = rsums15[j]
                else:
                    rsums15[j] = ((15*60 - 1)*rsumsPrev15[j] + inputTree.rates[j])/15/60
                    radmonData.rsums15[j] = rsums15[j]
                    rsumsPrev15[j] = rsums15[j]

                 # 30 minutes
                if i+1 < 30*60:
                    rsums30[j] += inputTree.rates[j]
                    radmonData.rsums30[j] = rsums30[j]
                    rsumsPrev30[j] = rsums30[j]
                else:
                    rsums30[j] = ((30*60 - 1)*rsumsPrev30[j] + inputTree.rates[j])/30/60
                    radmonData.rsums30[j] = rsums30[j]
                    rsumsPrev30[j] = rsums30[j]

                 # 60 minutes
                if i+1 < 60*60:
                    rsums60[j] += inputTree.rates[j]
                    radmonData.rsums60[j] = rsums60[j]
                    rsumsPrev60[j] = rsums60[j]
                else:
                    rsums60[j] = ((60*60 - 1)*rsumsPrev60[j] + inputTree.rates[j])/60/60
                    radmonData.rsums60[j] = rsums60[j]
                    rsumsPrev60[j] = rsums60[j]
                        
            
            t.Fill()
            
        fout.Write()
        fout.Close()
        
        del fillData
        del radmonData
        del t
        del fout   
        del inputTree
        del inputFile
            
            
 
#===========================================================
if __name__ == "__main__":
    addRunningSum()
    
