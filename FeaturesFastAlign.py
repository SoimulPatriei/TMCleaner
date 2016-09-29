#!/usr/bin/env python
#------------------------------------------------------------------------------------
#Compute the Features based on on Fast Align Alignments:
#   1. Apply the Tokenizer from MMT
#   2. Load the trained Fast Align Model and perform Alignment
#   3. Compute the Features based on the Fast Alignment  
#------------------------------------------------------------------------------------


"""Compute features based on on Fastalign alignments """
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"


import sys
import codecs
import collections
import re
from subprocess import call
import os
from Tokenizer import Tokenizer
from FastAlign import FastAlign
from WordMappings import *
import logging


class FeaturesFastAlignLine :
    """Compute Features based on Fastalign alignments for one translation unit given as parameter."""
    
    def getFeatureNames(self):
        """Get Computed features as first line of the file"""
        defaultString="\t".join(["sWordRatio","tWordRatio","smaxOneZone","smaxZeroZone","tmaxOneZone","tmaxZeroZone",
                     "sPositiveZoneRatio","sNegativeZoneRatio","tPositiveZoneRatio","tNegativeZoneRatio"])
        return defaultString
    
    def getDefaultValues(self):
        """Get Default Values of Features when no alignment can be performed"""
        
        nRepeat=len(self.getFeatureNames().split("\t"))
        defValues="\t".join(["0.0"]*nRepeat)
        return defValues
    
    def getAlignmentFeatures (self,sentenceAlignedLine,wordAlignedLine) :
        """Get the alignment features"""
        
        wm=WordMappings(sentenceAlignedLine,wordAlignedLine)
        
        #--------Get The Mapping Dictionary-------
        nbDict,wdMapSir=wm.getMappings()
        strFeatures=""
        if nbDict :
            nSourceTokens,nTargetTokens=wm.getNTokens()
            af=AlignFeatures(nSourceTokens,nTargetTokens,nbDict)
            alignmentDict=af.getAlignmentFeatures()
            for feature in alignmentDict:
                value=round(alignmentDict[feature],2)
                strFeatures+=str(value)+"\t"
            strFeatures=strFeatures.rstrip()
        else :
            strFeatures=self.getDefaultValues()
            
        return strFeatures   
        
    
    def printFeatures (self,featuresDict) :
        """Print some features for testing"""
        
        fString=""
        for feature in featuresDict :
            fString+=feature+":"+str(featuresDict[feature])+"\t"
        
        fString=fString.rstrip()
        print (fString)    
        
        
    
    def addFeatures(self,featuresDict):
        """Add Fast Align Alignment Features to the Feature Dictionary """
        
        sSegment=self.argDict["sourceSegment"]
        tSegment=self.argDict["targetSegment"]
        
        logging.debug("=========Tokenizer for source and target segments============")
        sSegmentTokenized=self.argDict["tokenizerSource"].run(sSegment+"\n")
        tSegmentTokenized=self.argDict["tokenizerSource"].run(tSegment+"\n")
        logging.debug("SSeg Tokenized:"+sSegmentTokenized)
        logging.debug("TSeg Tokenized:"+tSegmentTokenized)
        logging.debug("=========End tokenizer============")
        
        tokString=sSegmentTokenized+" ||| "+tSegmentTokenized
        logging.debug("=========Forward and Backward alignments============")
        aForward=self.argDict["faForward"].run(tokString+"\n")
        aBackward=self.argDict["faBackward"].run(tokString+"\n")
        logging.debug("faForward:"+aForward)
        logging.debug("faBackward:"+aBackward)
        logging.debug("=========End forward and backward alignments============")
        
        logging.debug("=========Merge alignments============")
        alignments=aForward+"@"+aBackward+"\n"
        fAlignment=self.argDict["mergeLine"].run(alignments)
        logging.debug("Final Alignment:"+fAlignment)
        logging.debug("=========Alignments merged============")
        
        featureValues=self.getAlignmentFeatures (tokString,fAlignment)
        featureNames=self.getFeatureNames()
        #logging.debug("Feature Names:"+featureNames)
        #logging.debug("Feature Values:"+featureValues)
        
        fValuesList=[float(i) for i in featureValues.split("\t")] 
        fNamesList=featureNames.split("\t")
        
        for i, name in enumerate(fNamesList) :
            featuresDict[name]=fValuesList[i]
            
        
        #self.printFeatures(featuresDict)
            
        
    
    def __init__(self,argDict,pDict):
        """Processes to run the tokenizer , fastalign with forward and backward models
        and the merge program"""
        
        self.argDict=argDict
        self.pDict = pDict
     

class FeaturesFastAlign:
   """Compute Features based on Fastalign alignments."""
   
   def getSentenceAlignedFile(self):
    """After Tokenization obtain the Fast Align File."""
    
    self.pDict["fSentenceAlignment"]=re.sub("-tok.txt","-"+self.pDict["targetLanguage"]+"-sentenceAlignment.txt",self.pDict["tokFileSource"])
    fs = codecs.open(self.pDict["tokFileSource"], "r", "utf-8")
    ft = codecs.open(self.pDict["tokFileTarget"], "r", "utf-8")
    fw = codecs.open(self.pDict["fSentenceAlignment"], "w", "utf-8")
    
    for lineSource in fs:
        lineSource=lineSource.rstrip()
        lineTarget=ft.readline().rstrip()
        fw.write(lineSource+" ||| "+lineTarget+"\n")
    fs.close()
    ft.close()
    fw.close()
    
    
    def alignForward(self):
        """Align using Fast Align with the Forward Model."""
        
        self.pDict["fWordAlignmentForward"]=re.sub("-sentenceAlignment.txt","-wordAlignmentForward.txt",self.pDict["fSentenceAlignment"])
        fa=FastAlign(self.pDict["fSentenceAlignment"],self.pDict["faForwardModel"],self.pDict["fWordAlignmentForward"])
        fa.align("fa.flags.forward")
    
   
   def alignBackward(self):
        """Align using Fast Align with the Backward Model."""
        
        self.pDict["fWordAlignmentBackward"]=re.sub("-sentenceAlignment.txt","-wordAlignmentBackward.txt",self.pDict["fSentenceAlignment"])
        fa=FastAlign(self.pDict["fSentenceAlignment"],self.pDict["faBackwardModel"],self.pDict["fWordAlignmentBackward"])
        fa.align("fa.flags.backward")
   
   def alignForward(self):
        """Align using Fast Align with the Forward Model."""
        
        self.pDict["fWordAlignmentForward"]=re.sub("-sentenceAlignment.txt","-wordAlignmentForward.txt",self.pDict["fSentenceAlignment"])
        fa=FastAlign(self.pDict["fSentenceAlignment"],self.pDict["faForwardModel"],self.pDict["fWordAlignmentForward"])
        fa.align("fa.flags.forward")
   
   
   def merge(self):
        """Merge the Forward and Backward Aligned files."""
        
        
        commandList=["java" ,"-cp",self.pDict["javaClassPathSym"],self.pDict["javaClassSym"],self.pDict["fWordAlignmentForward"],
                     self.pDict["fWordAlignmentBackward"],self.pDict["fSentenceAlignment"],self.pDict["fWordAlignment"]]
        logging.debug (" ".join(commandList))
        call(commandList)
   
   def runFastAlign(self):
    """After Tokenization obtain the Fast Align File and perform the Alignment using Fast Align."""
    
    self.getSentenceAlignedFile()
    self.pDict["fWordAlignment"]=re.sub("-sentenceAlignment.txt","-wordAlignment.txt",self.pDict["fSentenceAlignment"])
    self.alignForward()
    logging.debug ("------------------------------------------------------------------------------------------------------------")
    self.alignBackward()
    
        
   def populate(self,inFileSource,inFileTarget):
    """Obtain the input files for tokenizer."""
    
    fi = codecs.open(self.fInput, "r", "utf-8")
    fos=codecs.open(inFileSource, "w", "utf-8")
    fot=codecs.open(inFileTarget, "w", "utf-8")
    
    for line in fi:
        line=line.rstrip()
        components=line.split("@#@")
        sSegment=components[2]
        tSegment=components[3]
        fos.write(sSegment+"\n")
        fot.write(tSegment+"\n")
    
    fi.close()
    fos.close()
    fot.close()
    
   def runTokenizer(self):
    """Prepare the Files for the tokenizer"""
    
    inFileSource=re.sub(".txt$","",self.fInput)+"-"+self.pDict["sourceLanguage"]+".txt"
    tokFileSource=re.sub(".txt$","-tok.txt",inFileSource)
    
    inFileTarget=re.sub(".txt$","",self.fInput)+"-"+self.pDict["targetLanguage"]+".txt"
    tokFileTarget=re.sub(".txt$","-tok.txt",inFileTarget)
    
    self.populate(inFileSource,inFileTarget)
    
    tokenizer=Tokenizer(inFileSource,tokFileSource,self.pDict["sourceLanguage"])
    tokenizer.execute()
    
    tokenizer=Tokenizer(inFileTarget,tokFileTarget,self.pDict["targetLanguage"])
    tokenizer.execute()
    
    self.pDict["tokFileSource"]=tokFileSource
    self.pDict["tokFileTarget"]=tokFileTarget
    
    #-----Clean the intermediate Files------
    os.remove(inFileSource)
    os.remove(inFileTarget)
     
   def getDefaultValues(self):
    """Get Default Values of Features when no alignment can be performed"""
    nRepeat=len(self.getFeatureNames().split("\t"))
    defValues="\t".join(["0.0"]*nRepeat) 
    return defValues
    
   def getFeatureNames(self):
    """Get Computed features as first line of the file"""
    
    defaultString="\t".join(["sWordRatio","tWordRatio","smaxOneZone","smaxZeroZone","tmaxOneZone","tmaxZeroZone",
                     "sPositiveZoneRatio","sNegativeZoneRatio","tPositiveZoneRatio","tNegativeZoneRatio"])
    return defaultString


   def debugAlignment(self):
    """Debug an alignment by printing the words aligned in source and target."""
        
    fsa = codecs.open(self.pDict["fSentenceAlignment"], "r", "utf-8")
    fwa=codecs.open(self.pDict["fWordAlignment"], "r", "utf-8")
    fd=codecs.open(self.pDict["fDebug"], "w", "utf-8")
    
    for sentenceAlignedLine in fsa:
        sentenceAlignedLine=sentenceAlignedLine.rstrip()
        wordAlignedLine=fwa.readline().rstrip()
        alignList=wordAlignedLine.split(" ")
        wm=WordMappings(sentenceAlignedLine,wordAlignedLine)
        
        #--------Get The Mapping Dictionary-------
        nbDict,wdMapSir=wm.getMappings()
        fd.write(wdMapSir+"\n")
               
    fsa.close()
    fwa.close()
    fd.close()
    

    
    
   def getFeatureValues(self):
    """Compute the Alignment Features"""
    
    self.pDict["fFeatureAlignment"]=re.sub("-sentenceAlignment.txt","-featureAlignment.txt",self.pDict["fSentenceAlignment"])
    
    fsa = codecs.open(self.pDict["fSentenceAlignment"], "r", "utf-8")
    fwa=codecs.open(self.pDict["fWordAlignment"], "r", "utf-8")
    fo=codecs.open(self.pDict["fFeatureAlignment"], "w", "utf-8")
    
    fo.write(self.getFeatureNames()+"\n") 
    for sentenceAlignedLine in fsa:
        sentenceAlignedLine=sentenceAlignedLine.rstrip()
        wordAlignedLine=fwa.readline().rstrip()
        alignList=wordAlignedLine.split(" ")
        wm=WordMappings(sentenceAlignedLine,wordAlignedLine)
        
        #--------Get The Mapping Dictionary-------
        nbDict,wdMapSir=wm.getMappings()
        if nbDict :
            nSourceTokens,nTargetTokens=wm.getNTokens()
            
            af=AlignFeatures(nSourceTokens,nTargetTokens,nbDict)
            alignmentDict=af.getAlignmentFeatures()
            strFeatures=""
            for feature in alignmentDict:
                value=round(alignmentDict[feature],2)
                strFeatures+=str(value)+"\t"
            strFeatures=strFeatures.rstrip()    
            fo.write(strFeatures+"\n")  
        else :
            fo.write(self.getDefaultValues()+"\n")
            
    fsa.close()
    fwa.close()
    fo.close()
    
    return self.pDict["fFeatureAlignment"]
    
    
   def addFeatures(self,segmentFeaturesDict):
    """Add Fast Align Alignment Features to the Feature Dictionary """
    
    self.runTokenizer()
    self.runFastAlign()
    self.merge()
    self.getFeatureValues()
    fi = codecs.open(self.pDict["fFeatureAlignment"], "r", "utf-8")
    featureNames=fi.readline().rstrip().split("\t")
    indexLine=-1
    for line in fi:
        indexLine+=1
        key=str(indexLine)+"-"+str(indexLine)
        line=line.rstrip()
        if key in segmentFeaturesDict :
            featureValues=line.split("\t")
            for i in range(len(featureNames)):
                segmentFeaturesDict[key][featureNames[i]]=featureValues[i]
   
   
    
   def __init__(self, pDict):
    """ Init parameters..."""
    
    self.pDict = pDict
    
    #training or test mode
    if "fCategory" in self.pDict:
        self.fInput=self.pDict["fCategory"]
    else:
        self.fInput=self.pDict["segmentsFile"]
    
def getParameters () :
    """Get the parameters for debug operations."""
    
    pDict={}
    
    pDict["fSentenceAlignment"]="ObtainAlignments/full-English-Italian-Category-en-it-sentenceAlignment.txt"
    pDict["fWordAlignment"]="ObtainAlignments/full-English-Italian-Category-en-it-wordAlignment.txt"
    pDict["fDebug"]="ObtainAlignments/full-English-Italian-Category-en-it-debug.txt"
    pDict["segmentsFile"]=""
    
    return pDict
    
def main():
    
    pDict=getParameters()
    fa=FeaturesFastAlign(pDict)
    fa.debugAlignment()
    print ("Results in:"+pDict["fDebug"])
    
    

if __name__ == '__main__':
  main()   


