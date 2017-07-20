#!/usr/bin/env python

"""For the moment here is the function that reads the parameters."""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import codecs
import re

def readParameters (fileParameters) :
    fp = codecs.open(fileParameters, "r", "utf-8")
    pDict={}
    for lineSegment in fp:
        if lineSegment.startswith('#') :
            pass
        else :
            lineSegment=lineSegment.rstrip()
            if re.search ("\t",lineSegment) :
                argument,value=lineSegment.split("\t")
                pDict[argument]=value
    return pDict


def main():
    
    fileParameters="Parameters/Server/Fastalign/p-Batch-Italian.txt"
    pDict=readParameters(fileParameters)
    print ("Here")
    


if __name__ == '__main__':
  main()