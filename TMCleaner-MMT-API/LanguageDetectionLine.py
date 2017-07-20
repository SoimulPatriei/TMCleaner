#!/usr/bin/env python

"""Language Detection for bisegments"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"


import subprocess
from subprocess import Popen, PIPE, STDOUT
import pty
import os
import time

class LanguageDetectionLine :
   """Language Detection for Bisegments"""
   
   
   def terminate (self,terminator) :
      
      self.stdin.write(terminator)
   
   def run (self,sourceSegment,targetSegment) :
      """Run merge program with a forward and backward alignment."""
      
      tu=sourceSegment+"@#@"+targetSegment+"\n"
      self.stdin.write(tu)
      outputLine=self.stdout.readline().rstrip()
      return outputLine
   
   def getCommand(self):
    """Get the command to be used in alignment."""
        
    commandList=["java","-cp",self.pDict["javaClassPath"],self.pDict["javaClassLine"],self.pDict["langProfileDirectory"]]
    command=" ".join(commandList)
    return command

   def construct (self,command) :
    """Construct the Language Detector"""
    
    master, slave = pty.openpty()
    self.ld = subprocess.Popen(command,shell=True,preexec_fn=os.setsid,stdin=PIPE,stdout=slave)
    self.stdin = self.ld.stdin
    self.stdout = os.fdopen(master)
 
   
   def __init__(self, pDict):
      self.pDict=pDict
      command=self.getCommand()
      self.construct(command)
 
 
def testLD () :
    """Test the Language Detection ."""
    
    sourceSegment="Clinton Is Being Treated for Pneumonia, Doctor Says"
    targetSegment="Clinton e in trattamento per la polmonite, medico dice"
    
    pDict ={"javaClassPath":"Resources/idLanguage.jar",
            "javaClassLine":"test.translated.net.DetectLanguageString",
            "langProfileDirectory":"Resources/profiles.sm"}
    
    ldl=LanguageDetectionLine(pDict)
    print(ldl.run(sourceSegment,targetSegment))
    
    print(ldl.run(sourceSegment,targetSegment))
    
    ldl.terminate()
    
      
def main():
    """Construct and call the programs."""
    
    testLD()
    
    
if __name__ == '__main__':
  main()        
    
      
      
      