#!/usr/bin/env python
"""
parse brildaq log file
"""

import sys, os
logFileName = "radmonprocessor160823.log"
#logFileName = "21.log"

lookFor = "Request DIM server"
dataNotReady = "Data not ready!"

previous = {
    "date" : "",
    "fill" : 0,
    "run" : 0,
    "ls" : 0,
    "nb" : 0,
    }

current = {
    "date" : "",
    "fill" : 0,
    "run" : 0,
    "ls" : 0,
    "nb" : 0,
    }


def logParser():

    veryFirst = 1
    nTotal = 0
    nGaps = 0
    notReady = 0


    file = open(logFileName) 
    for line in file.readlines():
        
        if dataNotReady in line:
            notReady += 1
        
        if lookFor in line:
            data = line.split(',')
            fdata= data[0].split()
            #print fdata[-2], fdata[-1], data[1], data[2], data[3]
            #print ' '.join(fdata[0:5])
            
            for i in  range(1,4):
                key,value = data[i].split()
                current[key.strip()] = int(value.strip())
            current["date"] = ' '.join(fdata[0:5])
            
            nTotal += 1
            if veryFirst:
                veryFirst = 0
            else:
                if current['run'] != previous['run']:
                    pass
                else:
                    delta = current['nb'] - previous['nb']
                    if abs(delta) != 4 and abs(delta) != 60:
                        nGaps += 1
                        lPrevious = []
                        lPrevious.append("Previous:\t")
                        lCurrent = []
                        lCurrent.append("Current:\t")
                        for key in current.keys():
                            lCurrent.append(str(key) + ":" + str(current[key]) + ", ") 
                            lPrevious.append(str(key) + ":" + str(previous[key]) + ", ")                            
                        print ' '.join(lPrevious)
                        print ' '.join(lCurrent)
                        print "======"
            for key in current.keys():
                previous[key] = current[key]                    

    print "=============================="
    print "Summary"
    print "No of records:\t\t", nTotal
    print "No of gaps:\t\t", nGaps     
    print "Data not ready:\t\t", notReady


#===========================================================
if __name__ == "__main__": 
    logParser()    
