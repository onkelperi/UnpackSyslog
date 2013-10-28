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
        "The aim of this script is to help enpacking Problemreports.\n\nIn this version it is possible to unpack problemreports in the following format:\n- Folder containing WSIM*.zip\n- WSIM*.zip (containing ftplogs.zip)\n- ftplogs.zip (containing getlogandconfigfiles.zip)\n- getlogandconfigfiles.zip (ICLog gathered with ECP command GetLogAndConfigFile)\n- Folder containing the syslog.*.gz files", version="%prog 1.03")
    _add = parser.add_option
    _add ("-P", "--password",      action="store",        dest="password",      default="comit",                      help="The passwort for unziping")
    _add ("-p", "--problemreport", action="store",        dest="problemreport",                                       help="folder containing the problemreport")
    _add ("-o", "--outputfolder",  action="store",        dest="outputfolder",  default="/var/log/investigation",     help="destination folder of the problemreport")
    return parser

(options, args)=getOptions().parse_args()
Password = options.password
Problemreport = options.problemreport
OutputPath = options.outputfolder + "/"


def PrepareOutputFolder():
    if (os.path.exists(OutputPath)):
        if (OutputPath != "/"):
            shutil.rmtree(OutputPath)
    os.makedirs(OutputPath)

def getMainZip():
    if (os.path.isfile(Problemreport)):
        copyMainZipFile()
    elif (os.path.exists(Problemreport)):
        getMainZipFromPath()
    else:
        print "ERROR: the given Problemreport " + Problemreport + " must be a folde containing the problemreport or the problemreport (WSIM*.zip) itself"
        exit(1)

def getMainZipFromPath():
    FileList = glob.glob(Problemreport + "WSIM*.zip")
    if (len(FileList) == 0):
        print "Folder " + Problemreport + " does not contain a suitable problemreport in the form of WSIM*.zip"
    elif (len(FileList) > 1):
        print "More then one problemreport found. This script can only handle one!"
    else:
        print repr(len(FileList)) + " problemreport(s) found"
        for file in FileList:
            print "copy Problemreport " + file + " to " + OutputPath
            shutil.copy(file, OutputPath)            
            timeout = 5;
            WrittenFile = OutputPath + os.path.basename(file)
            while ((not os.path.exists(WrittenFile)) and (timeout > 0)):
                WrittenFile = OutputPath + os.path.basename(file)
                print OutputPath + os.path.basename(file) + " does not yet exists"
                time.sleep(1)
                timeout -= 1
                
def copyMainZipFile():
    print "copy the Problemreport zip " + Problemreport + " to outputfolder " + OutputPath
    if (re.search("WSIM.*.zip", Problemreport)):
        shutil.copy(Problemreport, OutputPath)
    else:
        print "ERROR: given problemreport " + Problemreport + " is not a problemreport containing IC logs"
        exit(1)
    
def getftplogs():
    print "get ftp logs from problemreport"
    File = glob.glob(OutputPath + "*.zip")
    if (len(File) < 1):
        print "no zip file found in " + OutputPath
        exit(1)
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
        exit(1)
    File = File[0]
    os.system("unzip -P " + Password + " " + File + " -d " + OutputPath)
    shutil.move(OutputPath + "Miscellaneous/IC Traces/ftplogs.zip", OutputPath)
    shutil.rmtree(OutputPath + "Miscellaneous")
    

def GetLogAndConfigFiles():
    print "get logandconfigfiles.zip"
    File = glob.glob(OutputPath + "ftplogs.zip")
    if (len(File) < 1):
        print "ERROR: ftplogs.zip not found"
        exit(1)
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

    
class StateMachine:
  class EState:
    Error = -1
    NotStarted = 0
    OutputFolderPrepared = 10
    InputEvaluated = 15
    LogsInFolderOrMainZip = 17
    MainZipReady = 20
    ftpLogsReady = 30
    LogAndConfigFilesReady = 40
    LogAndConfigFilesExtracted = 50
    SyslogsExtracted = 60
    OldZipFilesDeleted = 70
    Finish = 100
  
  State = EState.NotStarted
  Success = True
  ErrorMessage = ""
  
  def Run(self):
    while (self.State != self.EState.Finish):
      if (self.State == self.EState.NotStarted):
        PrepareOutputFolder()
        self.SetState(self.EState.OutputFolderPrepared)
      if (self.State == self.EState.OutputFolderPrepared):
        self.EvaluateInput()
        # State is set within EvaluateInput
      if (self.State == self.EState.LogsInFolderOrMainZip):
        getMainZip()
        self.SetState(self.EState.MainZipReady)
      if (self.State == self.EState.MainZipReady):
        getftplogs()
        self.SetState(self.EState.ftpLogsReady)
      if (self.State == self.EState.ftpLogsReady):
        GetLogAndConfigFiles()
        self.SetState(self.EState.LogAndConfigFilesReady)
      if (self.State == self.EState.LogAndConfigFilesReady):
        ExtractGetLogAndConfigFiles()
        self.SetState(self.EState.LogAndConfigFilesExtracted)
      if (self.State == self.EState.LogAndConfigFilesExtracted):
        ExtractSyslogs()
        self.SetState(self.EState.SyslogsExtracted)
      if (self.State == self.EState.SyslogsExtracted):
        DeleteOldZipFiles()
        self.SetState(self.EState.Finish)
      if (self.State == self.EState.Error):
        Success = False
        self.SetState(self.EState.Finish)
      if (self.State == self.EState.Finish):
        if (len(self.ErrorMessage) > 0):
          print "ERROR"
          print "ErrorMessage:\n" + self.ErrorMessage  
        else:
          print "====> unpacking Problemreport finish"
  
  def SetState(self, NewState):
    #print "State change from " + str(self.State) + " to " + str(NewState)
    self.State = NewState
  
  def AppendErrorMessage(self, Message):
    self.ErrorMessage = self.ErrorMessage + Message + "\n"
    self.Success = False
    
  def EvaluateInput(self):    
    if (Problemreport.find("ftplogs.zip") != -1):
      shutil.copy(Problemreport, OutputPath)
      self.SetState(self.EState.ftpLogsReady)
    elif (Problemreport.find("getlogandconfigfiles.zip") != -1):
      shutil.copy(Problemreport, OutputPath)
      self.SetState(self.EState.LogAndConfigFilesReady)
    elif (Problemreport.find("WSIM") != -1):
      self.SetState(self.EState.LogsInFolderOrMainZip)
    elif (os.path.isdir(Problemreport)):
      if (self.IsSyslogInFolder()):
        Destination = OutputPath + "home/roche/share/log"
        os.makedirs(Destination)
        for foundfile in glob.glob(Problemreport + "*"):
          shutil.copy(foundfile, Destination)
        self.SetState(self.EState.LogAndConfigFilesExtracted)
      elif (self.IsWSIMInFolder()):
        self.SetState(self.EState.LogsInFolderOrMainZip)
      else:
        self.AppendErrorMessage("A path was passed as input but the folder does not contain any suitable logs")
        self.SetState(self.EState.Error)    
    elif (not Problemreport):
      self.AppendErrorMessage("No problemreport passed")
      self.SetState(self.EState.Error)
    else:
      self.AppendErrorMessage("No problemreport passed")
      self.SetState(self.EState.Error)
    print "Start with state: " + str(self.State)
  
  def IsWSIMInFolder(self):
    file = glob.glob(Problemreport + "WSIM*.zip")
    if (len(file) > 0):
      return True
    return False  
  
  def IsSyslogInFolder(self):
    for file in glob.glob(Problemreport + "*"):
      if (file.find("syslog") != -1):
        return True
    return False  


#############################################################################33  

def main():
  print "==================== Syslog unpacker ==================================="
  print "OutputPath: " + OutputPath
  print "Problemreport: " + Problemreport
  print "========================================================================"
  MyStateMachine = StateMachine()
  MyStateMachine.Run()
  print "========================================================================"

    
if __name__ == '__main__':
    sys.exit(main())
