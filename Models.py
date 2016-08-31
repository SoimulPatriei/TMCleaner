#!/usr/bin/env python

"""Fit the algorithms to the training data and obtain the trained models and the feature names used in training"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"


from LoadData import *
from TrainModels import *

class Models():
    """Fit the algorithms to the training data and obtain the trained models and the feature names used in training"""

    def __init__(self,argumentsDict):
      self.argumentsDict = argumentsDict


    def getRandomForest (self) :
        """ Fit the model to the trainig data."""
        
        ld=LoadData(self.argumentsDict)
        X,y=ld.loadTrainingDataSet()
        tm=TrainModels(X,y)
        model=tm.getRandomForest()
        return model,ld           

        
    def getDecisionTree (self) :
        """ Fit the model to the trainig data."""
        
        ld=LoadData(self.argumentsDict)
        X,y=ld.loadTrainingDataSet()
        tm=TrainModels(X,y)
        model=tm.getDecisionTree()
        return model,ld     
        
        
    def getSVM (self) :
        """ Fit the model to the trainig data."""
        
        ld=LoadData(self.argumentsDict)
        X,y=ld.loadTrainingDataSet()
        tm=TrainModels(X,y)
        model=tm.getSVM()
        return model,ld


    def getKNearNeighbors  (self) :
        """ Fit the model to the trainig data."""
        
        ld=LoadData(self.argumentsDict)
        X,y=ld.loadTrainingDataSet()
        tm=TrainModels(X,y)
        model=tm.getModelKNear()
        return model,ld
  
 

    def getLogisticRegression (self) :
        """ Fit the model to the trainig data."""
        
        ld=LoadData(self.argumentsDict)
        X,y=ld.loadTrainingDataSet()
        tm=TrainModels(X,y)
        model=tm.getModelLogistic()
        return model,ld



    def getDummy (self) :
        """ Fit the model to the trainig data."""
        
        ld=LoadData(self.argumentsDict)
        X,y=ld.loadTrainingDataSet()
        tm=TrainModels(X,y)
        model=tm.getDummy()
        return model,ld








