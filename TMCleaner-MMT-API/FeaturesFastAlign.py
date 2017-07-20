#!/usr/bin/env python

"""Compute features based on on Fastalign alignments """
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"


import sys
import codecs
import collections
import re
from subprocess import call
import os
from WordMappings import *
import logging
from MMTAlignment import *

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
        
        mmt=MMTAlignments(sSegment,tSegment,self.pDict["sourceLanguage"],self.pDict["targetLanguage"])
        jsonAnswer=mmt.getAlignments()
        if isJson(jsonAnswer) :
            jsonParsed= json.loads(jsonAnswer)
            if not "error" in jsonParsed :
                data=jsonParsed["data"]
                tokString=" ".join(data["sourceToken"])+""" ||| """+" ".join(data["targetToken"])+"\n"
                sirAlignment=""
                for alignment in data["alignments"] :
                    sirAlignment+=str(alignment[0])+"-"+str(alignment[1])+" "
       
                featureValues=self.getAlignmentFeatures (tokString,sirAlignment[:-1])
                featureNames=self.getFeatureNames()

        
                fValuesList=[float(i) for i in featureValues.split("\t")] 
                fNamesList=featureNames.split("\t")
                
                for i, name in enumerate(fNamesList) :
                    featuresDict[name]=fValuesList[i]
            else :
                fNamesList=self.getFeatureNames().split("\t")
                fValuesList=[float(i) for i in self.getDefaultValues().split("\t")]
                for i, name in enumerate(fNamesList) :
                    featuresDict[name]=fValuesList[i]
                
            
        
    
    def __init__(self,argDict,pDict):
        """Processes to run the tokenizer , fastalign with forward and backward models
        and the merge program"""
        
        self.argDict=argDict
        self.pDict = pDict

class FeaturesFastAlign:
   """Compute Features based on Fastalign alignments."""
   
  
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
    
   def isJson(myjson):
     
    try:
        json.loads(myjson)
    except ValueError, e:
        return False
    return True


   def getAlFile (self) :
    """Get Alignment Files """
    
    
    self.pDict["fSentenceAlignment"]=re.sub("(-segments)*\.txt$","",self.pDict["segmentsFile"])+"-"+self.pDict["sourceLanguage"]+"-"+self.pDict["targetLanguage"]+"-sentenceAlignment.txt"
    self.pDict["fWordAlignment"]=re.sub("sentenceAlignment","wordAlignment",self.pDict["fSentenceAlignment"])
   
   
   def treatError (self,components,message,fo1,fo2) :
    """Treat a parsing json error"""
    
    fo1.write(components[2]+""" ||| """+components[3]+"\n")
    fo2.write(""+"\n")
    logging.error("The MMT API returned an error for index "+components[0]+" SSegment#"+components[2]+"###TSegment#"+components[3]+"###Message:"+message+"\n")
    
   
   def align_mmt (self) :
    """Align the training file using MMT API"""
    
    self.getAlFile()
    fi = codecs.open(self.pDict["segmentsFile"], "r", "utf-8")
    fo1 = codecs.open(self.pDict["fSentenceAlignment"], "w", "utf-8")
    fo2 = codecs.open(self.pDict["fWordAlignment"], "w", "utf-8")
    for line in fi :
        line=line.rstrip()
        components=line.split("@#@")
        sSegment=components[2].encode("utf-8")
        tSegment=components[3].encode("utf-8")
        mmt=MMTAlignments(sSegment,tSegment,self.pDict["sourceLanguage"],self.pDict["targetLanguage"])
        jsonAnswer=mmt.getAlignments()
        if isJson(jsonAnswer) :
            jsonParsed= json.loads(jsonAnswer)
            if "error" in jsonParsed :
                message="Default"
                if "message" in jsonParsed["error"] :
                    message=jsonParsed["error"]["message"]
                self.treatError(components,message,fo1,fo2)
                
            else :
                data=jsonParsed["data"]
                fo1.write(" ".join(data["sourceToken"])+""" ||| """+" ".join(data["targetToken"])+"\n")
                sirAlignment=""
                for alignment in data["alignments"] :
                    sirAlignment+=str(alignment[0])+"-"+str(alignment[1])+" "
                fo2.write(sirAlignment[:-1]+"\n")
        else :
            message="Not a json answer"
            self.treatError (components,message,fo1,fo2)
           
    fi.close()
    fo1.close()
    fo2.close()
    
    
    def align_mmt_offline (self) :
        """Align the training or test file using MMT API"""
        
        self.getAlFile()
        fi = codecs.open(self.pDict["segmentsFile"], "r", "utf-8")
        fo1 = codecs.open(self.pDict["fSentenceAlignment"], "w", "utf-8")
        fo2 = codecs.open(self.pDict["fWordAlignment"], "w", "utf-8")
        for line in fi :
            line=line.rstrip()
            components=line.split("@#@")
            sSegment=components[2].encode("utf-8")
            tSegment=components[3].encode("utf-8")
            jsonAnswer=components[4]
            if isJson(jsonAnswer) :
                jsonParsed= json.loads(jsonAnswer)
                if "error" in jsonParsed :
                    message="Default"
                    if "message" in jsonParsed["error"] :
                        message=jsonParsed["error"]["message"]
                    self.treatError(components,message,fo1,fo2)
                else :
                    data=jsonParsed["data"]
                    fo1.write(" ".join(data["sourceToken"])+""" ||| """+" ".join(data["targetToken"])+"\n")
                    sirAlignment=""
                    for alignment in data["alignments"] :
                        sirAlignment+=str(alignment[0])+"-"+str(alignment[1])+" "
                    fo2.write(sirAlignment[:-1]+"\n")
            else :
                message="Not a Json Answer"
                self.treatError (components,message,fo1,fo2)
               
        fi.close()
        fo1.close()
        fo2.close()
   
   
   def addFeaturesOffline(self,segmentFeaturesDict):
    """Add Fast Align Alignment Features to the Feature Dictionary
       but read the alignments from an offline Feature Dict."""
    
    self.align_mmt ()
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
    
   def addFeatures(self,segmentFeaturesDict):
    """Add Fast Align Alignment Features to the Feature Dictionary """
    
    self.align_mmt ()
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
    
    pDict["fSentenceAlignment"]="Debug/full-English-Italian-Category-en-it-sentenceAlignment.txt"
    pDict["fWordAlignment"]="Debug/full-English-Italian-Category-en-it-wordAlignment.txt"
    pDict["segmentsFile"]=""
    
    return pDict
    
def main():
    
    pDict=getParameters()
    fa=FeaturesFastAlign(pDict)
    fa.getFeatureValues()

    
    

if __name__ == '__main__':
  main()   


