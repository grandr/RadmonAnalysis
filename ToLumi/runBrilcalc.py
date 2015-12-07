#!/usr/bin/env python
"""
# Run briclac for specified fills
# -*- coding: UTF-8 -*-
"""

import sys, os
import re

# Zero output
         #[4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467, 4476, 4477, 4479, 4485, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4560, 4562, 4565, 4569]

fills = [3960, 3962, 3965, 3971, 3974, 3976, 3981, 3983, 3986, 3988, 3992, 3996, 4001, 4006, 4008, 4019, 4020, 4201, 4205, 4207, 4208, 4210, 4211, 4212, 4214, 4219, 4220, 4224, 4225, 4231, 4243, 4246, 4249, 4254, 4256, 4257, 4266, 4268, 4269, 4322, 4323, 4332, 4337, 4341, 4342, 4349, 4356, 4360, 4363, 4364, 4376, 4381, 4384, 4386, 4391, 4393, 4397, 4398, 4402, 4410, 4418, 4420, 4423, 4426, 4428, 4432, 4434, 4435, 4437, 4440, 4444, 4448, 4449, 4452, 4455, 4462, 4463, 4464, 4466, 4467, 4476, 4477, 4479, 4485, 4495, 4496, 4499, 4505, 4509, 4510, 4511, 4513, 4518, 4519, 4522, 4525, 4528, 4530, 4532, 4536, 4538, 4540, 4545, 4555, 4557, 4560, 4562, 4565, 4569]

normtag = '/afs/cern.ch/user/c/cmsbril/public/normtag_json/OfflineNormtagV1Sept28.json'
outdir = '/afs/cern.ch/work/g/grandr/Bril/Brilcalc/FillCsv/'

commandPattern = "brilcalc lumi --tssec --normtag __NORMTAG__ --byls -f __FILL__ -o __OUTDIR__fill__FILL__.csv"

def main():
    
    for fill in fills:
        command = commandPattern.replace('__FILL__', str(fill)).replace('__NORMTAG__', normtag).replace('__OUTDIR__', outdir)
        
        print "Processing fill " + str(fill) + "..."
        os.system(command)   

    print len(fills), " processed"        

if __name__=="__main__":
    main()
