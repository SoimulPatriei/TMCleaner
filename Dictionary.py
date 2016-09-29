#!/usr/bin/env python


"""This class loads a dictionary and  generates a pseudo translation based on the read dictionary"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import codecs
import sys
import re
import logging
import os
from os.path import split
from os import listdir
from os.path import isfile, join,isdir
import AhoNode
import string



class Dictionary:
   """This class loads a dictionary and  generates a pseudo translation based on the read dictionary"""
   
   def __init__(self,fSegments,fTrDict,dFile):
    
      self.fSegments=fSegments
      self.fTrDict=fTrDict
      self.dFile=dFile
   
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
    
   def computeRatio (self,initialSegment,mappedSegment) :
    """Compute the aligned words in source and in target. """
    if mappedSegment :
        wdInit=initialSegment.split(" ")
        wdMapped=mappedSegment.split(" ")
        ratio=round(float(len(wdMapped))/(len(wdInit)),2)
        return ratio
    return float(0)
    
    
   def addFeatures (self,segmentFeaturesDict) :
    """Get the translation based on the (probabilistic) dictionary """
    
    dictionary=self.readDictionary(self.dFile)
    root=self.createAhoTree(dictionary)
    
    fi = codecs.open( self.fSegments, "r", "utf-8")
    fo = codecs.open( self.fTrDict, "w", "utf-8")
    
    for line in fi :
        line=line.rstrip()
        components=line.split("@#@")
        dictTSegment=""
        key=components[0]+"-"+components[1]
        sSegment=self.normalizeSpaces(self.removePunctuation(components[2]))
        tSegment=self.normalizeSpaces(self.removePunctuation(components[3]))
        
        if sSegment==tSegment :
            dictTSegment=""
            segmentFeaturesDict[key]["sratio"]=0.0
            segmentFeaturesDict[key]["tratio"]=0.0
        else :
            sList,tList,commonList=self.eliminateCommon (sSegment,tSegment)
            sBestList=self.getSourceList(" ".join(sList),root)
            sCompleteList=sBestList+commonList
            dictSSegment=" ".join(sCompleteList)
            
            tBestList=self.getTargetList (sBestList,dictionary,tList)
            tCompleteList=tBestList+commonList
            dictTSegment=" ".join(tCompleteList)
            
            sRatio=self.computeRatio (sSegment,dictSSegment)
            tRatio=self.computeRatio(tSegment,dictTSegment)
            
            segmentFeaturesDict[key]["sratio"]=sRatio
            segmentFeaturesDict[key]["tratio"]=tRatio
            
        sirOutput="@#@".join([components[0],components[1],tSegment,dictTSegment,str(sRatio),str(tRatio)])
        fo.write(sirOutput+"\n")
    fi.close()
    fo.close()
      
   def createAhoTree(self,dictionary):
    """It creates the Aho Tree for the File List ..."""
    
    wList=dictionary.keys()
    root = AhoNode.aho_create_statemachine(wList)
    return root

   def readDictionary (self,fDictionary) :
        """Read Probabilistic Dictionary"""
        
        dictionary={}
        fi=codecs.open(fDictionary, "r", "utf-8")
        for line in fi :
            line=line.rstrip()
            
            #in Hunalign is viceversa target:source
            tUnit,sUnit=line.split(" @ ")
            dictionary.setdefault(sUnit.lower(), {})
            dictionary[sUnit.lower()][tUnit.lower()]="0"
        fi.close()
        return dictionary
 
   def eliminateCommon (self,sunit,tunit) :
        """Eliminate common words from source and target"""
        
        sList=sunit.split(" ")
        tList=tunit.split(" ")
        
        intersectSet=set(sList).intersection(tList)
        
        for el in intersectSet :
            sList.remove(el)
            tList.remove(el)
            
        return sList , tList, list(intersectSet)

   def cleanList (self,bestList) :
        """Deduplicate List when I matched multiple words but: this is not nice """
        
        deDupList=[]
        indexToDelete=[]
        for i in range(len(bestList)) :
            for j in range(i+1,len(bestList)) :
                sourceSet=set(bestList[i].split(" "))
                targetSet=set(bestList[j].split(" "))
                if sourceSet.issubset (targetSet) :
                    indexToDelete.append(i)
                elif targetSet.issubset(sourceSet) :
                    indexToDelete.append(j)
                else :
                    break
                
        deDupList = [element for j,element in enumerate(bestList) if j not in indexToDelete]
        return deDupList

   def getBestCoverage (self,unit,resList) :
        """Get best coverage by dictionary words"""
        
        bestList=[]
        bestDict={}
        myList=unit.split(" ")
        for item in resList:
            offsetChar,word=item.split("\t")
            offset=int(offsetChar)
            boolean=False
            components=word.split(" ")
            for comp in components:
                if comp not in myList :
                    boolean=False
                    break
                else :
                    boolean=True
            if boolean :
                bestDict.setdefault(offset,{})
                bestDict[offset][word]=0
        
        for offset in sorted(bestDict) :
            myWord=""
            maxLen=0
            maxOffset=0
            for word in bestDict[offset] :
                if len(word)>maxLen :
                    maxLen=len(word)
                    myWord=word            
            bestList.append(myWord)
        cleanList=self.cleanList(bestList)
                
        return cleanList
        
   def getSourceList (self,unit,root) :
        """Match dictionary against the source.
           Return the best matched list."""
        
        resList=[]
        AhoNode.aho_find_all(unit, root, resList)
        bestList=self.getBestCoverage(unit,resList)
        return bestList
        
   def getTargetList (self, sBestList,dictionary,tList) :
        """Get the target corresponding to the source"""
        
        tBestList=[]
        for wdSource in sBestList :
            targetDict=dictionary[wdSource]
            for wdTarget in targetDict:
                boolean=False
                components=wdTarget.split(" ")
                for comp in components:
                    if comp not in tList :
                        boolean=False
                        break
                    else :
                        boolean=True
                if boolean :
                    for comp in components:
                        tBestList.append(comp)
                    break
        return tBestList        
    
   def getNumberMapped (unitList,bestUnitList) :
        """Get the number of mapped words"""
        
        intersectSet=set(unitList).intersection(bestUnitList)
        return len(intersectSet)


   
def test() :
        """Test List Cleaning"""
        
        print ("Test")
        bestList=[u'solution after lunch', u'after', u'lunch', u'for cattle', u'cattle', u'and', u'pigs']
        dedupList=cleanList(bestList)
        print (bestList)
        print (dedupList)
        print ("End Test")        
 
 
def main():
    
   #see the last two translations they are bad. also add in output the TSegment.  
   fSegments="DictTest/smallFile.txt"
   fTrDict="DictTest/smallFileTranslated.txt"
   dFile="Resources/Dictionaries/English-Italian-Test.dic.txt"
   
   print "Translate using the dictionary"
   segmentFeaturesDict={"0-0":{},"1-1":{},"2-2":{},"3-3":{},"4-4":{},"5-5":{},"6-6":{},"7-7":{},"8-8":{},"9-9":{}}
   dictionary=Dictionary(fSegments,fTrDict,dFile)
   dictionary.addFeatures(segmentFeaturesDict)
   print "End translation"
  
   
   
   
   
   
   
  


if __name__ == '__main__':
  main()
  