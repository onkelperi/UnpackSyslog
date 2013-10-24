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
import time

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
OutputPath = options.outputfolder + "/"


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
            timeout = 5;
            WrittenFile = ""
            while ((not os.path.exists(WrittenFile)) and (timeout > 0)):
                WrittenFile = OutputPath + os.path.basename(file)
                print OutputPath + os.path.basename(file) + " does not yet exists"
                time.sleep(1)
                timeout -= 1
                
                
    
def getftplogs():
    print "get ftp logs from problemreport"
    File = glob.glob(OutputPath + "*.zip")
    if (len(File) < 1):
        print "no zip file found in " + OutputPath
        exit(0)
    File = File[0]
    os.system("unzip -P " + Password + " " + File + " -d " + OutputPath)
    shutil.move(OutputPath + "Miscellaneous/IC Traces/ftplogs.zip", OutputPath)
    IMTracePath = OutputPath + "IMTraces/"
    os.makedirs(IMTracePath)
    for file in glob.glob(OutputPath + "Miscellaneous/IM Traces/*"):
        shutil.move(file, IMTracePath)
    shutil.rmtree(OutputPath + "Miscellaneous")
    
def getIMTraces():
    print "get the IM traces from problemreport"
    File = glob.glob(OutputPath + "*.zip")
    if (len(File) < 1):
        print "no zip file found in " + OutputPath
        exit(0)
    File = File[0]
    os.system("unzip -P " + Password + " " + File + " -d " + OutputPath)
    shutil.move(OutputPath + "Miscellaneous/IC Traces/ftplogs.zip", OutputPath)
    shutil.rmtree(OutputPath + "Miscellaneous")
    

def getlogandconfigfiles():
    print "get logandconfigfiles.zip"
    File = glob.glob(OutputPath + "ftplogs.zip")
    if (len(File) < 1):
        print "ERROR: ftplogs.zip not found"
        exit(0)
    File = File[0]
    print "extract " + File
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
    
def DeleteOldZipFiles():
    for file in glob.glob(OutputPath + "*.zip"):
        os.remove(file)
        
def main():
  print "OutputPath: " + OutputPath
  print "Problemreport: " + ProblemreportPath
  PrepareOutputFolder()
  getMainZip()
  getftplogs()
  getlogandconfigfiles()
  ExtractGetLogAndConfigFiles()
  ExtractSyslogs()
  DeleteOldZipFiles()
    
if __name__ == '__main__':
    sys.exit(main())
