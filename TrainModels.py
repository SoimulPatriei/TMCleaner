#!/usr/bin/env python

"""Return the classifier after training on the training set."""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"


from sklearn.neighbors import KNeighborsClassifier
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier



class TrainModels(object):
    """Train Models."""
    
    def __init__(self,X_train,y_train):
      self.X_train = X_train
      self.y_train= y_train
    
    def getModelKNear (self) :
        "Get the model Fit to the training data. Default number of neighbors is 5"
        
        clf=KNeighborsClassifier()
        clf.fit(self.X_train,self.y_train)
        
        return clf

    def getDummy (self) :
        "Get the dummy classifier trained."
        
        clf = DummyClassifier(strategy='stratified',random_state=0)
        clf.fit(self.X_train,self.y_train)
        
        return clf


    def getModelLogistic (self) :
        "Get the Logistic model Fit to the training data"
        
        clf=LogisticRegression()
        clf.fit(self.X_train,self.y_train)
        
        return clf


    def getDecisionTree (self) :
        "Get the model Fit to the training data"
        
        clf=DecisionTreeClassifier()
        clf.fit(self.X_train,self.y_train)
        
        return clf


    def getSVM (self) :
        "Get the model Fit to the training data"
        
        clf=SVC()
        clf.fit(self.X_train,self.y_train)
        
        return clf


    def getRandomForest (self) :
        "Get the model Fit to the training data"
        
        clf=RandomForestClassifier()
        clf.fit(self.X_train,self.y_train)
        
        return clf









