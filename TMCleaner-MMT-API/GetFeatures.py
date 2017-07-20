#!/usr/bin/env python


"""Compute the Features for Training or Test set."""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import codecs
import collections
import re
from Features import *
import logging
from FeaturesFastAlign import *
import Parameters


class GetFeatures:
   """Compute the Features for Training or Test set."""
   
   def writeFeatureFile (self,fOutput,segmentFeaturesDict) :
    """Print the file in the CSV format to be handeled by scikit-learn"""
    
    fs = codecs.open(fOutput, "w", "utf-8")
    
    dbKeysList=segmentFeaturesDict.keys() #3091-20,3450-1
    featureNameDict=segmentFeaturesDict[dbKeysList[0]] 
    featureNameList=featureNameDict.keys() #langDifference,emailDifference
    
    featureNameList.remove("sourcesegment")
    featureNameList.remove("targetsegment")
    
    #------Write the first row containing feature names--------
    featureString="dbkey,"
    for feature in featureNameList :
        featureString+=feature+","
    featureString=featureString.rstrip(',')+"\n"
    
    fs.write(featureString)
    
    for dbKey in dbKeysList :
        featureValueString=dbKey+","
        for featureName in featureNameList :
            featureValueString+=str(segmentFeaturesDict[dbKey][featureName])+","
        featureValueString=featureValueString.rstrip(',')+"\n"
        fs.write(featureValueString)
   
   def readCategory(self):
    """Read the Category from the category file ..."""
    categoryD={}
    fi =codecs.open(self.pDict["fCategory"], "r", "utf-8")
    for line in fi:
        line=line.rstrip()
        components=line.split("@#@")
        category=int(components[-1])
        categoryD[components[0]+"-"+components[1]]=category
    fi.close()
    
    return categoryD            
    
   def addCategory(self,segmentFeaturesDict):
    """Add Category to the training features"""
    
    categoryD=self.readCategory()
    for key in segmentFeaturesDict:
        if key in categoryD :
           segmentFeaturesDict[key]["category"]=categoryD[key]
   
   def removeCategory(self):
    """Remove the category from the trainig file to obtain a standard input file equivalent to the test file"""
    
    fi = codecs.open(self.pDict["fCategory"], "r", "utf-8")
    fo = codecs.open(self.pDict["segmentsFile"], "w", "utf-8")
    
    for line in fi:
        line=line.rstrip()
        components=line.split("@#@")
        components.pop(-1)
        newLine="@#@".join(components)
        fo.write(newLine+"\n")
    fi.close()
    fo.close()
   
   def cleanSegment (self,segment) :
    """It cleans the segment from trailing spaces and the sign %@% that means "EOL"."""
    
    segment=re.sub("^\s+","",segment)
    segment=re.sub("\s+$","",segment)
    
    return segment
   
   def generateFeaturesLine (self,lineSegment,pDict) :
    """Generate the features for only a bisegment"""
    
    sLang=pDict["sourceLanguage"]
    dLang=pDict["targetLanguage"]
    featuresDict={}   
    id1,id2,sourceSegment,targetSegment,detectedSLangs,detectedDLangs=lineSegment.split("@#@")
    
    sourceSegment=self.cleanSegment (sourceSegment)
    targetSegment=self.cleanSegment(targetSegment)
    features=Features(sourceSegment,targetSegment,pDict["fileRe"])
    
    #Church Gale score
    featuresDict["cgscore"]=features.getCGSore()
    featuresDict["same"]=features.isEqual ()
    
    #Capital Letters
    featuresDict["hassourcecl"],featuresDict["hastargetcl"]=features.haveCL()
    featuresDict["caplettersworddif"]=features.difWordsCapitalLetters ()
    featuresDict["onlycaplettersdif"]=features.difWholeWordsCapitalLetters ()
    
    #Language Related Features: 0.0
    featuresDict["langdif"]=features.getLangScore (detectedSLangs,detectedDLangs,sLang,dLang)
    
    #URL and Similarity
    featuresDict["hassourceurl"],featuresDict["hastargeturl"]=features.haveItem("urlRe")
    featuresDict["urlsim"]=round(features.getItemSimilarity("urlRe"),2)
    
    #TAG and Similarity
    featuresDict["hassourcetag"],featuresDict["hastargettag"]=features.haveItem("tagRe")
    featuresDict["tagsim"]=round(features.getItemSimilarity("tagRe"),2)
    
    #EMAIL and Similarity
    featuresDict["hassourceemail"],featuresDict["hastargetemail"]=features.haveItem("emailRe")
    featuresDict["emailsim"]=round(features.getItemSimilarity("emailRe"),2)
    
    #NUMBER and Similarity
    featuresDict["hassourcenumber"],featuresDict["hastargetnumber"]=features.haveItem("numberRe")
    featuresDict["numbersim"]=round(features.getNumberSimilarity("numberRe"),2)
    
    #PUNCTUATION and Similarity
    featuresDict["hassourcepunctuation"],featuresDict["hastargetpunctuation"]=features.havePunctuation()
    featuresDict["punctsim"]=round(features.getPunctuationSimilarity(),2)
    
    #Name Entity Detection and Similarity
    featuresDict["hassourcenameentity"],featuresDict["hastargetnameentity"]=features.haveNameEntity()
    featuresDict["nersimilarity"]=features.getNameEntitiesSimilarity()
   
    return featuresDict
   
   def generateFeatures (self,pDict) :
    """It reads the bisegments from the file and computes the features for each of them"""
    
    sLang=pDict["sourceLanguage"]
    dLang=pDict["targetLanguage"]
    
    segmentFeaturesDict=collections.OrderedDict()
    fs = codecs.open(pDict["segmentsLangFile"], "r", "utf-8")
    for lineSegment in fs:
        featuresDict={}
        lineSegment=lineSegment.rstrip()
        
        dictKey1,dictKey2,sourceSegment,targetSegment,detectedSLangs,detectedDLangs=lineSegment.split("@#@")
        dictKey=dictKey1+"-"+dictKey2
        
        sourceSegment=self.cleanSegment (sourceSegment)
        targetSegment=self.cleanSegment(targetSegment)
        features=Features(sourceSegment,targetSegment,pDict["fileRe"])   
        
        #---------Features that are not used in ML ---------------    
        featuresDict["sourcesegment"]=sourceSegment
        featuresDict["targetsegment"]=targetSegment
        featuresDict["nwordssource"],featuresDict["nwordstarget"]=features.getNWords()
        
        
        #--------Features used in ML------------------
        
        #Church Gale score
        featuresDict["cgscore"]=features.getCGSore()
        featuresDict["same"]=features.isEqual ()
        
        #Capital Letters
        featuresDict["hassourcecl"],featuresDict["hastargetcl"]=features.haveCL()
        featuresDict["caplettersworddif"]=features.difWordsCapitalLetters ()
        featuresDict["onlycaplettersdif"]=features.difWholeWordsCapitalLetters ()
        
        #Language Related Features: 0.0
        featuresDict["langdif"]=features.getLangScore (detectedSLangs,detectedDLangs,sLang,dLang)
        
        #URL and Similarity
        featuresDict["hassourceurl"],featuresDict["hastargeturl"]=features.haveItem("urlRe")
        featuresDict["urlsim"]=round(features.getItemSimilarity("urlRe"),2)
        
        #TAG and Similarity
        featuresDict["hassourcetag"],featuresDict["hastargettag"]=features.haveItem("tagRe")
        featuresDict["tagsim"]=round(features.getItemSimilarity("tagRe"),2)
        
        #EMAIL and Similarity
        featuresDict["hassourceemail"],featuresDict["hastargetemail"]=features.haveItem("emailRe")
        featuresDict["emailsim"]=round(features.getItemSimilarity("emailRe"),2)
        
        #NUMBER and Similarity
        featuresDict["hassourcenumber"],featuresDict["hastargetnumber"]=features.haveItem("numberRe")
        featuresDict["numbersim"]=round(features.getNumberSimilarity("numberRe"),2)
        
        #PUNCTUATION and Similarity
        featuresDict["hassourcepunctuation"],featuresDict["hastargetpunctuation"]=features.havePunctuation()
        featuresDict["punctsim"]=round(features.getPunctuationSimilarity(),2)
        
        #Name Entity Detection and Similarity
        featuresDict["hassourcenameentity"],featuresDict["hastargetnameentity"]=features.haveNameEntity()
        featuresDict["nersimilarity"]=features.getNameEntitiesSimilarity()
        
        segmentFeaturesDict[dictKey]=featuresDict
        
    return segmentFeaturesDict
   
   def generateTestFeatures(self,pBatch):
    """Generate Test Features"""
    
    logger = logging.getLogger('GetFeatures::generateTestFeatures')
    logger.info ("Generate Universal Features ")
    segmentFeaturesDict=self.generateFeatures (pBatch)
    
    logger.info( "Add FastAlign Features")
    fa=FeaturesFastAlign(pBatch)
    fa.addFeatures(segmentFeaturesDict)
   

    logger.info ("Store Model File  : "+pBatch["testFeatureFile"])
    self.writeFeatureFile (pBatch["testFeatureFile"],segmentFeaturesDict)
   
   def getLanguageForSegmentFile (self) :
        commandList=["java" ,"-cp",self.pDict["javaClassPath"],self.pDict["javaClass"],
                     self.pDict["segmentsFile"],self.pDict["sourceLanguage"],
                     self.pDict["targetLanguage"],self.pDict["langProfileDirectory"]]
        self.pDict["segmentsLangFile"]=self.pDict["segmentsFile"]+".lang.txt"
        call(commandList)
    
   def generateTrainingFeatures(self):
    """Generate Training Features."""
    
    logger = logging.getLogger('GetFeatures::generateTrainingFeatures')
    logger.info ("Detect Source and Target Languages ")
    self.pDict["segmentsFile"]=re.sub(".txt$","",self.pDict["fCategory"])+"-segments.txt"
    self.removeCategory()
    self.getLanguageForSegmentFile ()
    
    logger.info( "Generate Universal Features ")
    segmentFeaturesDict=self.generateFeatures (self.pDict)
      
    logger.info( "Add FastAlign Features")
    fa=FeaturesFastAlign(self.pDict)
    fa.addFeatures(segmentFeaturesDict)
     
    logger.info( "Add the category for the Training Set")
    self.addCategory(segmentFeaturesDict)
    
    logger.info ("Store Model File  : "+self.pDict["trainingFeatureFile"])
    self.writeFeatureFile (self.pDict["trainingFeatureFile"],segmentFeaturesDict)
   
   def __init__(self,pTrainingFile=None):
      self.pTrainingFile = pTrainingFile
      if pTrainingFile :
        self.pDict=Parameters.readParameters(self.pTrainingFile)
     
   
   