#!/usr/bin/env python

"""Rule based classification"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"




import sys
import re
import codecs
import math


class Rules:
    """Apply rules that generate true or false values for the TU's  with good accuracy"""
    
    def __init__(self,source,target):
        self.source=self.cleanQuery(source)
        self.target=self.cleanQuery(target)
        
    def getDigits(self,string):
        """It gets the digits of a string if the number of digits is bigger than the number of letters."""
    
        digits=[c for c in string if c.isdigit()]
        nDigits= sum(1 for c in string if c.isdigit())
        nLetters=sum(1 for c in string if c.isalpha())
        
        if nDigits >nLetters :
            return True,"".join(digits)
        return False,"".join(digits)
 
    def ruleNumbers(self):
        """Treat entries that contain in majority numbers.
        Make the numbers and then compare the entries."""
        
        isSource,digitSource=self.getDigits(self.source)
        isTarget,digitTarget=self.getDigits(self.target)
        
        if isSource==True and isTarget==True :
            if digitSource==digitTarget :
                return True, "Number" 
            else :
                return False, "Number"
            
        return False, "General"
    
    
    def cleanQuery (self,string) :
        """It cleans the string from trailing spaces."""
        
        string=re.sub("^\s+","",string)
        string=re.sub("\s+$","",string)
        
        return string
        
    def ruleSame(self):
        """If the source and target contain the same word and
        the source and target are less than xxx characters
        then the source and target are OK. """
        
        sourceList=re.split("\s+",self.source)
        targetList=re.split("\s+",self.target)
        
        if len(sourceList) ==1 and len(targetList) ==1 and sourceList[0]==targetList[0] and len(self.source)<9:
            return True
        return False
    
    def ruleNameEntities(self):
        """A simple Name Entity Detection module"""
        
        sourceList=re.split("\s+",self.source)
        if self.source==self.target and len(sourceList)>1 :
            nCL=0
            for word in sourceList:
                if word[0].isupper() :
                    nCL+=1
            if nCL>(len(sourceList)-1)/float(2):
                return True
        
        return False
    
    def getLang (self,listLanguages,probLang) :
        detectedLang=""
        for lang in listLanguages :
            if lang==probLang :
                detectedLang=lang
        if detectedLang=="" :
            detectedLang=listLanguages[0]
        return detectedLang
    
    def hasManyCL(self,string):
        """It evalutes if a string has many capital letters. """
        
        nCL=sum(1 for c in string if c.isupper())
        lString=len(string)
        
        if float(nCL)/lString >0.5 :
            return True
        return False
    
    def ruleIdenticalLC(self,components,pBatch):
        """This rule says that if the length of the
        source and target are big enough and if the source and target have the same language code then
        the bisegment should be discarded"""
        
        guessedSLang=self.getLang(components[4].split("#"),pBatch["sourceLanguage"])
        guessedTLang=self.getLang(components[5].split("#"),pBatch["targetLanguage"])
        sourceList=re.split("\s+",self.source)
        
        if len(sourceList) >5 and (guessedSLang==guessedTLang):
            return True
        
        return False
    
    def getLength (self,sir):
        """It counts the length of queries ignoring spaces."""
        
        length=0
        for wd in sir.split():
            length+=len(wd)
        return length

    def getCGSore (self) :
        """It computes Church Gale Score"""
        
        lSource=self.getLength(self.source)
        lDestination=self.getLength(self.target)
        numarator=lDestination-lSource
        numitor=math.sqrt(3.4*(lSource+lDestination))
        cgScore=numarator/numitor
        return abs(round(cgScore,2))

    def ruleCG(self):
        """Apply Church Gale rule"""
        
        treshold=3.0
        absCGScore=abs(self.getCGSore())
        if absCGScore >treshold :
            return True
        
def main():
 
    print "Start Test..."
    
    source="Phone: (514) 861-8788"
    target="Telefono :  (514) 861-8788"
    
    rl=Rules(source,target)
    if rl.ruleNumbers() ==(True,"Number") :
        print "NumberRule:"+"1"
        
    elif rl.ruleNumbers() ==(False,"Number") :
        print "NumberRule:"+"0"
    
    print "End Test ..."
    
    
if __name__ == '__main__':
  main()