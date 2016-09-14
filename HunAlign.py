#!/usr/bin/env python

"""Run Hunalign and add the Hunalign Features to the computed features"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import codecs
import collections
import re
from subprocess import call
from os.path import split ,join
import Parameters


class HunAlign:
   """Run HunAlign and add the HunAlign Features to the computed features"""
   
   fHunParameters="Parameters/p-HunAlign.txt"
   
   
   def getAlignerFiles(self):
    """Get the Aligner Input Files: Source File and Target File."""
    
    fSource=re.sub(".txt","",self.pDict['segmentsFile'])
    fSource+="-Source.txt"
    
    fTarget=re.sub(".txt","",self.pDict['segmentsFile'])
    fTarget+="-Target.txt"
    
    fAlignment=re.sub(".txt","",self.pDict['segmentsFile'])
    fAlignment+="-Aligned.txt"
    
    return fSource,fTarget,fAlignment
    
   def performAlignment(self):
    
    """Perform the Sentence Alignment with HunAlign"""
    
    pHunDict=Parameters.readParameters ()
    pHunDict['fileS'],pHunDict['fileT'],self.pDict['fAlignment']=self.getAlignerFiles()
    self.pDict['fAlignment']=self.getFAPath(pHunDict)
    
    self.writeContent(self.pDict['segmentsFile'],pHunDict['fileS'],pHunDict['fileT'])
    self.runAligner(pHunDict,self.pDict['fAlignment'])
   
    
    return self.pDict['fAlignment']
     
   def writeContent(self,fSeed,fSource,fTarget):
    """Write Content for Source and Target Alignment """
    
    fi = codecs.open(fSeed, "r", "utf-8")
    fs = codecs.open(fSource, "w", "utf-8")
    ft = codecs.open(fTarget, "w", "utf-8")
    
    for line in fi:
        line=line.rstrip()
        components=line.split("@#@")
        fs.write(components[2]+"\n")
        ft.write(components[3]+"\n")
    
    
    fi.close()
    fs.close()
    ft.close()

   def runAligner(self,pHunDict,fAlignment):
    """Run the Aligner..."""
    
    fo = codecs.open(fAlignment, "w", "utf-8")
    arguments=[pHunDict["fileProgram"],pHunDict["fileDictionary"], pHunDict['fileS'],pHunDict['fileT']]
    runString=" ".join(arguments)
    print (runString)
    call(arguments,stdout=fo)
    fo.close()
    
   def getFAPath (self,pHunDict) :
    """Get the file alignment path."""
    
    path, fileSL = split(pHunDict["fileS"])
    path, fileDL = split(pHunDict["fileT"])
    
    fileST=re.sub(".txt","",fileSL)+"-"+re.sub(".txt","",fileDL)+"-Aligned.txt"
    fileSTPath=join(path,fileST)
    
    return fileSTPath
      
   def readAlignmentScores(self):
    
    """Read Alignment Scores"""
    
    scoreD={}
    fi =codecs.open(self.pDict['fAlignment'], "r", "utf-8")
    for line in fi:
        line=line.rstrip()
        id1,id2,score=line.split("\t")
        if id1==id2 :
            scoreD[str(id1)+"-"+str(id2)]=float(score)
    fi.close()
    
    return scoreD

   def addFeatures(self,segmentFeaturesDict) :
      self.performAlignment()
      scoreD=self.readAlignmentScores()
      for key in segmentFeaturesDict:
          if key in scoreD :
             segmentFeaturesDict[key]["hunascore"]=scoreD[key]
          else :
              segmentFeaturesDict[key]["hunascore"]=0
 
   def __init__(self,pDict):
    self.pDict=pDict
    
   
   
   
   
    
def main():
   
    pDict=Parameters.readParameters("Parameters/p-Training.txt")
    pDict["segmentsFile"]="Training/full-English-Italian-Category-segments.txt"
    
    ha=HunAlign(pDict)
    fAlignment=ha.performAlignment()
    print "Output->"+fAlignment
    
    
    
    
   

if __name__ == '__main__':
  main()    