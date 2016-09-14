#!/usr/bin/env python


"""Tokenize using MMT tokenizer before using Fastalign"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import codecs
import collections
import re
from subprocess import call
import Parameters


class Tokenizer:
   """Apply tokenization using the mmt tokenizers."""
   
   pFile="Parameters/p-Tokenizer.txt"
   
   
   def execute(self):
    """Execute the tokenization command"""
    
    cList=["cat",self.inFile,"|", "java", "-Dmmt.home="+self.pDict["mmt.home"],
          self.pDict["tok.class"],self.pDict["tok.flags"]]
    if self.mmtLang :
        cList.extend(["--lang",self.mmtLang])
    cList.extend([">"+self.outFile])
    command=" ".join(cList)
    print(command)
    call(command, shell=True)

    
    
   def __init__(self, inFile,outFile,mmtLang=None):
      self.pDict = Parameters.readParameters(Tokenizer.pFile)
      self.inFile = inFile
      self.outFile= outFile
      self.mmtLang=mmtLang
   

def main():
    
    inFile=sys.argv[1]
    outFile=sys.argv[2]
    mmtLang=sys.argv[3]
    tokenizer=Tokenizer(inFile,outFile,mmtLang)
    
    print "Execute the Tokenizer"
    tokenizer.execute()
    print "Result in out file =>"+outFile
    
    

if __name__ == '__main__':
  main()    