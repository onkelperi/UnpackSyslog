#! /usr/bin/env python

from optparse import OptionParser
import sys
import os
import shutil
import glob
import tarfile
import zipfile
import gzip
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
    elif (len(FileList) > 1):
        print "More then one problemreport found. This script can only handle one!"
    else:
        print repr(len(FileList)) + " problemreport(s) found"
        for file in FileList:
            print "copy Problemreport " + file + " to " + OutputPath
            shutil.copy(file, OutputPath)
    
def getftplogs():
    print "get ftp logs from problemreport"
    File = glob.glob(OutputPath + "*.zip")[0]
    os.system("unzip -P " + Password + " " + File + " -d " + OutputPath)
    shutil.move(OutputPath + "Miscellaneous/IC Traces/ftplogs.zip", OutputPath)
    shutil.rmtree(OutputPath + "Miscellaneous")
    

def getlogandconfigfiles():
    print "get logandconfigfiles.zip"
    File = glob.glob(OutputPath + "ftplogs.zip")[0]
    print File
    myZip = zipfile.ZipFile(File)
    Member = myZip.namelist()[0]
    myZip.extract(Member, OutputPath)
  
def ExtractGetLogAndConfigFiles():
    print "extract the getlogandconfigfiles.zip"
    File = glob.glob(OutputPath + "getlogandconfigfiles.zip")[0]
    myZip = zipfile.ZipFile(File)
    with myZip as zip:
        members = zip.namelist()
        for member in members:        
            myZip.extract(member, OutputPath)

def ExtractSyslogs():
    print "extract all syslog.x"
    os.chdir(OutputPath + "home/roche/share/log/")
    os.system("gunzip syslog.* .")
    
def main():
  IncludeWorkAlready = True
  PrepareOutputFolder()
  getMainZip()
  getftplogs() # not suported, ftplogs.zip has to be extracted manually
  if (IncludeWorkAlready):
    getlogandconfigfiles()
    ExtractGetLogAndConfigFiles()
    ExtractSyslogs()
    
if __name__ == '__main__':
    sys.exit(main())
