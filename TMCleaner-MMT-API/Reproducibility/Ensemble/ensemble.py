#!/usr/bin/env python

"""The training data for English-Italian and English-French language pairs is loaded and the
individual classifiers and ensembles of classifiers are run.
To run these scripts you need scikit-learn installed on your computer. The Stacking ensemble is imported from
mxltend.classifier package :http://rasbt.github.io/mlxtend/ """

"""Run the script: 

English-Italian : python ensemble.py --config Config/c-Italian.txt --resultsdir English-Italian-Classified
English-French:   python ensemble.py --config Config/c-French.txt --resultsdir English-French-Classified

Output :
======> English-Italian-Classified directory
======> English-French-Classified directory
"""


    

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import collections
from mlxtend.classifier import StackingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
from LoadData import *
import argparse
import os
import shutil 



def readParameters (fileParameters) :
    fp = codecs.open(fileParameters, "r", "utf-8")
    pDict={}
    for lineSegment in fp:
        if lineSegment.startswith('#') :
            pass
        else :
            lineSegment=lineSegment.rstrip()
            if re.search ("\t",lineSegment) :
                argument,value=lineSegment.split("\t")
                pDict[argument]=value          
    return pDict






def getClassifiers () :
    """Get the individual classifiers"""
    
    np.random.seed(1)
    dictClassifiers=collections.OrderedDict()
    
    clf1 = LogisticRegression()
    clf2=SVC(kernel='rbf', probability=True)
    clf3=DecisionTreeClassifier(max_depth=4)
    clf4=KNeighborsClassifier(n_neighbors=7)
    clf5=SVC(kernel='linear', probability=True)
    
    dictClassifiers[clf1]="LogisticRegression"
    dictClassifiers[clf2]="SVM-RBF"
    dictClassifiers[clf3]="kNearstNeighbors"
    dictClassifiers[clf4]="DecisionTree"
    dictClassifiers[clf5]="SVM-Linear"
    
    return dictClassifiers


def classify (clf,label,dictML,dbkeys) :
    "Classify based on a Machine Learning Algorithm"
    
    model=clf.fit(dictML["X_train"],dictML["y_train"])
    predicted = model.predict(dictML["X_test"])
    classifiedFPath=os.path.join(dictML["resultsDirectory"],label+"-classified.txt")
    
    fo = codecs.open(classifiedFPath, "w", "utf-8")
    i=-1
    for dbkey in dbkeys :
        i+=1
        dbkey1,dbkey2=dbkey.split("-")
        classRes=predicted[i]
        fo.write(dbkey1+"@#@"+dbkey2+"@#@"+"ML"+"@#@"+str(classRes)+"\n")
    fo.close()
    print ("Results=>"+classifiedFPath)


def runIndividualAndMajority(dictML,dbkeys):
    """Run Individual Classifiers and the Majority Voting"""
    
    dictClassifiers=getClassifiers()
    listClassifiers=[(label,clf) for clf,label in dictClassifiers.items()]
    
    eclfHard = VotingClassifier(estimators=listClassifiers, voting='hard')
    
    for clf, label in dictClassifiers.items():
        print (label)
        classify(clf,label,dictML,dbkeys)
    
    classify(eclfHard,"VotingMajorityHard",dictML,dbkeys)
        

def runStacking(dictML,dbkeys):
    """Run Ensemble Classification using Stacking"""
    
    dictClassifiers=getClassifiers()
    listClassifiers=[(clf) for clf,label in dictClassifiers.items()]
    
    lr = LogisticRegression()
    stackcl = StackingClassifier(classifiers=listClassifiers, meta_classifier=lr)
    
    classify(stackcl ,"StackingLogisticRegression",dictML,dbkeys)
    

def adaBoost (dictML,dbkeys) :
    """AdaBoost classifier with 500 weak learners """
    
    adacl = AdaBoostClassifier(n_estimators=500)
    classify(adacl,"AdaBoost500learners",dictML,dbkeys)


def bagging (dictML,dbkeys) :
    """Bagging classifier ... """
    
    tree = DecisionTreeClassifier(criterion='entropy', max_depth=None,random_state=1)
    bagcl = BaggingClassifier(base_estimator=tree,
                            n_estimators=500,
                            max_samples=1.0,
                            max_features=1.0,
                            bootstrap=True,
                            bootstrap_features=False,
                            n_jobs=1,
                            random_state=1)
    classify(bagcl,"BaggingClassifier",dictML,dbkeys)


def getDataSet(pDict,resdir):
    """Load the data set"""
    
    ld=LoadData(pDict)
    X_train,y_train=ld.loadTrainingDataSet()
    X_test,dbkeys=ld.loadTestDataSet()
    dictML={"X_test":X_test,"X_train":X_train,"y_train":y_train,"resultsDirectory":resdir}
    return dictML,dbkeys


def executeProgram():
    """Parse the arguments of the scripts using argparse and executes the script"""
    
    parser = argparse.ArgumentParser(description='Classify using individual classifiers and the ensembles of classifiers')
    parser.add_argument("--config",type=str,help="configuration file with the parameters for classification")
    parser.add_argument("--resultsdir",type=str,help="The output directory where we store the results of the classification")
    
    
    args = parser.parse_args()
    
    print "Create directory=>"+args.resultsdir
    if (os.path.isdir(args.resultsdir)) :
        print ("Directory present. I delete it!")
        shutil.rmtree(args.resultsdir)
    os.makedirs(args.resultsdir)    
    
    print ("Read Parameters from:"+args.config)
    pDict=readParameters(args.config)
    
    print ("Load data")
    dictML,dbkeys=getDataSet(pDict,args.resultsdir)
    
    print("Run the Individual Classifiers and the ensembles of classifiers")
    
    print ("Majority Voting")
    runIndividualAndMajority (dictML,dbkeys)
    print ("====================================================")
    
    print ("Stacking")
    runStacking(dictML,dbkeys)
    print ("====================================================")
    
    print ("Ada Boost")
    adaBoost (dictML,dbkeys)
    print ("====================================================")
    
    print ("Bagging")
    bagging (dictML,dbkeys)
    print ("====================================================")
    print ("Final Results in =>"+args.resultsdir)
    



def main():
   
    executeProgram()
    
    

if __name__ == '__main__':
  main()