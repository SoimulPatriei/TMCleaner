#!/usr/bin/env python

"""Train a Fastalign model and use the model to obtain the alignments."""
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
import time
import Parameters



class MergeLine :
   """Merge the Forward and Backward Alignments ."""
   
   
   def terminate (self,terminator) :
      """Terminate the process. It does not work on Linux"""
      
      self.stdin.write(terminator)
   
   def run (self,alignments) :
      """Run merge program with a forward and backward alignment."""
      
      self.stdin.write(alignments)
      outputLine=self.stdout.readline().rstrip()
      return outputLine
   
   def getCommand(self):
    """Get the command to be used in alignment."""
        
    cList=["java" ,"-cp",self.javaCP,self.javaClass]
    command=" ".join(cList)
    return command
   
   def construct(self,command):
      """Construct the fastalign with the command as parameter """
      
      master, slave = pty.openpty()
      self.merge = subprocess.Popen(command,shell=True,preexec_fn=os.setsid,stdin=PIPE,stdout=slave)
      self.stdin = self.merge.stdin
      self.stdout = os.fdopen(master)
   
   def __init__(self, javaCP,javaClass):
      self.javaCP=javaCP
      self.javaClass=javaClass
      command=self.getCommand()
      self.construct(command)


class FastAlignLine:
   """Load a Fast Align model and align a line"""
   
   def construct(self,command):
      """Construct the fastalign with the command as parameter """
      
      master, slave = pty.openpty()
      self.fa = subprocess.Popen(command,shell=True,preexec_fn=os.setsid,stdin=PIPE,stdout=slave)
      self.stdin = self.fa.stdin
      self.stdout = os.fdopen(master)
   
   def getCommand(self):
    """Get the command to be used in alignment."""
        
    cList=[self.pDict["fa.path"],self.pDict[self.direction],
           "-f",self.modelFile,"-b 0","-i","/dev/stdin"]
    command=" ".join(cList)
    return command
    
    
   def run (self,tokString) :
      """Run  Fastalign with a bisegment to be aligned"""
      
      self.stdin.write(tokString)
      outputLine=self.stdout.readline().rstrip()
      return outputLine
     
   def __init__(self, direction,modelFile):
      self.pDict = Parameters.readParameters(FastAlign.pFile)
      self.modelFile=modelFile
      self.direction=direction
      command=self.getCommand()
      self.construct(command)


class FastAlign:
   """Train a Fastalign model and use the model to obtain the alignments."""
   
   pFile="Parameters/p-FastAlign.txt"
   
   
   
   def train(self,direction):
    """Execute the training command to build a "bin" model."""
    
    cList=[self.pDict["fa.path"],self.pDict[direction],
           "-p",self.modelFile,"-i",self.tokFile]
    command=" ".join(cList)
    call(command, shell=True)

   def align(self,direction):
    """Execute the alignment command based on a model."""
        
    cList=[self.pDict["fa.path"],self.pDict[direction],
           "-f",self.modelFile,"-i",self.tokFile ,">"+self.alignFile]
    command=" ".join(cList)
    call(command, shell=True)
    
    
    
   def __init__(self, tokFile,modelFile,alignFile=None):
      self.pDict = Parameters.readParameters(FastAlign.pFile)
      self.tokFile = tokFile
      self.alignFile= alignFile
      self.modelFile=modelFile


def testFA (tokFile,modelFile,alignFile) :
   """Test Fast Align in file modality """
   
   #Train Example :
    #   python FastAlign.py Europarl/en-it-sample-FL.txt Europarl/en-it-sample-FL.bin ""
    
    #Align Example :
    #   python FastAlign.py Europarl/en-it-sample-FL.txt Europarl/en-it-sample-FL.bin Europarl/en-it-sample-FL.align.txt
   
   fa=FastAlign(tokFile,modelFile,alignFile)
    
   if alignFile :
      print "Align Using the Model=>"+modelFile
      fa.align("fa.flags.forward")
      print "Aligned File =>"+alignFile
   else :
      print "Train a Fast Align Model"
      fa.train("fa.flags.forward")
      print "Model File in =>"+modelFile

   
def testFALine () :
   
   
   """Test Fast Align in line modality."""
   
   print ("===================First Align======================")
   tokString="""What will Donald Trump and his supporters do if he loses a close race to Hillary Clinton ? ||| Quali saranno Donald Trump ei suoi sostenitori fare se perde una corsa vicina a Hillary Clinton?\n"""
   modelForward="AlignmentModels/model-100mil.align.fwd.bin"
   faForward=FastAlignLine("fa.flags.forward",modelForward)
   
   print ("***Forward***")
   aForward=faForward.run(tokString)
   print(aForward)
   
   
   modelBackward="AlignmentModels/model-100mil.align.bwd.bin"
   faBackward=FastAlignLine("fa.flags.backward",modelBackward)
   
   print("***Backward***")
   aBackward=faBackward.run(tokString)
   print(aBackward)
   
   print("===================Second Align========================")
   tokString="""Clinton Is Being Treated for Pneumonia, Doctor Says ||| Clinton e in trattamento per la polmonite, medico dice\n"""
   
   print("Forward")
   aForward=faForward.run(tokString)
   print(aForward)
   
   print("Backward")
   aBackward=faBackward.run(tokString)
   print(aBackward)   


def testMergeLine () :
   """Test Merge Forward and Backward Alignments."""
   
   javaCP="Resources/merge.jar"
   javaClass="symmetrization.mmt.fastalign.MergeAlignmentsLine"
   ml=MergeLine(javaCP,javaClass)
   
   alignment="0-0 0-1 2-2 4-4 4-5 5-6 6-7 7-8@0-0 3-6 4-4 5-6 6-7 7-8\n"
   res=ml.run(alignment)
   print ("Result=>"+res)
   
   #print ("Sleep 30 seconds")
   #time.sleep(30)
   
   res=ml.run(alignment)
   print ("Result=>"+res)
   
   ml.terminate()
   
   
def alignAndMerge() :
   
   """Test Fast Align and merge in line modality."""
   
   print ("Load Merge Line")
   javaCP="Resources/merge.jar"
   javaClass="symmetrization.mmt.fastalign.MergeAlignmentsLine"
   ml=MergeLine(javaCP,javaClass)
   
   print ("===================Load the Forward model======================")
   tokString="""What will Donald Trump and his supporters do if he loses a close race to Hillary Clinton ? ||| Quali saranno Donald Trump ei suoi sostenitori fare se perde una corsa vicina a Hillary Clinton?\n"""
   modelForward="AlignmentModels/model-100mil.align.fwd.bin"
   faForward=FastAlignLine("fa.flags.forward",modelForward)
   
   print ("***Forward***")
   aForward=faForward.run(tokString)
   print(aForward)
   
   print ("===================Load the Backward model======================")
   modelBackward="AlignmentModels/model-100mil.align.bwd.bin"
   faBackward=FastAlignLine("fa.flags.backward",modelBackward)
   
   print("***Backward***")
   aBackward=faBackward.run(tokString)
   print(aBackward)
   
   print("Merge")
   alignment=aForward+"@"+aBackward+"\n"
   res=ml.run(alignment)
   print(alignment)
   
   print("===================Second Align========================")
   tokString="""Clinton Is Being Treated for Pneumonia, Doctor Says ||| Clinton e in trattamento per la polmonite, medico dice\n"""
   
   print("Forward")
   aForward=faForward.run(tokString)
   print(aForward)
   
   print("Backward")
   aBackward=faBackward.run(tokString)
   print(aBackward)
   
   print("Merge")
   alignment=aForward+"@"+aBackward+"\n"
   res=ml.run(alignment)
   print(alignment)
   ml.terminate()

   
def main():
    
    #testFA(sys.argv[1],sys.argv[2],sys.argv[3])
    #testFALine ()
    
    alignAndMerge()
    
    
    
    

if __name__ == '__main__':
  main()    