#!/usr/bin/env python


"""Load the training and test data in the standard scikit learn format and perform data normalization"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sklearn as sk
import numpy as np
import csv
import codecs
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler

class LoadData():
    """Load the training and test data in the standard scikit learn format. It also performs data normalization. """


    def __init__(self,argumentsDict):
      self.argumentsDict = argumentsDict
      self.feature_training_names=""
     
      
    def removeIndexes (self,row,listIndex) :
        "Remove the elements at the indexes. First sort the indexes to be sure you delete them correctly"
        
        for i in sorted(listIndex, reverse=True):
            row.pop(i)

    def getIndexTrFeatures (self,row) :
        "Get the Indexes of the features to remove"
        
        featuresEliminateList=self.argumentsDict["featuresEliminate"].split(",")
        listIndex=[]
        for feature in featuresEliminateList :
            listIndex.append (row.index(feature))
        return listIndex

    def getIndexTestFeatures (self,row) :
        "Get the Indexes of the features to remove"
        
        featuresEliminateList=self.argumentsDict["featuresEliminate"].split(",")
        featuresEliminateList.remove('category')
        listIndex=[]
        for feature in featuresEliminateList :
            listIndex.append (row.index(feature))
        return listIndex

    def getCategoryIndex (self,row) :
        "Get the index of the category "
        
        return row.index(self.argumentsDict["category"])

    def getFeatureFile (self,fileOld,ending) :
        "It generates a New File from an Old One"
        li=fileOld.rsplit(".txt",1)
        return ending.join(li)

    def getMapping (self,feature_test_names, feature_training_name ) :
        """ Get the mapping between the feature indexes"""
        mapDict={}
        for i in range(len(feature_test_names)):
            mapDict[i]=feature_training_name.index(feature_test_names[i])
        return mapDict    
    
    def correctRow (self,row,mapDict) :
        """Get the correct row such as the indexes of test and training set correspond """
        finalRow=row
        for i in range(len(row))  :
            finalRow[i]=row[mapDict[i]]
        return finalRow    
    
    def getCorrectRow (self,mapDict,feature_training_names) :
        """Get the row correponding to training set """
        correctRow=[]
        for feature in feature_training_names :
            correctRow.append(mapDict[feature])
        return correctRow

    def scaleToRange(self,X,rangeString):
        """Scale feature values between min and max"""
        
        minValue,maxValue=rangeString.split(",")
        min_max_scaler = preprocessing.MinMaxScaler(feature_range=(int(minValue),int(maxValue)))
        X_minmax = min_max_scaler.fit_transform(X)
        return X_minmax

    def trainingScaling(self,X):
        """Variance Scaling for training set"""

        scaler = preprocessing.StandardScaler().fit(X)
        X_transform=scaler.transform(X)
        return X_transform,scaler

    def testScaling(self,X,scaler):
        """Variance Scale for the test set """
        
        X_transform=scaler.transform(X)
        return X_transform

    def loadTestDataSet (self) :
        """It reads the test dataSet from the CSV file"""
        
        fs = codecs.open(self.argumentsDict["testFile"], "r", "utf-8")
        reader = csv.reader(fs, delimiter=',')
        
        #Load feature names and remove the ones you do not want.
        #The category feature for sure there is not in the test data  
        row = reader.next()
        listIndexes=self.getIndexTestFeatures (row)
        
        
        dbKeyIndex=row.index("dbkey")
        self.removeIndexes(row,listIndexes)
        
       
        feature_test_names = list(row)
        
        #Load dataset, and target classes
        X,dbkeys = [],[]
        for row in reader:
            dbkeys.append(row[dbKeyIndex])
            self.removeIndexes(row,listIndexes)
            
            mapDict=dict(zip(feature_test_names, row))
            correctRow=self.getCorrectRow (mapDict,self.feature_training_names)
            
            floatRowList=[float(i) for i in correctRow]
            X.append(floatRowList)
        
        X = np.array(X)
        
        #Scale the features in range min max...
        if (self.argumentsDict["scaleToRange"]=="1") :
            X=self.scaleToRange(X,self.argumentsDict["range"])
            
        #Scale the features using variance scaling
        if (self.argumentsDict["varianceScaling"]=="1") :
            X=self.testScaling(X,self.scaler)
        
        #normalized by the axis 0, that is by feature
        #normalized_X=preprocessing.normalize(X,axis=0)
        
        
        return X,dbkeys

    def loadTrainingDataSet (self) :
        """It reads the training dataSet from the CSV file.
           I give as parameters also the features names to be sure than the features are the same
           as in training set. """
        
        fs = codecs.open(self.argumentsDict["trainingFile"], "r", "utf-8")
        reader = csv.reader(fs, delimiter=',')
        
        #Load feature names and remove the ones you do not want
        row = reader.next()
        categoryIndex=self.getCategoryIndex (row)
        listIndexes=self.getIndexTrFeatures (row)
        self.removeIndexes(row,listIndexes)
        
       
        self.feature_training_names = list(row)
        
        #Load dataset, and target classes
        X, y = [], []
        for row in reader:  
            y.append(row[categoryIndex])
            self.removeIndexes(row,listIndexes)
            
            floatRowList=[float(i) for i in row]
            X.append(floatRowList)
        
        X = np.array(X)
        y = np.array(y)
        
        #Scale the features in range min max...
        if (self.argumentsDict["scaleToRange"]=="1") :
            X=self.scaleToRange(X,self.argumentsDict["range"])
        
        # Scale the features using variance scaling
        self.scaler=None
        if (self.argumentsDict["varianceScaling"]=="1") :
            X,self.scaler=self.trainingScaling(X)
        
        #normalized by the axis 0, that is by feature
        #normalized_X=preprocessing.normalize(X,axis=0)
        
        
        return X,y
    
    def loadDataSetStratifiedClassification (self) :
        
        """It reads the dataSet from the CSV file.
        The data read in this way will be used in cross classification."""
        
        featureFile=self.argumentsDict["featureFile"]
        fs = codecs.open(featureFile, "r", "utf-8")
        reader = csv.reader(fs, delimiter=',')
        
        #Load feature names and remove the ones you do not want
        row = reader.next()
        categoryIndex=self.getCategoryIndex (row)
        listIndexes=self.getIndexTrFeatures (row)
        self.removeIndexes(row,listIndexes)
        
       
        feature_names = np.array(row)
        
        #Load dataset, and target classes
        X, y = [], []
        for row in reader:  
            y.append(row[categoryIndex])
            self.removeIndexes(row,listIndexes)
            
            floatRowList=[float(i) for i in row]
            X.append(floatRowList)
        
        X = np.array(X)
        y = np.array(y)
        
        #normalized by the axis 0, that is by feature
        #normalized_X=preprocessing.normalize(X,axis=0)
        
        
        return X,y,feature_names
    

