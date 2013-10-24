#! /usr/bin/env python

from optparse import OptionParser
import sys
import os
import shutil
import glob
import tarfile
import re


def getOptions():
    currentDir = (os.path.dirname( os.path.realpath( __file__ ) ))
    parser = OptionParser(usage="usage: %prog [options]\n\n" \
        "The aim of this script is to help enpacking Problemreports.", version="%prog 1.00")
    _add = parser.add_option
    _add ("-P", "--password",      action="store",        dest="password",      default="comit",                      help="The passwort for unziping")
    _add ("-p", "--problemreport", action="store",        dest="problemreport",                                       help="folder containing the problemreport")
    _add ("-o", "--outputfolder",  action="store",        dest="outputfolder",  default="/var/log/investigation",     help="destination folder of the problemreport")
    return parser

(options, args)=getOptions().parse_args()
Password = options.password
ProblemreportPath = options.problemreport
OutputPath = options.outputfolder


def PrepareOutputFolder():
    if (os.path.exists(OutputPath)):
        shutil.rmtree(OutputPath)
    os.makedirs(OutputPath)

def getMainZip():
    FileList = glob.glob(ProblemreportPath + "WSIM*.zip")
    if (len(FileList) == 0):
        print "Folder " + ProblemreportPath + " does not contain a suitable problemreport in the form of WSIM*.zip"
    else:
        print repr(len(FileList)) + " problemreport(s) found"
        for file in FileList:
            print "copy Problemreport " + file + " to " + OutputPath
            shutil.copy(file, OutputPath)
    

def main():
    PrepareOutputFolder()
    getMainZip()
    
if __name__ == '__main__':
    sys.exit(main())
