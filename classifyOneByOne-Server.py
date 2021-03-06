#!/usr/bin/env python


"""This script should be used as a web service
   when it classify a source and target segment."""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
from Features import *
import codecs
import re
import collections
import time
import logging
import os
from os.path import split
from os import listdir
from os.path import isfile, join,isdir
import shutil
import argparse
from GetFeatures import *
from Rules import *
from Classification import *
import Parameters
from LanguageDetectionLine import *
from Tokenizer import *
from FastAlign import *
from FeaturesFastAlign import *
import time
import json
import cherrypy
from cherrypy import tools
import os
import signal
import argparse


def initLogger(loggingFile):
    """Init the logger for the console and logging file"""
    
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=loggingFile,
                        filemode='w')
    
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    
    console.setFormatter(formatter)
    
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)    



    
    
    
def fireRules(lineSegment,pDict):
    """Fire the extra rules ..."""
    
    
    components=lineSegment.split("@#@")
    
    rl=Rules(components[2],components[3])
    
    if rl.ruleNumbers() ==(True,"Number") :
        return True,"NumberRule","1"
    
    elif rl.ruleNumbers() ==(False,"Number") :
        return True,"NumberRule","0"
    
    if rl.ruleSame() :
        return True, "SameRule","1"
    
    if rl.ruleNameEntities() :
        return True, "NameEntitiesRule","1"
    
    if rl.ruleIdenticalLC(components,pDict) :
        return True,"LanguageRule","0"
    
    if rl.ruleCG() :
        return True,"ChurchGale","0"
    
    return False,"",""


def construcLD (pDict) :
    """Construct the language detector"""
    
    pDict ={"javaClassPath":"Resources/idLanguage.jar",
            "javaClass":"test.translated.net.DetectLanguageString",
            "langProfileDirectory":"Resources/profiles.sm"}
    commandList=["java","-cp",pDict["javaClassPath"],pDict["javaClass"],pDict["langProfileDirectory"]]
    command=" ".join(commandList)
    logging.debug(command)
    
    master, slave = pty.openpty()
    ld = subprocess.Popen(command,shell=True,stdin=PIPE,stdout=slave)
    stdin_ld = ld.stdin
    stdout_ld = os.fdopen(master)
    return ld,stdin_ld,stdout_ld

def getCorrectOrder (featureTrainingNames,featuresDict) :
    """Get Correct Order of the Test features"""
    
    X=[]
    for featureName in featureTrainingNames :
        if featureName in featuresDict :
            X.append(featuresDict[featureName])
    logging.debug(X)        
    X = np.array(X)
    
    return X.reshape(1, -1)


def decideClass(pDict,listPred):
      """Decide the class based on probability scores """
      
      threshold=float(pDict["threshold"])
      classRes=int(pDict["defaultClass"])
      if listPred[1-classRes]>threshold :
         classRes=1-classRes
      return classRes



def classify(argDict,pDict):
    """Classify the source segment and target segment."""
    
    resDict={}
    resDict["rule"]="default"
    resDict["classRes"]="default"
    resDict["classesPred"]="default"
    
    sSegment=argDict["sourceSegment"]
    tSegment=argDict["targetSegment"]

    logging.debug("Generate Test Features")
    
    logging.debug("Perform LI")
    ldl=argDict["languageDetector"]
    
    #-----Make a line as the one you read from the file-----     
    langString=ldl.run(sSegment,tSegment)
    sDetectLang,tDetectLang=langString.split("@#@")
    components=["0","0",sSegment,tSegment,sDetectLang,tDetectLang]
    lineSegment="@#@".join(components)

   
    logging.debug("Apply the rules")
    isRule,rule,value=fireRules(lineSegment,pDict)
    if (isRule) :
        resDict["rule"]=rule
        resDict["classRes"]=value
        return resDict
    else :
        logging.debug("We classify using ML")
        gf=GetFeatures()
        featuresDict=gf.generateFeaturesLine (lineSegment,pDict)
        fa=FeaturesFastAlignLine(argDict,pDict)
        getCorrectOrder
        fa.addFeatures(featuresDict)
        X=getCorrectOrder (argDict["featureTrainingNames"],featuresDict)
        predictProbabilities=argDict["classifier"].predict_proba(X)
        classesPred=str(round(predictProbabilities[0][0],2))+"-"+str(round(predictProbabilities[0][1],2))
        classRes=decideClass(pDict,predictProbabilities[0])
        resDict["rule"]="ML"
        resDict["classRes"]=str(classRes)
        resDict["classesPred"]=classesPred
        return resDict
    
    
def getParametersFile (argDict) :
    """Get the Parameters File based
       on  input and output Language Codes"""
    
    mappingFile="map.txt"
    pFile=""
    fi = codecs.open( mappingFile, "r", "utf-8")
    for line in fi :
        line=line.rstrip()
        components=line.split("\t")
        if components[0]==argDict["sourceLanguage"] and components[1]==argDict["targetLanguage"] :
            pFile=components[2]
            break
    fi.close()
    return pFile


def getLogisticRegressionClassifier (pDict) :
        """Fit the Logistic Regression algorithm to data"""
        
        pDict["trainingFile"]=pDict["trainingFeatureFile"]
        ld=LoadData(pDict)
        X,y=ld.loadTrainingDataSet()
        tm=TrainModels(X,y)
        clf=tm.getModelLogistic()
        featureTrainingNames=ld.feature_training_names
        return clf,featureTrainingNames

def printFeatureNames (featureTrainingNames) :
        """Test print feature names."""
        fString=""
        for feature in featureTrainingNames :
            fString+=feature+"\t"
        fString=fString.rstrip()    
        print (fString)    

def loadSoftwareResources (argDict,pDict) :
    """Get the in memory software that will be used in classification."""

    logging.info("=======Load the Logistic Regression classifier =======")
    clf,featureTrainingNames=getLogisticRegressionClassifier(pDict)
    argDict["classifier"]=clf
    argDict["featureTrainingNames"]=featureTrainingNames
    logging.info("=======Classifier loaded======")
    
    logging.info("================Load Language Detector==========================")
    argDict["languageDetector"]=LanguageDetectionLine(pDict)
    logging.info("================Language Detector Loaded=========================")
    
    logging.info("================Load the Merge class=========================")
    argDict["mergeLine"]=MergeLine(pDict["javaClassPathSym"],pDict["javaClassSymLine"])
    logging.info("=================Merge Class Loaded=====================")
    
    logging.info("==============Load Tokenizers for Source and Target==========================")
    argDict["tokenizerSource"]=TokenizerLine(pDict["sourceLanguage"])
    argDict["tokenizerTarget"]=TokenizerLine(pDict["targetLanguage"])
    logging.info("==========================Tokenizers Loaded===================================")
    
    logging.info("===============Load Fastalign Forward and Backward models========================")
    argDict["faForward"]=FastAlignLine("fa.flags.forward",pDict["faForwardModel"])
    argDict["faBackward"]=FastAlignLine("fa.flags.backward",pDict["faBackwardModel"])
    logging.info("================Sleep==================================")
    time.sleep(15)
    logging.info("================Fastalign Loaded==================================")
    
    
    
def terminate () :
    """Correctly terminate the language detector and the merge script."""
    
    terminator="@##@10951@##@"
    logging.debug ("Sleep 5 seconds")
    time.sleep(5)
    logging.debug("I wake up and terminate scan processes")
    argDict["languageDetector"].terminate(terminator)
    argDict["mergeLine"].terminate(terminator)
    logging.debug ("Language Detector and Merge Script terminated.")
    

def getQueriesFromFile (fileTest,argDict,pDict) :
    """Get queries from file"""
    
    fi = codecs.open(fileTest, "r", "utf-8")
    for line in fi :
        line=line.rstrip()
        components=line.split("@#@")
        sourceSegment=components[2]
        targetSegment=components[3]
        logging.debug(sourceSegment+"@#@"+targetSegment +"\n")
        argDict["sourceSegment"]=sourceSegment.encode('utf-8')
        argDict["targetSegment"]=targetSegment.encode('utf-8')
        resDict=classify(argDict,pDict)
        logging.debug("Rule :"+resDict["rule"])
        logging.debug("Class Result :"+resDict["classRes"])
        raw_input("Press Enter to continue...")
        
    fi.close()


def initResources (pFile) :
    """Init Resources ..."""
    
    cherrypy.log.access_log.propagate = False
    loggingFile="onebyone-Server.log"
    initLogger(loggingFile)
    argDict={}
    argDict["pFile"]=pFile
    pDict=Parameters.readParameters (argDict["pFile"])
    loadSoftwareResources (argDict,pDict)
    return argDict,pDict

def error_page_404(status, message, traceback, version):
    return "404 Error!"

def getJsonAnswer (resDict) :
    """Get the Json Answer"""
    json=""
    for k, v in resDict.items() :
        keyvalue = '"'+k+'"'+":"+'"'+v+'"' +","
        json+=keyvalue
    json=json[:-1]
    json="{"+json + "}"
    
    return json

def initResourcesTest (pFile) :
    """Init Resources ..."""
    
    loggingFile="onebyone-Server.log"
    initLogger(loggingFile)
    argDict={}
    argDict["pFile"]=pFile
    pDict=Parameters.readParameters (argDict["pFile"])
    return argDict,pDict

def shutdownProcess (pid,duration, message) :
        """Gracefully shutdown a process loaded in memory"""
        
        logging.info(message+" with pid:"+str(pid)+" in seconds:"+str(duration))
        time.sleep(duration)
        os.killpg(pid, signal.SIGTERM)
        logging.info("Process killed!")

        
class HomeController():
    
    def __init__(self, argDict,pDict):
        self.argDict=argDict
        self.pDict=pDict
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def classifyApp(self, **kwargs):
        input_json = cherrypy.request.json
        sourceSegment=input_json["sourceSegment"]
        targetSegment=input_json["targetSegment"]
        self.argDict["sourceSegment"]=sourceSegment.encode('utf-8')
        self.argDict["targetSegment"]=targetSegment.encode('utf-8')
        resDict=classify(self.argDict,self.pDict)
        return resDict
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def classifyTest(self, **kwargs):
        input_json = cherrypy.request.json
        sourceSegment=input_json["sourceSegment"]
        targetSegment=input_json["targetSegment"]
        resDict={}
        resDict["rule"]="default"
        resDict["classRes"]="default"
        resDict["classesPred"]="default"
        return resDict
    
    
    @cherrypy.expose
    def shutdown(self):
        
        duration=1
        logging.debug("Shutdown the processes loaded in memory and the service")
        
        shutdownProcess (self.argDict["languageDetector"].ld.pid,duration, "Kill Language Detector")
        shutdownProcess (self.argDict["mergeLine"].merge.pid,duration, "Kill Merger")
        shutdownProcess (self.argDict["tokenizerSource"].tokenizer.pid,duration, "Kill Tokenizer Source")
        shutdownProcess (self.argDict["tokenizerTarget"].tokenizer.pid,duration, "Kill Tokenizer Target")
        shutdownProcess (self.argDict["faForward"].fa.pid,duration,"Kill Fastalign Forward")
        shutdownProcess (self.argDict["faBackward"].fa.pid,duration,"Kill Fastalign Backward")
        cherrypy.engine.exit()
        
    @cherrypy.expose
    def shutdownTest(self):
        logging.debug("Test: shutdown the service")
        cherrypy.engine.exit()         
        
        

def start_server(port,pFile):
    
    argDict,pDict=initResources (pFile)
    hc=HomeController(argDict,pDict)
    cherrypy.tree.mount(hc, '/')
    cherrypy.config.update({'error_page.404': error_page_404})
    cherrypy.config.update({'server.socket_host': '0.0.0.0'} )  
    cherrypy.config.update({'server.socket_port': port})
    cherrypy.engine.start()

def executeServer():
        """Parse the arguments using argparse and execute the web service"""
        
        parser = argparse.ArgumentParser(description='Start the web service with the configuration file for a language pair')
        parser.add_argument("--config",type=str, help="The configuration file")
        parser.add_argument("--port",type=int, help="The port of the web service")
        
        args = parser.parse_args()
        start_server(args.port,args.config)
        

def main():
    
    executeServer()
    

if __name__ == '__main__':
  main()
  