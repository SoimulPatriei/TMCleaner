#!/usr/bin/env python


"""This script it is the command line test of the web service that classify
   the segments one by one.
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
from FeaturesFastAlign import *
import time
import json
import os
import signal
from ExtraRules import *


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



def fireExtraRules(source, target,pBatch) :
    """Here you fire the extra rules addded to accomodate the test sets of Luca and Francesco """
    
    rl=ExtraRules(source,target,pBatch)
    if rl.ruleAbreviation() :
        return True, "abreviationRule","1"
    
    if rl.ruleAlignment () :
        return True, "alignmentRule","1"
    
    return False,"",""

    
    
    
def fireRules(lineSegment,pDict):
    """Fire the extra rules ..."""
    
    
    components=lineSegment.split("@#@")
    source=components[2]
    target=components[3]
    
    booolean,rule,value=fireExtraRules(source,target,pDict)
    if rule :
        return booolean,rule,value
    
    rl=Rules(source,target)
    
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
    logging.info(command)
    
    master, slave = pty.openpty()
    ld = subprocess.Popen(command,shell=True,stdin=PIPE,stdout=slave)
    stdin_ld = ld.stdin
    stdout_ld = os.fdopen(master)
    return ld,stdin_ld,stdout_ld



def testScaling(X,scaler):
    """Variance Scale for the test set """
        
    X_transform=scaler.transform(X)
    return X_transform

def getCorrectOrder (featureTrainingNames,featuresDict,scaler) :
    """Get Correct Order of the Test features"""
    
    X=[]
    for featureName in featureTrainingNames :
        if featureName in featuresDict :
            X.append(featuresDict[featureName])
    logging.info(X)        
    X = np.array(X)
    
    #apply feature scaling to test data
    X=X.reshape(1, -1)
    X_transform=testScaling(X,scaler)
    
    return X_transform



def decideClass(pDict,listPred):
      """Decide the class based on probability scores """
      
      threshold=float(pDict["threshold"])
      classRes=int(pDict["defaultClass"])
      if listPred[1-classRes]>threshold :
         classRes=1-classRes
      return classRes



def notProbClassifier (y) :
    """In case of a classfier that does not return probabilities for classes
    return a fake probability string "0-1" or "1-0" """
    
    classesPred="1-0"
    if y :
        classesPred="0-1"
    return classesPred
    

def classify(argDict,pDict):
    """Classify the source segment and target segment."""
    
    resDict={}
    resDict["rule"]="default"
    resDict["classRes"]="default"
    resDict["classesPred"]="default"
    
    sSegment=argDict["sourceSegment"]
    tSegment=argDict["targetSegment"]

    logging.info("Generate Test Features")
    
    logging.info("Perform LI")
    ldl=argDict["languageDetector"]
    
    #-----Make a line as the one you read from the file-----     
    langString=ldl.run(sSegment,tSegment)
    sDetectLang,tDetectLang=langString.split("@#@")
    components=["0","0",sSegment,tSegment,sDetectLang,tDetectLang]
    lineSegment="@#@".join(components)

   
    logging.info("Apply the rules")
    isRule,rule,value=fireRules(lineSegment,pDict)
    if (isRule) :
        resDict["rule"]=rule
        resDict["classRes"]=value
        return resDict
    else :
        logging.info("We classify using ML")
        gf=GetFeatures()
        featuresDict=gf.generateFeaturesLine (lineSegment,pDict)
        fa=FeaturesFastAlignLine(argDict,pDict)
        fa.addFeatures(featuresDict)
        X=getCorrectOrder (argDict["featureTrainingNames"],featuresDict,argDict["scaler"])
        classRes=int(argDict["classifier"].predict(X)[0])
        #This is the case of logistic regression where you can predict probabilities for classes
        #predictProbabilities=argDict["classifier"].predict_proba(X)
        #classesPred=str(round(predictProbabilities[0][0],2))+"-"+str(round(predictProbabilities[0][1],2))
        #classRes=decideClass(pDict,predictProbabilities[0])
        resDict["rule"]="ML"
        classesPred=notProbClassifier (classRes)
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


def getSVMClassifier (pDict) :
    """Fit the SVM algorithm to data"""
    
    pDict["trainingFile"]=pDict["trainingFeatureFile"]
    ld=LoadData(pDict)
    X,y=ld.loadTrainingDataSet()
    
    #get the variance scaler for the training data set
    scaler=ld.getScaler()
    tm=TrainModels(X,y)
    clf=tm.getSVM()
    featureTrainingNames=ld.feature_training_names
    return clf,featureTrainingNames,scaler



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

def loadSoftwareResources (argDict,pDict) :
    """Get the in memory software that will be used in classification."""
    
    logging.info("=======Load the SVM classifier =======")
    clf,featureTrainingNames,scaler=getSVMClassifier(pDict)
    argDict["classifier"]=clf
    argDict["scaler"]=scaler
    argDict["featureTrainingNames"]=featureTrainingNames
    logging.info("=======Classifier loaded======")
    
    logging.info("================Load Language Detector==========================")
    argDict["languageDetector"]=LanguageDetectionLine(pDict)
    logging.info("================Language Detector Loaded=========================")
    
    
def terminate () :
    """Correctly terminate the language detector and the merge script."""
    
    terminator="@##@10951@##@"
    logging.info ("Sleep 5 seconds")
    time.sleep(5)
    logging.info("I wake up and terminate scan processes")
    argDict["languageDetector"].terminate(terminator)
    argDict["mergeLine"].terminate(terminator)
    logging.info ("Language Detector and Merge Script terminated.")
    

def getQueriesFromFile (fileTest,argDict,pDict) :
    """Get queries from file"""
    
    fi = codecs.open(fileTest, "r", "utf-8")
    for line in fi :
        line=line.rstrip()
        components=line.split("@#@")
        sourceSegment=components[2]
        targetSegment=components[3]
        logging.info(sourceSegment+"@#@"+targetSegment +"\n")
        argDict["sourceSegment"]=sourceSegment.encode('utf-8')
        argDict["targetSegment"]=targetSegment.encode('utf-8')
        resDict=classify(argDict,pDict)
        logging.info("Rule :"+resDict["rule"])
        logging.info("Class Result :"+resDict["classRes"])
        raw_input("Press Enter to continue...")
        
    fi.close()
    


def shutdownProcess (pid,duration, message) :
    """Gracefully shutdown a process loaded in memory"""
    
    logging.info(message+" with pid:"+str(pid)+" in seconds:"+str(duration))
    time.sleep(duration)
    os.killpg(pid, signal.SIGTERM)
    logging.info("Process killed!")

    
def shutdown(argDict):
        
        duration=1
        logging.info("Shutdown the processes loaded in memory")
        shutdownProcess (argDict["languageDetector"].ld.pid,duration, "Kill Language Detector")


def initResources (pFile) :
    """Init Resources ..."""
    
    loggingFile="onebyone-CommandLine.log"
    initLogger(loggingFile)
    argDict={}
    argDict["pFile"]=pFile
    pDict=Parameters.readParameters (argDict["pFile"])
    loadSoftwareResources (argDict,pDict)
    return argDict,pDict

def getJsonAnswer (resDict) :
    """Get the Json Answer"""
    json=""
    for k, v in resDict.items() :
        keyvalue = '"'+k+'"'+":"+'"'+v+'"' +","
        json+=keyvalue
    json=json[:-1]
    json="{"+json + "}"
    
    return json
        



def main():
    
    fileTest="test-Luca-o.txt"
    pFile="Parameters/Fastalign/p-Test-Italian.txt"
    argDict,pDict=initResources(pFile)
    getQueriesFromFile (fileTest,argDict,pDict)
    shutdown(argDict)
    

if __name__ == '__main__':
  main()
  