#!/usr/bin/env python

"""Computes basic features used by the TM Cleaner in all modalities """
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"



import sys
import codecs
import collections
import math
import urllib2
import urllib
import re
import string
from sklearn.metrics.pairwise import cosine_similarity
from subprocess import call
from collections import Counter
import numpy as np

class Features ():
    """ This class calculates the basic features that only need
       the source segment,the target segment and the language codes detected for source and target."""
    
    def countWordsCriteria (self,wordList,regex) :
        "It counts the words that fulfill certain criteria given in the regular expression. "
        
        nWords=0
        for word in wordList:
            match=re.match(regex, word)
            if match :
                nWords+=1
        return nWords        
    
    def hasCL (self,segment) :
        """1 if the segment contains capital letters"""
        
        regex=r"[A-Z]+"
        tokenList= re.split("\s+",segment)
        nCLWords=self.countWordsCriteria (tokenList,regex)
        if nCLWords :
            return float(1)
        return float(0)
    
    def haveCL(self):
        """Checks if the source and target have Capital Letters"""
        
        return self.hasCL (self.sSegment), self.hasCL (self.tSegment)  
    
    def difWholeWordsCapitalLetters (self) :
    
        """It computes the difference between the number of words that have only capital
        letters in source and destination"""
        
        regex= r'\b[A-Z]{2,}\b'
        tokenS= re.split("\s+",self.sSegmentNoPunctuation)
        tokenT= re.split("\s+",self.tSegmentNoPunctuation)
        
        nSourceWords=self.countWordsCriteria (tokenS,regex)
        nTargetWords=self.countWordsCriteria (tokenT,regex)
        
        
        #---------+1 to not divide to 0----------
        score= float(abs (nSourceWords-nTargetWords))/(nSourceWords+nTargetWords+1)
        
        return float(score)
        
    def difWordsCapitalLetters (self) :
        """It computes the difference between the number of Words that have capital letters 
         in source and destination queries"""
        
        regex=r"[A-Z]+"
        
        tokenS= re.split("\s+",self.sSegmentNoPunctuation)
        tokenT= re.split("\s+",self.tSegmentNoPunctuation)
        
        nSourceWords=self.countWordsCriteria (tokenS,regex)
        nTargetWords=self.countWordsCriteria (tokenT,regex)
        
        #---------to not divide to 0------------
        score=float(abs (nSourceWords-nTargetWords))/(nSourceWords+nTargetWords+1)
        return float(score)

    def hasItem (self,regex,segment) :
        "If a certain type of item exists a feature is generated (e.g. email, url etc...)"
        
        matchList= re.search(regex, segment)
        if (matchList) :
            return float(1)
        return float(0)
    
    def haveItem(self, typeRe):
        """Match a feature in source and target: e.g. email url """
        regex=self.reDict[typeRe]
        return self.hasItem (regex,self.sSegment),self.hasItem (regex,self.tSegment)
        
    def getNWordsSegment (self,segment) :
        "Get the Number of Words for a segment."
        
        words=segment.split("\s+")
        lSeg=0
        for word in words :
            lSeg+=len(word)
        return lSeg
    
    def getNWords (self) :
        "Get the Number of Words for source and target segments"
        
        lSource=self.getNWordsSegment(self.sSegment)
        lTarget=self.getNWordsSegment(self.tSegment)
        return lSource,lTarget

    def getTypeEntry(self) :
        """This gives the type of source and destination Segment (1-1,1-2,3-4).
        It is used only for data inspection."""
        
        lengthSSegment=self.getNWords(self.sSegment)
        lengthDSegment=self.getNWords(self.tSegment)
        
        return str(lengthSSegment)+"-"+str(lengthDSegment)

    def isEqual (self) :
        """Checks if the source and destination segments are the same"""
        
        if (self.sSegment.lower()==self.tSegment.lower()) :
            return float(1)
        return float(0)

    def getNumber (self,segment,item) :
        """Returns the number of items in a segment"""
        
        regex=re.escape(item)+"+";
        return len(re.findall(regex, segment))

    def hasPunctuation(self,segment):
        """1.0 if the segment has punctuation"""
        
        punctuationSigns=["?","!",":",";","(",")","[","]",'"',","]
        for sign in punctuationSigns:
            if segment.find(sign)==-1 :
                return float(0)
        return float(1)
    
    def havePunctuation(self):
        """Check if the source segment and target segment have punctuation"""
        
        return self.hasPunctuation(self.sSegment),self.hasPunctuation(self.tSegment)

    def prepareVectors (self,sourceVect,destVect) :
        """Prepare the vectors to for cosine similarity function """
        
        X=np.asarray(sourceVect).reshape(1,-1)
        Y=np.asarray(destVect).reshape(1,-1)
        
        return X,Y

    def getPunctuationSimilarity(self) :
        """Returns the cosine similarity between two vectors source and destination Queries"""
        
        punctuationSigns=[".","?","!",":",";","(",")","[","]",'"',","]
        sourceVect=[]
        targetVect=[]
        
        for sign in punctuationSigns :
            nSignsSource=self.getNumber (self.sSegment,sign)
            sourceVect.append(nSignsSource)
            
            nSignsDest=self.getNumber(self.tSegment,sign)
            targetVect.append(nSignsDest)
        
        allZero=[0]*len(punctuationSigns)
        if sourceVect==allZero and targetVect == allZero :
            return float(1)
        
        X,Y=self.prepareVectors (sourceVect,targetVect)
        cosineSimilarity=cosine_similarity(X,Y) 
        return cosineSimilarity[0][0]

    def normalizeNumbers (self,numberList) :
        """Numbers can be on different formats in the Source and Target Queries.
           This function normalizes the numbers """
           
        newList=[]
        for number in numberList :
            number=re.sub("[\.,\,]+","",number)
            newList.append(number)
        return newList    

    def getNumberSimilarity (self,typeRe) :
        """Returns the difference betwen the number of numbers in the source and the destination segments"""
        
        regex=self.reDict[typeRe]
        
        numbersSourceList=re.findall(regex, self.sSegment)
        numbersDestList=re.findall(regex, self.tSegment)
        
        if (numbersSourceList==[] and numbersDestList==[]) :
            return float(1)

        numbersSourceList=self.normalizeNumbers(numbersSourceList)
        numbersDestList=self.normalizeNumbers(numbersDestList)
        
        uniqueFeatureList=list(set(numbersSourceList+numbersDestList))
        sourceDict=Counter(numbersSourceList)
        destDict=Counter(numbersDestList)
        
        sourceVect=self.getVector(uniqueFeatureList,sourceDict)
        destVect=self.getVector(uniqueFeatureList,destDict)
        
        X,Y=self.prepareVectors (sourceVect,destVect)
        cosineSimilarity=cosine_similarity(X,Y)         
        return cosineSimilarity[0][0]

    def getItemSimilarity (self,typeRe) :
        """Gets the similarity between the vectors of somethingh (e.g. emails) in source and destination queries"""
        
        regex=self.reDict[typeRe]
        sourceList=re.findall(regex, self.sSegment)
        targetList=re.findall(regex, self.tSegment)
        
        if (sourceList==[] and targetList==[]) :
            return float(1)
        
        uniqueFeatureList=list(set(sourceList+targetList))
        sourceDict=Counter(sourceList)
        targetDict=Counter(targetList)
        
        sourceVect=self.getVector(uniqueFeatureList,sourceDict)
        destVect=self.getVector(uniqueFeatureList,targetDict)
        
        X,Y=self.prepareVectors (sourceVect,destVect)
        cosineSimilarity=cosine_similarity(X,Y) 
        return cosineSimilarity[0][0]       

    def getLang (self,listLanguages,probLang) :
        detectedLang=""
        for lang in listLanguages :
            if lang==probLang :
                detectedLang=lang
        if detectedLang=="" :
            detectedLang=listLanguages[0]
        return detectedLang
    
    def guessLang (self,detectedSLangs,detectedDLangs,sLang,dLang) :
        "A meta function to guess the right language from the languages identified by the language guesser"
        
        sListLanguages=detectedSLangs.split("#")
        dListLanguages=detectedDLangs.split("#")
        
        guessedSLang=self.getLang (sListLanguages,sLang)
        guessedDLang=self.getLang(dListLanguages,dLang)
        
        return (guessedSLang,guessedDLang) 
        
    def getLangScore (self,detectedSLangs,detectedDLangs,sLang,dLang) :
        """It computes the difference between the detected source and destination languages"""
        
        guessedSlang,guessedDLang=self.guessLang (detectedSLangs,detectedDLangs,sLang,dLang)
        dif=0.0
        
        if(sLang!=guessedSlang) :
            dif+=1
        elif(dLang!=guessedDLang) :
            dif+=1
        return dif
        
    def getLength (self,sir):
        """It counts the length of queries ignoring spaces."""
        
        length=0
        for wd in sir.split():
            length+=len(wd)
        return length
        
    def getCGSore (self) :
        """It computes Church Gale Score"""
        
        lSource=self.getLength(self.sSegment)
        lDestination=self.getLength(self.tSegment)
        numarator=lDestination-lSource
        numitor=math.sqrt(3.4*(lSource+lDestination))
        cgScore=numarator/numitor
        return abs(round(cgScore,2))

    def getVector (self,uniqueFeatureList, featureDict) :
        "Get the vectors to be used in the computation of cosine similarity"
        
        vector=[]
        for feature in uniqueFeatureList :
            if  feature in featureDict :
                vector.append(featureDict[feature])
            else :
                vector.append(0)
                
        return vector

    def removePunctuation (self,segment) :
        """It removes the punctuation from a segment.
         In this way increases the probability of good similarity match."""
         
        punctList=list(string.punctuation)
        for punct in punctList :
            segment=segment.replace(punct," ")
        return segment
    
    def normalizeSpaces(self,segment):
        """Normalize the spaces in a chunck"""
         
        segment=re.sub("\s+$","",segment)
        segment=re.sub("^\s+","",segment)
        segment=re.sub("\s+"," ",segment)
         
        return segment
    
    def nameEntityDetection(self,sir):
        """Simple Rules for Name Entity Detection.
        Take all contiguos segments of Upper Capital letters words"""
        
        nameEntityList=[]
        sir=self.removePunctuation(sir)
        sir=self.normalizeSpaces(sir)
        
        matchList=re.findall(self.reDict["nameEntity"],sir)
        return matchList
    
    def hasNameEntity(self,segment):
        """If the source or target segments have name entities 1 otherwise 0"""
        
        matchList=self.nameEntityDetection(segment)
        if (matchList) :
            return float(1)
        return float(0)
    
    def haveNameEntity(self):
        """1 if the source and target segments have name entities """
    
        return self.hasNameEntity(self.sSegment), self.hasNameEntity(self.tSegment)
    
    def getNameEntitiesSimilarity(self):
        """Get the Name Entity similarity between the source and target"""
        
        matchSourceList=self.nameEntityDetection(self.sSegment)
        matchDestinationList=self.nameEntityDetection(self.tSegment)
        
        if (matchSourceList==[] and matchDestinationList==[]) :
            return float(1)

        uniqueFeatureList=list(set(matchSourceList+matchDestinationList))
        sourceDict=Counter(matchSourceList)
        destDict=Counter(matchDestinationList)
        
        sourceVect=self.getVector(uniqueFeatureList,sourceDict)
        destVect=self.getVector(uniqueFeatureList,destDict)
        
        X,Y=self.prepareVectors (sourceVect,destVect)
        cosineSimilarity=cosine_similarity(X,Y)        
        return cosineSimilarity[0][0]
    
    def readRegularExpressions (self, fileRe) :
        fre = codecs.open(fileRe, "r", "utf-8")
        reDict={}
        for lineSegment in fre:
            lineSegment=lineSegment.rstrip()
            argument,value=lineSegment.split("\t")
            reDict[argument]=value
        return reDict       
    
    def __init__(self,sSegment,tSegment,fRe):
      self.sSegment=sSegment
      self.tSegment=tSegment
      self.sSegmentNoPunctuation=self.removePunctuation(sSegment)
      self.tSegmentNoPunctuation=self.removePunctuation(tSegment)
      self.reDict=self.readRegularExpressions(fRe)
      

def main():
    pass

if __name__ == '__main__':
  main()
