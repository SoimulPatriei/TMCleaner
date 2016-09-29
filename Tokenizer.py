#!/usr/bin/env python


"""Tokenize using MMT tokenizer before using Fastalign"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import codecs
import collections
import re
from subprocess import call
import subprocess
from subprocess import Popen, PIPE, STDOUT
import pty
import os
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
    call(command, shell=True)

    
    
   def __init__(self, inFile,outFile,mmtLang=None):
      self.pDict = Parameters.readParameters(Tokenizer.pFile)
      self.inFile = inFile
      self.outFile= outFile
      self.mmtLang=mmtLang


class TokenizerLine:
   """Apply tokenization using the mmt tokenizers to a line of text."""
   
   pFile="Parameters/p-Tokenizer.txt"
   
   def construct(self,command):
      """Construct the tokenizer using the command passed as parameter"""
      
      master, slave = pty.openpty()
      self.tokenizer = subprocess.Popen(command,shell=True,preexec_fn=os.setsid,stdin=PIPE,stdout=slave)
      self.stdin = self.tokenizer.stdin
      self.stdout = os.fdopen(master)
   
   def run (self,string) :
      """Run  the Tokenizer with a string to be tokenized"""
      
      self.stdin.write(string)
      outputLine=self.stdout.readline().rstrip()
      return outputLine
   
    
   def getCommand (self) :
      """Construct the mmt tokenizer command """
      
      cList=["java", "-Dmmt.home="+self.pDict["mmt.home"],
          self.pDict["tok.class"],self.pDict["tok.flags"]]
      if self.mmtLang :
        cList.extend(["--lang",self.mmtLang])
        
      command=" ".join(cList)
      return command
   
    
   def __init__(self,mmtLang=None):
      self.pDict = Parameters.readParameters(Tokenizer.pFile)
      self.mmtLang=mmtLang
      command=self.getCommand()
      self.construct(command)

      
def testTokenizer () :
    """Test the Tokenizer on files"""
    
    inFile=sys.argv[1]
    outFile=sys.argv[2]
    mmtLang=sys.argv[3]
    tokenizer=Tokenizer(inFile,outFile,mmtLang)
    
    print "Execute the Tokenizer"
    tokenizer.execute()
    print "Result in out file =>"+outFile

def testTokenizerLine () :
    """Test the Tokenizer on simple lines"""
    
    mmtLang="en" 
    tokenizer=TokenizerLine(mmtLang)
    print "Execute the Tokenizer"
    string="What will Donald Trump and his supporters do if he loses a close race to Hillary Clinton?\n"
    tokLine=tokenizer.run(string)
    print "Tokenized Line =>"+tokLine
    

    print "Again"
    string="""The Center for Economic Studies (CES), which is an independent institute within the Faculty of Economics of the University of Munich,
    invites visiting scholars to conduct their research in Munich, Germany, and to give a lecture series in return.\n"""
    tokLine=tokenizer.run(string)
    print "Tokenized Line =>"+tokLine
    

def main():
    
    testTokenizerLine()
    
    
if __name__ == '__main__':
  main()    