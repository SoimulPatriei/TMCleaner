#!/usr/bin/env python

"""Train a Fastalign model and use the model to obtain the alignments."""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import codecs
import collections
import re
from subprocess import call


class FastAlign:
   """Train a Fastalign model and use the model to obtain the alignments."""
   
   pFile="Parameters/p-FastAlign.txt"
   
   def readParameters (self,pFile) :
    """Read tokenization parameters"""
    
    fp = codecs.open(pFile, "r", "utf-8")
    pDict={}
    for lineSegment in fp:
        lineSegment=lineSegment.rstrip()
        if re.search ("\t",lineSegment) :
            argument,value=lineSegment.split("\t")
            pDict[argument]=value
    return pDict
   
   
   def train(self,direction):
    """Execute the training command to build a "bin" model."""
    
    cList=[self.pDict["fa.path"],self.pDict[direction],
           "-p",self.modelFile,"-i",self.tokFile]
    command=" ".join(cList)
    print(command)
    call(command, shell=True)

   def align(self,direction):
    """Execute the alignment command based on a model."""
        
    cList=[self.pDict["fa.path"],self.pDict[direction],
           "-f",self.modelFile,"-i",self.tokFile ,">"+self.alignFile]
    command=" ".join(cList)
    print(command)
    call(command, shell=True)
    
    
    
   def __init__(self, tokFile,modelFile,alignFile=None):
      self.pDict = self.readParameters(FastAlign.pFile)
      self.tokFile = tokFile
      self.alignFile= alignFile
      self.modelFile=modelFile
   

def main():
    
    #Train Example :
    #   python FastAlign.py Europarl/en-it-sample-FL.txt Europarl/en-it-sample-FL.bin ""
    
    #Align Example :
    #   python FastAlign.py Europarl/en-it-sample-FL.txt Europarl/en-it-sample-FL.bin Europarl/en-it-sample-FL.align.txt
    
    tokFile=sys.argv[1]
    modelFile=sys.argv[2]
    alignFile=sys.argv[3]
    
    
    fa=FastAlign(tokFile,modelFile,alignFile)
    
    if alignFile :
        print "Align Using the Model=>"+modelFile
        fa.align("fa.flags.forward")
        print "Aligned File =>"+alignFile
    else :
        print "Train a Fast Align Model"
        fa.train("fa.flags.forward")
        print "Model File in =>"+modelFile
    
    
    
    

if __name__ == '__main__':
  main()    