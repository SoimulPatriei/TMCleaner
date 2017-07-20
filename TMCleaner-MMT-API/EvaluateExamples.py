#!/usr/bin/env python

"""Performs the evaluation comparing a manually annotated file with the result of classification """
__author__      = "Eduard Barbu"
__copyright__ = "Copyright 2016, The Expert Project"

import sys
import re
import codecs
import numpy as np
from sklearn import metrics
import numpy as np
from collections import OrderedDict
import produceHTMLFormat as ph
from os.path import split,join
import argparse


class Evaluate():
    """ Evaluate the performance of the automatic classification."""
        
    def printFile(self,fOutput,y_vect):
        """Auxiliary function """
    
        fo = codecs.open(fOutput, "w", "utf-8")
        for value in y_vect:
            fo.write(str(value)+"\n")
        fo.close()
    
    def printOutput (self,y_true,y_pred) :
        """Generate all output files """
         
        print ("Get and print miss Lines") 
        difList=[i for i in range(len(y_true)) if y_true[i]!=y_pred[i]]
        with codecs.open(self.fClassified,"r","utf-8") as fi:
            lines = list(line for line in (l.strip() for l in fi) if line) 
        missLines=[lines[i]+"\t"+str(y_true[i]) for i in difList]
        
        fo = codecs.open(self.fMiss, "w", "utf-8")
        for line in missLines:
            fo.write(line+"\n")
        fo.close()
        fi.close()

    def roundA(self,mArray):
        """Round the results of an array"""
        rArray=[]
        for item in mArray:
            rItem=round (item,2)
            rArray.append(rItem)
        return rArray
    
    def pPredicted(y_pred,fTruePred):
        """Print Y_Predicted. """
        
        fo = codecs.open(fTruePred, "w", "utf-8")
        for i in range (len(y_pred)):
            fo.write(str(y_pred[i])+"\n")
        fo.close()
    
    def getY (self,fileTest) :
        """Get y values."""
        
        fi = codecs.open(fileTest, "r", "utf-8")
        y=[]
        for line in fi :
            line=line.rstrip()
            if line!='' :
                components=line.split("@#@")
                y.append(int(components[-1]))
        fi.close
        return y
        
    
    def mpBinary(self,y_true,y_pred):
        
        """Measure Performance for the Binary Task ... """
        
        fo = codecs.open(self.fStat, "w", "utf-8")
        fo.write ("Confusion matrix\n")
        cm=metrics.confusion_matrix(y_true,y_pred,[1,0])
        fo.write ( str(cm)+"\n")
        fo.write("--------------------------------------------------\n")
        
        
        arrayP=self.roundA(metrics.precision_score(y_true, y_pred,[1,0], average=None))
        arrayR=self.roundA(metrics.recall_score(y_true,y_pred,[1,0], average=None))
        arrayF1=self.roundA(metrics.f1_score(y_true,y_pred,[1,0], average=None))
        
        fo.write("Per class measures\n")
        fo.write("Precision :"+str(arrayP)+"\n")
        fo.write("Recall :"+str(arrayR)+"\n")
        fo.write("F1 Score :"+str(arrayF1)+"\n")
        fo.write("------------------------------------------------\n")
        
        ba=(arrayR[0]+arrayR[1])/2
        fo.write("Balanced Accuracy:"+str(ba)+"\n")
        fo.close()
    
    
    def generateHTML(self):
        """Generate the HTML file with the results to be presented """
        
        mList=ph.getFileContents(self.fManual)
        evList=ph.getFileContents(self.fClassified)
        
        ph.pTableFile(mList,evList,self.fHTML)
        
    
    def evaluate(self) :
        """Perform the evaluation operations."""
        
        y_true=self.getY(self.fManual)
        y_pred=self.getY(self.fClassified)
        self.mpBinary(y_true,y_pred)
        self.printOutput(y_true,y_pred)
        self.generateHTML()
    
    
    def getPrecisionNegative(self,y_true,y_pred):
        """Get precision for negative class """
        
        cList=[i for i in range(len(y_true)) if y_true[i]==y_pred[i]]
        p=float(len(cList))/len(y_true)
        return p
    
        
    def evaluateNegativeClass(self) :
        """Perform the evaluation operations only for negative class."""
        
        y_true=self.getY(self.fManual)
        y_pred=self.getY(self.fSample)
        self.printOutput(y_true,y_pred)
        p=self.getPrecisionNegative(y_true,y_pred)
        return p
        
        
    def __init__(self,fClassified,fManual):
      self.fClassified = fClassified
      self.fManual= fManual
      path,fName=split(fClassified)
      self.fStat=join(path,"statistics-sample.txt")
      self.fMiss=join(path,"miss-sample.txt")
      self.fHTML=join(path,"visualize-sample.html")
          
    
def executeProgram():
        """Parse the arguments of the program using argparse and execute the program"""
        
        parser = argparse.ArgumentParser(description='Evaluate the results using a manually annotated file')
        parser.add_argument("--classified",type=str, help="The classified file")
        parser.add_argument("--annotated",type=str, help="The annotated file")
        
        args = parser.parse_args()
        print ("Evaluate...")
        ev=Evaluate(args.classified,args.annotated)
        ev.evaluate()
        print "End Results Evaluation ..."
        
def main():
    
    executeProgram()
    
    
    
       
if __name__ == '__main__':
  main()