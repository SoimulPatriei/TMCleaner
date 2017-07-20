#!/usr/bin/env python


"""The class calls various classification algorithms from scikit learn package """
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"


import sys
import re
import codecs
import sklearn as sk
import numpy as np
import csv
from LoadData import *
from Models import *
from Features import *
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.cross_validation import train_test_split
from sklearn import tree
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier
import storeFeatures
import logging

 

class Classification:
   """We run various classification algorithms. """
   
   
   def __init__(self,pDict):
      self.pDict = pDict
      self.probabilities=False
      
   def getNewFile (self,ending) :
    "Get the test csv file name"
    
    li=self.pDict["testFile"].rsplit(".csv",1)
    return ending.join(li)
   
   def decideClass(self,listPred):
      """Decide the class based on probability scores """
      
      threshold=float(self.pDict["threshold"])
      classRes=int(self.pDict["defaultClass"])
      if listPred[1-classRes]>threshold :
         classRes=1-classRes
      return classRes
   
   def classifyBasedOnML (self,model,ld) :
    "Classify based on a Machine Learning Algorithm"
    
    X,dbkeys=ld.loadTestDataSet ()
    predicted = model.predict(X)
    if self.probabilities:
      predictProbabilities=model.predict_proba(X)
    fo = codecs.open(self.pDict["classifiedFile"], "w", "utf-8")
    fi = codecs.open(self.pDict["segmentsLangFile"], "r", "utf-8")
    for line in fi :
        line=line.rstrip()
        dbkey1,dbkey2,sourceQuery,destQuery,sLangs,tLangs=line.split("@#@")
        dbkey=dbkey1+"-"+dbkey2
        if dbkey in dbkeys :
            i=dbkeys.index (dbkey)
            classRes=predicted[i]
            if self.probabilities :
               classesPred=str(round(predictProbabilities[i][0],2))+"-"+str(round(predictProbabilities[i][1],2))
               classRes=self.decideClass(predictProbabilities[i])
               fo.write(dbkey1+"@#@"+dbkey2+"@#@"+classesPred+"@#@ML@#@"+str(classRes)+"\n")
            else:
               fo.write(dbkey1+"@#@"+dbkey2+"@#@"+"ML"+"@#@"+str(classRes)+"\n")
   
   
   
   def fitSVM (self) :
      "Classify the test data using the SVM algorithm "
      
      models=Models(self.pDict)  
      model,ld=models.getSVM ()
      self.pDict["classifiedFile"]=self.getNewFile(".classifiedCG-SVM.txt")
      self.classifyBasedOnML (model,ld)            
               
   

   def fitDummy (self) :
      """ Fit the dummy algorithm to the test data"""
      
      models=Models(self.pDict)
      model,ld=models.getDummy()
      self.pDict["classifiedFile"]=self.getNewFile(".classifiedDummy.txt")
      self.classifyBasedOnML (model,ld)  
   
   
        
   def fitKNearNeighbors(self) :
        "Classifiy the test data using the KNearNeighbors algorithm"
        
        models=Models(self.pDict)
        model,ld=models.getKNearNeighbors()
        self.pDict["classifiedFile"]=self.getNewFile(".classifiedkNear.txt")
        self.classifyBasedOnML (model,ld)  
   
      

   def fitRandomForest (self) :
        "Classifiy the test data using the Random Forest algorithm"
        
        models=Models(self.pDict)
        model,ld=models.getRandomForest()
        self.pDict["classifiedFile"]=self.getNewFile(".classifiedRandomForest.txt")
        self.classifyBasedOnML (model,ld)  
        

   def fitDecisionTree (self) :
        "Classifiy the test data using the Decision Tree algorithm"
        
        models=Models(self.pDict)
        model,ld=models.getDecisionTree()
        self.pDict["classifiedFile"]=self.getNewFile(".classifiedDecisionTree.txt")
        self.classifyBasedOnML (model,ld)  
        

        
   def fitLogisticRegression (self) :
        """Classifiy the test data using the Logistic Regression algorithm.
        It can output probabilities. """
        
        models=Models(self.pDict)
        model,ld=models.getLogisticRegression()
        self.probabilities=True
        self.pDict["classifiedFile"]=self.getNewFile(".classifiedLogisticRegression.txt")
        self.classifyBasedOnML (model,ld)  
        
        
     
def main():
    pass
    
   
    
if __name__ == '__main__':
  main()
