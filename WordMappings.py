#!/usr/bin/env python

"""Manage the Word Mappings resulted from Fastalign alignments. """
   
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import codecs
import collections
import re

class AlignFeatures:
    """Compute features necessary for alignment ..."""
    
    
    def computeZones(self,inputList,lSize):
        """I compute Zones by Binary representation"""
    
        # blist =>11001110, bCompList =>1010, BLenList=>2231
        
        bList = [0] * lSize
        for i in range(lSize):
            if i in inputList :
                bList[i]=1
                
        bCompList=[]
        bLenList=[]
        
        bitPrev=-1
        bList.append(-1) #for last comparison
        zLen=0
        for bit in bList:
            if bit != bitPrev :
                if zLen:
                    bLenList.append(zLen)
                    zLen=0    
                bitPrev=bit    
                bCompList.append(bit)
            zLen+=1
        
        bList.pop(-1)
        bCompList.pop(-1)
        return bList,bCompList,bLenList
   
   
    def getZoneProp(self,bComplist):
        """Get the positive zone proportion and negative zone proportion."""
    
        nZones=len(bComplist)
        nPosZone=len([i for i in bComplist if i==1])
        nNegZone=len([i for i in bComplist if i==0])
        
        posProp=float(nPosZone)/float(nZones)
        negProp=float(nNegZone)/float(nZones)
        
        return posProp, negProp
    
    
    def printLists(self,fo):
        """Get and print the Lists. Just for debugging"""
        
        sNumberList,tNumberList=self.getUniqueMappedWords()
        
        sbList,sbCompList,sbLenList=self.computeZones(sNumberList,self.nSourceTokens)
        fo.write("Source Lists\n")
        fo.write("".join(map(str,sbList))+"->")
        fo.write(" ".join(map(str,sbLenList))+"\n")
        fo.write("".join(map(str,sbCompList))+"\n")
        
        
        tbList,tbCompList,tbLenList=self.computeZones(tNumberList,self.nTargetTokens)
        fo.write("Target Lists\n")
        fo.write("".join(map(str,tbList))+"->")
        fo.write(" ".join(map(str,tbLenList))+"\n")
        fo.write("".join(map(str,tbCompList))+"\n")
        
    
    def getExtremeZoneRL(self,bCompList,bLenList,length):
        """Get the Relative Lenght of the most extreme zones ."""
        
        maxOneValue=0
        maxZeroValue=0
        for i in range(len(bCompList)):
            if bCompList[i]==0 :
                if bLenList[i]>maxZeroValue:
                    maxZeroValue=bLenList[i]
            else :
                if bLenList[i]>maxOneValue:
                    maxOneValue=bLenList[i]
        
        
        maxOneRatio=float(maxOneValue)/length
        maxZeroRatio=float(maxZeroValue)/length
        return maxOneRatio,maxZeroRatio
        
    
    def getZoneRatio(self):
        """Compute zone ratio ..."""
            
        sNumberList,tNumberList=self.getUniqueMappedWords()
        sbList,sbCompList,sbLenList=self.computeZones(sNumberList,self.nSourceTokens)
        smaxOne,smaxZero=self.getExtremeZoneRL(sbCompList,sbLenList,self.nSourceTokens)
        sposProp, snegProp=self.getZoneProp(sbCompList)
        
        
        tbList,tbCompList,tbLenList=self.computeZones(tNumberList,self.nTargetTokens)
        tposProp, tnegProp=self.getZoneProp(tbCompList)
        tmaxOne,tmaxZero=self.getExtremeZoneRL(tbCompList,tbLenList,self.nTargetTokens)
        
        zoneDict=collections.OrderedDict()
        
        #Max Zone Features
        zoneDict["smaxOneZone"]=smaxOne
        zoneDict["smaxZeroZone"]=smaxZero
        zoneDict["tmaxOneZone"]=tmaxOne
        zoneDict["tmaxZeroZone"]=tmaxZero
        
        #Zone Proportions
        zoneDict["sPositiveZoneRatio"]=sposProp
        zoneDict["sNegativeZoneRatio"]=snegProp
        zoneDict["tPositiveZoneRatio"]=tposProp
        zoneDict["tNegativeZoneRatio"]=tnegProp
        
        return zoneDict
        

    def getAlignmentFeatures(self):
        """Get the alignment features in a dictionary """
        
        sRatio,tRatio=self.wordRatio()
        zoneDict=self.getZoneRatio()
        
        alignmentDict= collections.OrderedDict()
        
        alignmentDict["sWordRatio"]=sRatio
        alignmentDict["tWordRatio"]=tRatio
        
        for fName in zoneDict:
            alignmentDict[fName]=zoneDict[fName]
        
        return alignmentDict    
    
    def getUniqueMappedWords(self):
        """Get Unique Mapped Words in source and target """
        
        tNumberList=[]
        sNumberList=sorted(self.nbDict.keys())
        for lindex in sNumberList:
            for rindex in self.nbDict[lindex]:
                if rindex not in tNumberList:
                    tNumberList.append(rindex)
        tNumberList=sorted(tNumberList)
        return sNumberList,tNumberList
    
        
    def wordRatio(self):
        """Compute the ratio of aligned words in the source and target segments"""
        
        sNumberList,tNumberList=self.getUniqueMappedWords()
        sRatio=float(len(sNumberList))/self.nSourceTokens
        tRatio=float(len(tNumberList))/self.nTargetTokens
        return sRatio,tRatio
    
    
        
        
        
    def __init__(self, nSourceTokens,nTargetTokens,nbDict):
      self.nSourceTokens= nSourceTokens
      self.nTargetTokens= nTargetTokens
      self.nbDict=nbDict


class WordMappings:
   """Manage the Mappings resulted from Fast Align Alignments"""
   
   
   def getNTokens(self):
    """Get the number of tokens in source and target"""
    
    source,target=self.sentenceAlignedLine.split(" ||| ")
    sTokList=source.split(" ")
    tTokList=target.split(" ")
    self.nSourceTokens=len(sTokList)
    self.nTargetTokens=len(tTokList)
   
    return self.nSourceTokens,self.nTargetTokens
   
   def getMappings(self):
    """Get the Word Mappings in a dictionary"""
    
    nbDict={}
    wdMapSir=""
    source,target=self.sentenceAlignedLine.split(" ||| ")
    sTokList=source.split(" ")
    tTokList=target.split(" ")
    
    if self.wordAlignedLine :
        alignList=self.wordAlignedLine.split(" ")
        
        for pair in alignList:
            lindex,rindex=pair.split("-")
            lindex=int(lindex)
            rindex=int(rindex)
            if lindex not in nbDict :
                nbDict[lindex]={}
            nbDict[lindex][rindex]=0
                
        
        for lindex in sorted(nbDict.keys()):
            for rindex in nbDict[lindex]:
                wdMapSir+=sTokList[int(lindex)]+"->"+tTokList[int(rindex)]+";"
            
    return nbDict,wdMapSir
    
     
   def __init__(self, sentenceAlignedLine,wordAlignedLine):
      self.sentenceAlignedLine = sentenceAlignedLine
      self.wordAlignedLine = wordAlignedLine



def debugAlignment():
    """It debugs an alignment."""


 
   
def main():
    
    
    
    print "Results in =>"+outputFile
    
if __name__ == '__main__':
  main()     
    
   