#!/usr/bin/env python

"""Can be used to import the data in a postgres database"""
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import codecs
import collections
import re
#import postgresOperations
    
    
def getTuple (segmentFeaturesDict) :
    "It inserts the feature values in the database"
    
    insertList=[]
    dbKeysList=segmentFeaturesDict.keys()
    for dbKey in dbKeysList :
        segmentFeaturesDict[dbKey]["dbkey"]=str(dbKey)
        insertList.append(segmentFeaturesDict[dbKey])
    insertTuple=list(insertList)    
    return insertTuple    


def writeFeatureFile (segmentFeaturesDict,fileModel) :
    """Print the file in the CSV format to be handeled by scikit-learn"""
    
    fs = codecs.open(fileModel, "w", "utf-8")
    
    dbKeysList=segmentFeaturesDict.keys() #3091-20,3450-1
    featureNameDict=segmentFeaturesDict[dbKeysList[0]] 
    featureNameList=featureNameDict.keys() #langDifference,emailDifference
    
    featureNameList.remove("sourcesegment")
    featureNameList.remove("destsegment")
    
    #------Write the first row containing feature names--------
    featureString="dbKey,"
    for feature in featureNameList :
        featureString+=feature+","
    featureString=featureString.rstrip(',')+"\n"
    
    fs.write(featureString)
    
    for dbKey in dbKeysList :
        featureValueString=dbKey+","
        for featureName in featureNameList :
            featureValueString+=str(segmentFeaturesDict[dbKey][featureName])+","
        featureValueString=featureValueString.rstrip(',')+"\n"
        fs.write(featureValueString)
        
        
def deleteRecords(segmentFeaturesDict,tableName):
    """It deletes the already present table records"""
    
    con=postgresOperations.getDbConnection()
    cursor = con.cursor()
    dbkeyList=segmentFeaturesDict.keys()
    for dbkey in dbkeyList:
        stringToExecute="select exists(select 1 from " +tableName+ " where dbkey='"+dbkey+"')"
        cursor.execute(stringToExecute)
        for res in cursor:
            if res[0] ==True :
                del segmentFeaturesDict[dbkey]
            break    
            
    postgresOperations.closeDbConnection(con)
    

 
def insertRecordsTableExistent (segmentFeaturesDict,tableName) :
    """Insert the records in a database table when the table already exists.
       It checks if the records already exists in the table. """
        
    con=postgresOperations.getDbConnection()
    deleteRecords(segmentFeaturesDict,tableName)
    insertTuple =getTuple(segmentFeaturesDict)
    
    postgresOperations.insertIntoTable(tableName,insertTuple,con)
    postgresOperations.closeDbConnection(con)
     
    

def insertRecords (segmentFeaturesDict,fileCommand,tableName) :
    """Insert the records in a database table."""
        
    con=postgresOperations.getDbConnection()
    postgresOperations.createTable(con,fileCommand,tableName)
    
    insertTuple =getTuple(segmentFeaturesDict)
    
    postgresOperations.insertIntoTable(tableName,insertTuple,con)
    postgresOperations.closeDbConnection(con)
        
    
def writeFeatureFile (segmentFeaturesDict,fileModel) :
    """Print the file in the CSV format to be handeled by scikit-learn"""
    
    fs = codecs.open(fileModel, "w", "utf-8")
    
    dbKeysList=segmentFeaturesDict.keys() #3091-20,3450-1
    featureNameDict=segmentFeaturesDict[dbKeysList[0]] 
    featureNameList=featureNameDict.keys() #langDifference,emailDifference
    
   
    featureNameList.remove("sourcesegment")
    featureNameList.remove("destsegment")
    if "sourcesegmenttranslated" in featureNameList :
        featureNameList.remove("sourcesegmenttranslated")
    
    
    #------Write the first row containing feature names--------
    featureString="dbkey,"
    for feature in featureNameList :
        featureString+=feature+","
    featureString=featureString.rstrip(',')+"\n"
    
    fs.write(featureString)
    
    for dbKey in dbKeysList :
        featureValueString=dbKey+","
        for featureName in featureNameList :
            featureValueString+=str(segmentFeaturesDict[dbKey][featureName]).decode('unicode-escape')+","
        featureValueString=featureValueString.rstrip(',')+"\n"
        fs.write(featureValueString)
            

