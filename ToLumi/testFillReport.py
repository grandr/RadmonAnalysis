#!/usr/bin/env python
"""
Testing class FillReport
"""

import os, sys
from fillReport import *

def main():
    
    fills = FillReport("FillReport_1446656923991.xls")
    
    while 1:
        fillNo = raw_input("Enter fill number: ")
    
        print "Fill ", fillNo
        print "Creation ts ", fills.getFillCreationTime(fillNo)
        print "StableBeams ts ", fills.getFillStableTime(fillNo)
        print "Duration ", fills.getFillDuration(fillNo)
        print "Magnetic field ", fills.getFillField(fillNo)
        print 

if __name__=="__main__":
    main()
    

    