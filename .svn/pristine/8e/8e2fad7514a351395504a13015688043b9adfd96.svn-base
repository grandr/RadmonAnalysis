#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Fetch instant lumi  data from Oracle and store this info in root files
"""

import sys, os
from xconfig import *
from xutils import *
import cx_Oracle
from datetime import *
import time
from ROOT import TTree, TFile, AddressOf, gROOT


gROOT.ProcessLine(\
    "struct LumiData{\
    Int_t fill;\
    Int_t run;\
    Int_t lsNo;\
    Int_t nb4;\
    Int_t tstamp;\
    Int_t msecs;\
    Int_t lsStart;\
    Int_t lsStartMs;\
    Int_t lsEnd;\
    Int_t lsEndMs;\
    Int_t bunchSpacing;\
    Double_t lsLumi;\
    Double_t bestLumi;\
    Double_t hfLumi;\
    Double_t pltZeroLumi;\
    Double_t pltLumi;\
    Double_t bcmfLumi;\
};")


from ROOT import LumiData

def main():
    
    # Get environment
    cfg = Config()
    lumiprefix = cfg.get_option('Env', 'lumiprefix')
    fills = cfg.get_option('Env', 'fills').split(',')

    time_zone = cfg.get_option('Misc', 'time_zone')
    dbtime_format = cfg.get_option('DB', 'dbtime_format')
    connstr = cfg.get_option('DB', 'connstr')
    qtemplate = cfg.get_option('DB', 'qtemplate')
    
    #os.environ['TZ'] = time_zone
    del cfg


    #Connect to DB
    conn = cx_Oracle.connect(connstr)
    curs = conn.cursor()
    #fills = [3960, 3962, 3965, 3971, 3974, 3976, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257, 4266, 4268, 4269, 4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467, 4476, 4477, 4479, 4485, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4560, 4562, 4565, 4569]

    #Loop over the fills
    for fill in fills:

	#DB query
	query = qtemplate
	query = query.replace('__XXX__', str(int(fill)))


	#print "Using query ", query
	print "Procesing fill", int(fill)
	
	rootfile = lumiprefix + str(int(fill)) + '.root'

	f = TFile(rootfile,'RECREATE')
	t = TTree('t','Lumi Data')
	lumiData = LumiData()
	
	t.Branch('IntBranch', lumiData, 'fill/I:run/I:lsNo/I:nb4/I:tstamp/I:msecs/I:lsStart/I:lsStartMs/I:lsEnd/I:lsEndMs/I:bunchSpacing/I')
	t.Branch('DblBranch',  AddressOf(lumiData, 'lsLumi'), 'lsLumi/D:bestLumi:hfLumi:pltZeroLumi:pltLumi:bcmfLumi')
	
	curs.execute(query)
	
	started = 0
	
	for row in curs:
            ##Ugly!!! Gotta think of something better
            #try:
                #limit = float(row[7])
            #except:
                #print row[7]
                #limit = -1.
                
            #if limit > 5.:
                #started = 1
                
            #if  not started:
                #continue
            
            lumiData.fill = int(row[0])
            lumiData.run = int(row[1])
            lumiData.lsNo = int(row[2])
            lumiData.nb4 = int(row[3])
            lumiData.tstamp = int(row[4].strftime("%s"))
            lumiData.msecs = int(row[4].strftime("%f"))
            lumiData.bestLumi = float(row[8])
            #for some fills lsLumi is None
            try:
                lsLumi = float(row[7])
            except TypeError:
                lsLumi = -1.
            lumiData.lsLumi = lsLumi
            lumiData.hfLumi = float(row[9])
            lumiData.bcmfLumi = float(row[10])
            lumiData.pltZeroLumi = float(row[11])
            lumiData.pltLumi = float(row[12])
            lumiData.lsStart = int(row[5].strftime("%s"))
            lumiData.lsStartMs = int(row[5].strftime("%f"))
            lumiData.lsEnd = int(row[6].strftime("%s"))
            lumiData.lsEndMs = int(row[6].strftime("%f"))
            
            scheme = row[13].split('_')
            try:
                lumiData.bunchSpacing = int(scheme[0].strip('ns'))
            except:
                lumiData.bunchSpacing = -1
  
	    t.Fill()
	
	f.Write()
	f.Close()
	del query
	del t
	del f
	del lumiData

if __name__=="__main__":
  main()
  
    
    
    
