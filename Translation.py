#!/usr/bin/env python

"""Use a Machine Translation engine to translate the source segment and
   compute features based on the similarity
   between source and the translation of the source"""
   
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"



import logging
import sys
import codecs
import collections
import math
import urllib2
import urllib
import re
import string
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Translate:
   """Use a Machine Translation engine to translate the source segment
   and compute features based on the similarity between source and the translation of the source."""
   
   
   def __init__(self,fSegments,fTranslations,sLanguage,tLanguage ):
    self.fSegments=fSegments
    self.fTranslations=fTranslations
    self.sLanguage=sLanguage
    self.tLanguage=tLanguage
    
   def removePunctuation (self,segment) :
    """It removes the punctuation from a segment.
     In this way increases the probability of good similarity match."""
     
    punctList=list(string.punctuation)
    for punct in punctList :
        segment=segment.replace(punct," ")
    return segment    
   
   def getSegmentWordList (self,segment) :
    "Gets the word list of segment for the purpose of computing the cosine similarity"
    
    segment=re.sub("^\s+","",segment)
    segment=re.sub("\s+$","",segment)
    
    segmentList=re.split("\s+",segment)
    segmentListPruned=[];
    punctuationSigns=[".","?","!",":",";","-","(",")","[","]","'",'"',"/",",","+"]
    for el in segmentList :
        if not (el in punctuationSigns) :
            segmentListPruned.append(el)
    return segmentListPruned
   
   def prepareVectors (self,sourceVect,destVect) :
    """Prepare the vectors to for cosine similarity function """
    
    X=np.asarray(sourceVect).reshape(1,-1)
    Y=np.asarray(destVect).reshape(1,-1)
    
    return X,Y
   
   def getVector (self,uniqueFeatureList, featureDict) :
    "Get the vectors to be used in the computation of cosine similarity"
    
    vector=[]
    for feature in uniqueFeatureList :
        if  feature in featureDict :
            vector.append(featureDict[feature])
        else :
            vector.append(0)
            
    return vector

   def getSegmentSimilarity (self,sSegment,tSegment) :
    """It gets the cosine similarity between the translation of the source segment and the target segment"""
    
    
    for sourceSegmentTranslated,e in self.getBingTranslation (sSegment):
        if e:
            logging.error( "Got a translation exception %s" %e)
            return 0,0
        else :
            sourceSegmentTranslated=unicode(sourceSegmentTranslated,"UTF-8")
            sourceSegmentTranslatedLower=self.removePunctuation (sourceSegmentTranslated.lower())
            sourceSegmentTranslatedPrunedList=self.getSegmentWordList (sourceSegmentTranslatedLower)
            
            
            targetSegmentP=self.removePunctuation (tSegment.lower())
            targetSegmentPrunedList=self.getSegmentWordList (targetSegmentP)
            
            
            uniqueFeatureList=list(set(targetSegmentPrunedList+sourceSegmentTranslatedPrunedList))
            sourceDict=Counter(sourceSegmentTranslatedPrunedList)
            destDict=Counter(targetSegmentPrunedList)
            
            sourceVect=self.getVector(uniqueFeatureList,sourceDict)
            destVect=self.getVector(uniqueFeatureList,destDict)
            X,Y=self.prepareVectors (sourceVect,destVect)
            cosineSimilarity=cosine_similarity(X,Y)
            
            return (sourceSegmentTranslated,cosineSimilarity[0][0])   
   
   def getTranslationSimilarity(self):
    fi = codecs.open( self.fSegments, "r", "utf-8")
    scoreTranslation={}
    
    fo = codecs.open( self.fTranslations, "w", "utf-8")
    
    for line in fi:
        line=line.rstrip()
        components=line.split("@#@")
        key=components[0]+"-"+components[1]
        sSegment=components[2]
        tSegment=components[3]
        sourceSegmentTranslated,score=self.getSegmentSimilarity(sSegment,tSegment)
        if sourceSegmentTranslated ==0 :
            sourceSegmentTranslated="Got Exception"
        fo.write(key+"@#@"+sourceSegmentTranslated+"@#@"+str(round(score,2))+"\n")
        scoreTranslation[key]=round(score,2)
    fi.close()
    fo.close()
    return scoreTranslation    
    
   def addFeatures (self,segmentFeaturesDict) :
        """Add features to the dictionary."""
        
        scoreTranslation=self.getTranslationSimilarity()
        for key in segmentFeaturesDict:
          if key in scoreTranslation :
             segmentFeaturesDict[key]["simscore"]=scoreTranslation[key]
          else :
              segmentFeaturesDict[key]["simscore"]=0
        
   def getBingTranslation (self,sSegment) :
    "Get the source Segment translation using BING API"
    
    fBing="Parameters/p-Bing.txt"
    pDict=Parameters.readParameters(fBing)
    try :
        sSegment=urllib.quote(sSegment.encode("utf-8"))
        parameters="&from="+self.sLanguage+"&to="+self.tLanguage+"&text="+sSegment
        url=pDict["bingAPI"]+pDict["key"]+parameters
        answer=urllib2.urlopen(url).read()
        pattern="""<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">(.+)</string>"""
        m = re.search(pattern, answer)
        tSegment="Error#"
        if m :
            tSegment=m.group(1)
    except Exception as e:
        yield (None ,e)
    else :
        yield(tSegment,None)
        
               
def testSet():
    """The Test set in a dict """
    
    tDict= {"yeah, hurricane selina.":"- Gia'. L'uragano Selina",
           "uh-oh, wait a minute.":"Oh, aspettate un attimo.",
            "does that exist, hurricane selina?":"Ma esiste? L'uragano Selina?",
            "- oh, i don't-- - can we run a check on that?":"- Oh, non... - Possiamo controllare?"}
    
    return tDict

def getSegmentFeatures(fSegments):
    """Simulates a segment features dict """
    
    segmentFeaturesDict={}
    fi = codecs.open(fSegments, "r", "utf-8")
    for line in fi:
        line=line.rstrip()
        components=line.split("@#@")
        key=components[0]+"-"+components[1]
        segmentFeaturesDict[key]={}
        segmentFeaturesDict[key]["fakeFeature"]=0
    fi.close()
    return segmentFeaturesDict 
    


def main():
    sLanguage="en"
    tLanguage="it"
    fSegments="TestFiles/split-618.txt"
    fTranslations="translations.txt"
    
    print "Translate and Compute Similarity"
    segmentFeaturesDict=getSegmentFeatures(fSegments)
    tr=Translate(fSegments,fTranslations,sLanguage,tLanguage)
    tr.addFeatures(segmentFeaturesDict)
    print "Done"
    
    

if __name__ == '__main__':
  main()


        
