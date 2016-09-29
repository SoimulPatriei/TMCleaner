#!/usr/bin/env python

#--------------------------------------------------------------------------
#The client send queries one by one to the server and processes the answers.
#--------------------------------------------------------------------------

import requests
import sys
import codecs


def readSegments (ip,port,fileTest) :
    """Read the segments from the file """
    
    argDict={}
    fi = codecs.open(fileTest, "r", "utf-8")
    for line in fi :
        argDict={}
        line=line.rstrip()
        components=line.split("@#@")
        sourceSegment=components[2]
        targetSegment=components[3]
        argDict["sourceSegment"]=sourceSegment.encode('utf-8')
        argDict["targetSegment"]=targetSegment.encode('utf-8')
        execute(argDict,"run",ip,port)
        
    fi.close()
    execute({},"shutdown",ip,port)


def execute (argDict,message,ip,port) :
    
    #run ubuntu amazon : 54.86.81.224
    shutdown="shutdown"
    if message != shutdown :
        address="http://"+ip+":"+port+"/classifyApp"    
        result=requests.post(address, json=argDict)
        print result.text
        
    else :
        address="http://"+ip+":"+port+"/"+shutdown
        requests.post(address)
        print ("ServiceStopped")




if __name__ == '__main__':
    ip=sys.argv[1]
    port=sys.argv[2]
    fileTest="testonebyone.txt"
    readSegments (ip,port,fileTest)
    #execute({},"shutdown",ip,port)