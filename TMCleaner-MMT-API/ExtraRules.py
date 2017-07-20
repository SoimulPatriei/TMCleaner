#!/usr/bin/env python

"""Rule based classification based on test sets provided by Luca Mastrostefano
and Francesco Elefante from Translated"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"




import sys
import re
import codecs
import math
from MMTAlignment import *


class ExtraRules:
    """Apply rules that generate true or false values for the TU's  starting from some test sets"""
    
    def __init__(self,source,target,pDict):
        self.source=self.cleanQuery(source)
        self.target=self.cleanQuery(target)
        self.pDict=pDict
    
    
    def ruleAlignment (self) :
        """If there are few words is source and target and some alignments then return True """
        
        maxWordsSource=4
        maxWordsTarget=4
        minAlignmentTreshold=0.3
        
            
        wordsSource=self.source.split()
        wordsTarget=self.target.split()
        
        
        if len(wordsSource) <=maxWordsSource and len(wordsTarget) <=maxWordsTarget :
            mmt=MMTAlignments(self.source,self.target,self.pDict["sourceLanguage"],self.pDict["targetLanguage"])
            jsonAnswer=mmt.getAlignments()
            if isJson(jsonAnswer) :
                jsonParsed= json.loads(jsonAnswer)
                if not "error" in jsonParsed :
                    data=jsonParsed["data"]
                    nAlignments=len(data["alignments"])
                    nSourceWords=len(data["sourceToken"])
                    nTargetWords=len(data["targetToken"])
                    nMaxAlignments=min(nSourceWords,nTargetWords)
                    if float(nMaxAlignments)/nAlignments >= minAlignmentTreshold :
                        return True
        return False    

        
        
    def cleanQuery (self,string) :
        """It cleans the string from trailing spaces."""
        
        string=re.sub("^\s+","",string)
        string=re.sub("\s+$","",string)
        
        return string
        
    def countCapital(self, string) :
        """Count the number of words that start with capital letters divide by the numbers of words """
        
        words=string.split()
        nWordsCapital=0
        for wd in words :
            if wd[0].isupper() :
                nWordsCapital+=1
        return float (nWordsCapital)/(len(words))
    
    def ruleAbreviation (self) :
        """If left sides contains an abreviation and right side expands the abbreviation:
        e.g. FDIC@#@Federal Deposit Insurance Corporation"""
        
        threshold=0.5
        m=re.match("^[A-Z]+$", self.source)
        if m :
            propCap=self.countCapital(self.target)
            if propCap>=threshold :
                return True  
        return False
        
def main():
 
    print "Start Test..."
    
    source="FDIC"
    target="federal Deposit insurance corporation"
    
    rl=ExtraRules(source,target)
    if rl.ruleAbreviation() :
        print "abreviationRule=>"+"1"
    
    print "End Test ..."
    
    
if __name__ == '__main__':
  main()