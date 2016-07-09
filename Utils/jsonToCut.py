#! /usr/bin/python

import json, sys
from pprint import pprint

if len(sys.argv) != 2 :
    print sys.argv[0], "running with arglist:", str(sys.argv), \
        "\ncorrect syntax :", sys.argv[0], "INPUT_JSON_FILE"
    sys.exit(100)

fileData=open(sys.argv[1]).read()
json = json.loads(fileData)

tCutString = ""

isFirstRun = True
for run, lumiRanges in json.iteritems() :
    if not isFirstRun :
        tCutString += " || "
    isFirstRun = False
    tCutString += "( run==" + str(run)  + " && ( " 

    isFirstRange = True
    for lumiRange in lumiRanges :
        if not isFirstRange :
            tCutString += " || "
        isFirstRange = False

        tCutString += "( lumi>=" + str(lumiRange[0])  + " && lumi<=" + str(lumiRange[1]) + ")"

    tCutString += " ) ) "

print("TCutString : %s" % tCutString)
print
