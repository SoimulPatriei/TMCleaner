#!/usr/bin/env python


"""It uses MMT API  alignments and tokens for a translation unit."""
   
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
import Parameters
from urlparse import urljoin
import json


def isJson(myjson):
  try:
    json.loads(myjson)
  except ValueError, e:
    return False
  return True


def parseJson (jsonAnswer) :
    """It parses the json answer"""
    
    if isJson (jsonAnswer) :
        jsonParsed= json.loads(jsonAnswer)
        data=jsonParsed["data"]
        print data["sourceToken"]
        print data["targetToken"]
        for alignment in data["alignments"] :
            print alignment
    


def testMany (fTest,fOut,sLanguage,tLanguage) :
    """Test with translations units """
    
    fi = codecs.open( fTest, "r", "utf-8")
    fo = codecs.open( fOut, "w", "utf-8")
    for line in fi :
        line=line.rstrip()
        components=line.split("@#@")
        sSegmentU=components[0]
        tSegmentU=components[1]
        testOne(sSegmentU,tSegmentU,sLanguage,tLanguage,fo)
    fi.close()
    fo.close()
    

def testOne (sSegmentU,tSegmentU,sLanguage,tLanguage,fo) :
    """Test with one translation unit """
    
    mmt=MMTAlignments(sSegmentU.encode('utf-8'),tSegmentU.encode('utf-8'),sLanguage,tLanguage)
    jsonAnswer=mmt.getAlignments()
    jsonAnswerU=jsonAnswer.decode('utf-8')
    fo.write(sSegmentU+"@#@"+tSegmentU+"@#@"+jsonAnswerU+"\n")
    
    


class MMTAlignments:
   """Use MMT API to get the alignments and tokens for a translation unit."""
   
   
   def clean (self,segment) :
    """Clean the segments from symbols that generate exceptions  """
    
    segment=re.sub("\%","",segment)
    segment=re.sub("=","",segment)
    
    return segment
   
   def __init__(self,sSegment,tSegment,sLanguage,tLanguage ):
    self.sSegment=self.clean(sSegment)
    self.tSegment=self.clean(tSegment)
    self.sLanguage=sLanguage
    self.tLanguage=tLanguage
    
    
   def getAlignments (self) :
    "Get the alignments and tokens for source and target segments. Source and target should be encoded to utf-8"
    
    fMMT="Parameters/Fastalign/p-MMT.txt"
    pDict=Parameters.readParameters(fMMT)
    sLangUrl=self.sLanguage+"-"+self.sLanguage.upper()
    tLangUrl=self.tLanguage+"-"+self.tLanguage.upper()
    #----------------to preculde % problem URL encoding---------------------------------
    sEncodeSegment=urllib.quote(self.sSegment)
    tEncodeSegment=urllib.quote(self.tSegment)
    parameters="?"+"sl="+sLangUrl+"&tl="+tLangUrl+"&s="+sEncodeSegment+"&t="+tEncodeSegment+"&d=true"
    pDict["endpoint"]=re.sub(r'/$','',pDict["endpoint"])
    urlParameters=pDict["endpoint"]+parameters
    jsonAnswer="Default"
    try :  
      jsonAnswer=urllib2.urlopen(urlParameters).read()
    except Exception as e:
        myError="@#@".join([str(e),urlParameters])
        logging.error(myError)
    return jsonAnswer


def main():
    
    
    print "=========Extract Alignments for Large Sets==============="
    fTest=sys.argv[1]
    fOut=sys.argv[2]
    sLanguage=sys.argv[3]
    tLanguage=sys.argv[4]
    testMany (fTest,fOut,sLanguage,tLanguage)
    print "Results in =>"+fOut
    
    
    
    
if __name__ == '__main__':
  main()

    