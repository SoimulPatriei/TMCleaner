#!/usr/bin/env python


"""Produce a HTML file to easily see the results of the evaluation"""

import sys
import re
import codecs


def getFileContents(f):
    """Read the content of evaluation file or the manually classified file """
    
    tList=[]
    fi = codecs.open(f, "r", "utf-8")
    for line in fi:
        line=line.rstrip()
        tList.append(line)
        
    return tList    
 
def writeHeader(fo):
    
    fo.write("<html>")
    fo.write("<head>")
    fo.write("<title>HTML Tables</title>")
    fo.write("""<meta charset="UTF-8">""")
    fo.write("</head>")


def writeTH(fo):
    
    fo.write("<tr>\n")
    fo.write("<th>"+"Source Translation Unit"+"</th>\n")
    fo.write("<th>"+"Destination Translation Unit"+"</th>\n")
    fo.write("<td>"+"Automatic Category"+"</td>\n")
    fo.write("<td>"+"Manual Category"+"</td>\n")
    fo.write("</tr>\n")


   
def writeRow(fo,sQuery,dQuery,cEv,cManual):
    
    fo.write("<tr>\n")
    fo.write("""<td style="word-wrap: break-word;">"""+sQuery+"</td>\n")
    fo.write("""<td style="word-wrap: break-word;">"""+dQuery+"</td>\n")
    if cEv == cManual :
        fo.write("""<td style="word-wrap: break-word;">"""+cEv+"</td>\n")
    else :
        fo.write("""<td bgcolor="#00FF00" style="word-wrap: break-word;"> <font color="red"><b>"""+cEv+"</b></td>\n")
        
    fo.write("""<td style="word-wrap: break-word;">"""+cManual+"</td>\n")
    
        
    fo.write("</tr>\n")



def pTableFile(mList,evList,fTable):
    """Print The Table File ..."""
    
    fo = codecs.open(fTable, "w", "utf-8")
    writeHeader(fo)
    fo.write("<body>\n")
    fo.write("""<table width="700"  border="1">""")
    writeTH(fo)
    for i in range (len(mList)) :
        compManual=mList[i].split("@#@")
        compEv=evList[i].split("@#@")
        
        sQuery=compManual[2]
        dQuery=compManual[3]
        cEv=compEv[-1]
        cManual=compManual[-1]
        
        writeRow(fo,sQuery,dQuery,cEv,cManual)
    
    fo.write ("</table>")    
    fo.write("<body>\n")
    fo.write("</html>\n")
    
    fo.close()



def main():
    
    fManual=sys.argv[1]
    fEvaluation=sys.argv[2]
    fTable=sys.argv[3]
    
    mList=getFileContents(fManual)
    evList=getFileContents(fEvaluation)
    
    pTableFile(mList,evList,fTable)
    
    print "Results in =>" +fTable
    
    


       
if __name__ == '__main__':
  main()