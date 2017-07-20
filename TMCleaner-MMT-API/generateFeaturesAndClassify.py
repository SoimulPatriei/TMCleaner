#!/usr/bin/env python


"""The main script for performing training or classification"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import storeFeatures
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
from ExtraRules import *
from Classification import *
import Parameters



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



def getLanguageForSegmentFile (pDict) :
    commandList=["java" ,"-cp",pDict["javaClassPath"],pDict["javaClass"],
                 pDict["segmentsFile"],pDict["sourceLanguage"],
                 pDict["targetLanguage"],pDict["langProfileDirectory"]]
    logging.info (" ".join(commandList))
    pDict["segmentsLangFile"]=pDict["segmentsFile"]+".lang.txt"
    call(commandList)



def performLI(pDict):
    """It performs language identification for the Bisegments"""
    
    startLI=time.time()
    getLanguageForSegmentFile (pDict)
    endLI=time.time()
    timeLI=endLI-startLI
    logging.info("====>Time LI:"+str(timeLI))
    
 

def getFeatureFilePath (tFile):
    """Get Feature File Full Path """
    
    featureFile=re.sub(".txt$","-Features.csv",tFile)
    featureFP=os.path.abspath(featureFile)
    return featureFP



def makeDirectories(pBatch):
    """Make classification Directory where I add classification files """
    
    pBatch["dirClassified"]=join(pBatch["dirTest"],"Classified")
    if os.path.exists(pBatch["dirClassified"]):
        shutil.rmtree(pBatch["dirClassified"])
        
    os.makedirs(pBatch["dirClassified"])
    
    if "translation" in pBatch and pBatch["translation"] =="yes" :
        pBatch["dirTranslation"]=join(pBatch["dirTest"],"Translated")
        if os.path.exists(pBatch["dirTranslation"]):
            shutil.rmtree(pBatch["dirTranslation"])
        os.makedirs(pBatch["dirTranslation"])
        
     
            
def moveFiles (pBatch,testFPath) :
    """Move the classified file and delete the intermediary files """
    
    allFPath = [ join(pBatch["dirTest"],curFile) for curFile in listdir(pBatch["dirTest"]) if isfile(join(pBatch["dirTest"],curFile)) ]
    for curFile in allFPath:
        curFilePath=os.path.abspath(curFile)
        if curFilePath == pBatch["classifiedFile"] :
            shutil.move(curFile,pBatch["dirClassified"])
        elif curFilePath==pBatch["testFeatureFile"] :
            shutil.move(curFile,pBatch["dirClassified"])
        elif "translation" in pBatch and pBatch["translation"] =="yes" and curFilePath == os.path.abspath (pBatch["translationFile"]) :
            shutil.move(curFile,pBatch["dirTranslation"])
        elif curFile in testFPath :
            pass
        else :
            os.remove(curFile)



def fireExtraRules(source, target,pBatch) :
    """Here you fire the extra rules addded to accomodate the test sets of Luca and Francesco """
    
    rl=ExtraRules(source,target,pBatch)
    if rl.ruleAbreviation() :
        return True, "abreviationRule","1"
    
    if rl.ruleAlignment () :
        return True, "alignmentRule","1"
    
    return False,"",""


def fireRules(components,pBatch):
    """Fire the extra rules ..."""
    
    source=components[2].encode('utf-8')
    target=components[3].encode('utf-8')
    
    #booolean,rule,value=fireExtraRules(source,target,pBatch)
    #if rule :
    #   return booolean,rule,value
    
    rl=Rules(source,target)
    
    if rl.ruleNumbers() ==(True,"Number") :
        return True,"NumberRule","1"
    
    elif rl.ruleNumbers() ==(False,"Number") :
        return True,"NumberRule","0"
    
    if rl.ruleSame() :
        return True, "SameRule","1"
    
    if rl.ruleNameEntities() :
        return True, "NameEntitiesRule","1"
    
    if rl.ruleIdenticalLC(components,pBatch) :
        return True,"LanguageRule","0"
    
    if rl.ruleCG() :
        return True,"ChurchGale","0"
    
    return False,"",""  
    
 
def applyRules (pBatch) :
    """Apply extra rules before the Machine Learning Algorithm
    to add labels to some bisegments that you are sure they are true or false."""

    segmentsLangFile=pBatch["segmentsLangFile"]
    ruleFile=segmentsLangFile+"-rl.txt"
    restFile=segmentsLangFile+"-lan.txt"
    
    fi = codecs.open( segmentsLangFile, "r", "utf-8")
    fo1 = codecs.open( ruleFile, "w", "utf-8")
    fo2 = codecs.open( restFile, "w", "utf-8")
    
    pBatch["ruleFile"]=ruleFile
    
    nIndex=-1
    for line in fi:
        line=line.rstrip()
        components=line.split("@#@")
        ok,ruleFired,res=fireRules(components,pBatch)
        if ok :
            table=[]
            table.append(components[0])
            table.append(components[1])
            table.append(ruleFired)
            table.append(res)
            fo1.write("@#@".join(table)+"\n")
        else :
            fo1.write(components[0]+"\n")
            nIndex+=1
            components[0]=str(nIndex)
            components[1]=str(nIndex)
            fo2.write("@#@".join(components)+"\n")
                      
        
    fi.close()
    fo1.close()
    fo2.close()
    
    shutil.move(restFile, segmentsLangFile)
    
def concatenate (fClassification,fRule) :
    """Concatenate the classified file by machine learning with your rule file """
    
    fConcat=fClassification+".txt"
    fr = codecs.open(fRule, "r", "utf-8")
    fc = codecs.open( fClassification, "r", "utf-8")
    fo = codecs.open( fConcat, "w", "utf-8")
    
    fr = codecs.open(fRule, "r", "utf-8")
    for lineRule in fr:
        lineRule=lineRule.rstrip()
        if re.search("@#@",lineRule) :
            fo.write(lineRule+"\n")
        else :
            components=fc.readline().rstrip().split("@#@")
            components[0]=components[1]=lineRule
            fo.write("@#@".join(components)+"\n")
    
    fc.close()
    fr.close()
    fo.close()
    
    shutil.move(fConcat, fClassification)


def getFunction(mlalgorithm,pDict):
    """get the function corresponding to the algorithm passed as parameter."""
    
    algList=["SVM", "RandomForest", "DecisionTree", "LogisticRegression","KNearstNeighbors"]
    cl=Classification(pDict)
    
    options={
    "SVM":cl.fitSVM,
    "RandomForest":cl.fitRandomForest,
    "DecisionTree":cl.fitDecisionTree,
    "LogisticRegression":cl.fitLogisticRegression,
    "KNearstNeighbors":cl.fitKNearNeighbors
    }
    
    return options[mlalgorithm]



def classifyInBatch(fPBatch,withRules,mlalgorithm):
    """Classify the files found in directory one by one.
       It can be specified if you use the extra rules or not. """
    
    pBatch=Parameters.readParameters (fPBatch)
    makeDirectories(pBatch)
    
    testFPath = [ join(pBatch["dirTest"],curFile) for curFile in listdir(pBatch["dirTest"]) if isfile(join(pBatch["dirTest"],curFile)) and curFile.endswith(".txt")]
   
    for tFile in testFPath:
        
        logging.info("Generate Test Features =>"+tFile)
        pBatch["testFeatureFile"]=getFeatureFilePath(tFile)
        pBatch["segmentsFile"]=tFile
        
        logging.info("Perform LI")
        performLI(pBatch)
        
        if (withRules == "yes") :
            logging.info("Apply the rules")
            applyRules(pBatch)
        else :
            logging.info ("No rules")
         
        logging.info("We classify using ML")
        gf=GetFeatures()
        gf.generateTestFeatures(pBatch)
        
        pBatch["trainingFile"]=pBatch["trainingFeatureFile"]
        pBatch["testFile"]=pBatch["testFeatureFile"]
    
        logging.info("Fit the ML algorithm :"+mlalgorithm)
        getFunction(mlalgorithm,pBatch)()
        
        if (withRules=="yes") :
            logging.info("Unify Rule Based and Classification File")
            concatenate (pBatch["classifiedFile"],pBatch["ruleFile"])
            
        logging.info("Move everything in the Classified directory.")    
        moveFiles (pBatch,testFPath)
        
def getAlgorithm(mlalgorithm):
    """Treat the machine learning algorithm provided"""
    
    algList=["SVM", "RandomForest", "DecisionTree", "LogisticRegression","KNearstNeighbors"]
    
    if mlalgorithm :    
        if mlalgorithm in algList :
            return mlalgorithm
        else:
            sys.exit("Unknown algorithm or algorithm not implemented")
    else :
        return "SVM"

def treatRules(rules):
    """Treat the rules """
    
    if rules :
        return rules
    else :
        return "yes"

 
def executeProgram():
    """Parse the arguments of the program using argparse and execute the program ..."""
    
    parser = argparse.ArgumentParser(description='You can either (obtain the feature file for training data) or (classify using the model.)')
    parser.add_argument("--features",action="store_true",help="I tell the tool to obtain the training features")
    parser.add_argument("--classify",action="store_true",help="I tell the tool to classify")
    parser.add_argument("--config",type=str, help="The file that stores parameters for training or classification")
    parser.add_argument("--translation",type=str, help="The file that stores parameters for translation")
    parser.add_argument("--rules",nargs='?',type=str,help=" 'no' if you do not want to use the rules in classification. default: 'yes'.")
    parser.add_argument("--mlalgorithm",nargs='?',type=str, help="""The ML algorithm to use for classification.
                        One of : {SVM, RandomForest, DecisionTree, LogisticRegression,KNearstNeighbors}.
                        Of course you can add any other ML algorithm implemented in scikit-learn.""")
    
    args = parser.parse_args()
    
    
    if args.features and args.config :
        loggingFile="train.log"
        initLogger(loggingFile)
        gf=GetFeatures(args.config)
        gf.generateTrainingFeatures()    
    elif args.classify and args.config:
        loggingFile="test.log"
        initLogger(loggingFile)
        mlalgorithm=getAlgorithm(args.mlalgorithm)
        rules=treatRules(args.rules)
        
        logging.info("Start Classification")
        classifyInBatch(args.config,rules,mlalgorithm)
        logging.info("End Classification")
    else :
        logging.error( "Wrong arguments! You can either Train OR Classify.")
    
    

def main():
    
#    Run the program.
#	1. Training => --features --config Parameters/Fastalign/p-Training-Italian.txt
#	2. Classify     =>  --classify --config Parameters/Fastalign/p-Test-Italian.txt --mlalgorithm LogisticRegression
  
    startC=time.time()
    executeProgram()
    endC=time.time()
    timeC=endC-startC
    logging.info("Time Whole Program=>:"+str(timeC))
    print ("End")
    


if __name__ == '__main__':
  main()
  