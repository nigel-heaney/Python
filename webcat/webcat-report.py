#!/usr/bin/env python
"""
   webcat-report  : Tool to parse webcat xml files and generate an excel report. OBIEE/Weblogic reports.
                
   Version      Author          Date        Description      
     0.1        Nigel Heaney    20161010    Initial version
"""

import os
import sys
import time
import re
import xlwt

class WebcatReport():
    def __init__(self):
        self.version='0.1'
        self.basepath='/u01/oracle/global/webcat/root/shared'       #Default location to find the webcat xml files.
        self.reportpath='/u01/oracle/reports'
        self.debug=False    
        self.filelist=[]    #list of files to be processed
        self.xlsfh=''       #file handle for the xls file
        self.xlsfile=self.reportpath + "/webcat_report_" + time.strftime("%Y%m%d-%H%M") + ".xls"
        #self.xlsfile=self.reportpath + "report.xls"
        self.xlsbook=''
        self.xlssheet=''
        self.emailuser='some.one@example.test'
        
        
        print "WebcatReport v" + self.version 
        print "============================\n"
        
    def generate_file_list(self):
        '''
           generate a list of files to process from 
        '''
        print "Generating file list: ",
        sys.stdout.flush()
        for root, dirs, files in os.walk(self.basepath, topdown=True):
            for name in files:
                f=os.path.join(root, name)
                if os.path.isfile(f):
                    #ignore .atr files
                    if f.find('.atr') > -1:
                        continue
                    else:
                        self.filelist.append(f)
        print "Done - " + str(len(self.filelist)) + " Files to check"

    def parse_files(self):
        '''
           Parse the xml files to extract data.
        '''
        self.xlsbook=xlwt.Workbook(encoding="utf-8")
        self.xlssheet = self.xlsbook.add_sheet("webcat_extraction")
        #Setup styles
        boldstyle = xlwt.easyxf('font: bold 1, color blue;')
        wrapstyle = xlwt.easyxf('align: wrap 1;')
        
        #Define column width for easier reading (Guess work only).
        self.xlssheet.col(1).width = 30 * 256       #filename
        self.xlssheet.col(2).width = 60 * 256       #filepath
        #self.xlssheet.col(5).width = 40 * 256       #Format
        self.xlssheet.col(6).width = 40 * 256       #Subject
        self.xlssheet.col(7).width = 40 * 256       #Message
        self.xlssheet.col(8).width = 60 * 256       #Report Path
        self.xlssheet.col(9).width = 40 * 256       #Email List

        #Create headers
        self.xlssheet.write(0,0,"Index", boldstyle)
        self.xlssheet.write(0,1,"Filename", boldstyle)
        self.xlssheet.write(0,2,"Filepath", boldstyle)
        self.xlssheet.write(0,3,"Disabled", boldstyle)
        self.xlssheet.write(0,4,"RunAS", boldstyle)
        self.xlssheet.write(0,5,"Format", boldstyle)
        self.xlssheet.write(0,6,"Subject", boldstyle)
        self.xlssheet.write(0,7,"Message", boldstyle)
        self.xlssheet.write(0,8,"ReportRef Path", boldstyle)
        self.xlssheet.write(0,9,"Email List", boldstyle)
        
        count=1
        index=0
        maxcount=len(self.filelist)
        for xfile in self.filelist:
            print "\rProcessing [{0}/{1}]".format(count, maxcount),
            sys.stdout.flush()
            data=open(xfile, 'r').read()
            #check if file is xml, if not ignore.
            count=count+1
            if data.find('saw:ibot') > -1:
                #extract data values
                #index, filename, filepath, disabled?, RunAS, mFormat, Subject, Message Body, ReportRef, Emaillist
                disabled = runas = mformat = subject = mbody = reportref = emaillist = ""
                index=index+1
                filename=re.search('(^.*\/)(.*)',xfile).group(2)
                filepath=re.search('(^.*\/)(.*)',xfile).group(1)
                filepath=re.sub('/$','',filepath)
                if re.search('disabled="(.*)"><saw:start startImmediately', data): 
                    disabled=re.search('disabled="(.*)"><saw:start startImmediately', data).group(1)
                if re.search('runAs="(.*)" runAsGuid', data): 
                    runas=re.search('runAs="(.*)" runAsGuid', data).group(1)
                if re.search('format="(.*)"><saw:headline>', data): 
                    mformat=re.search('format="(.*)"><saw:headline>', data).group(1)
                if re.search('<saw:headline><saw:caption><saw:text>(.*)</saw:text></saw:caption></saw:headline>', data, re.DOTALL): 
                    subject=re.search('<saw:headline><saw:caption><saw:text>(.*)</saw:text></saw:caption></saw:headline>', data, re.DOTALL).group(1)
                if re.search('<saw:attachmentMessage><saw:caption><saw:text>(.*)</saw:text></saw:caption></saw:attachmentMessage>', data, re.DOTALL): 
                    mbody=re.search('<saw:attachmentMessage><saw:caption><saw:text>(.*)</saw:text></saw:caption></saw:attachmentMessage>', data, re.DOTALL).group(1)

                #Turns out Report ref has a few different tags so we collate them here
                if re.search('reportRef path="(.*?)"', data): 
                    reportref=re.search('reportRef path="(.*?)"', data).group(1)
                if re.search('saw:dashboardPageRef dashboard="(.*?)"', data): 
                    reportref=re.search('saw:dashboardPageRef dashboard="(.*?)"', data).group(1)
                if re.search('briefingBook path="(.*?)"', data): 
                    reportref=re.search('briefingBook path="(.*?)"', data).group(1)
                #if re.search('briefingBook path="(.*?)"', data): 
                #    reportref=re.search('briefingBook path="(.*?)"', data).group(1)


                if re.search('<saw:emailRecipients>(.*)</saw:emailRecipients>', data): 
                    emaillist=re.search('<saw:emailRecipients>(.*)</saw:emailRecipients>', data).group(1)
                    emaillist=re.sub('<saw:emailRecipient address="','',emaillist)
                    emaillist=re.sub('" type="HTML"/>','\n',emaillist)
                    emaillist=re.sub(',$','',emaillist)
                self.printdebug('INDEX: ' + str(index))
                self.printdebug('File: ' + filepath + ' -> ' + filename)
                self.printdebug('Disabled: ' + disabled)
                self.printdebug('RunAs: ' + runas)
                self.printdebug('Msg Format: ' + mformat)
                self.printdebug('Subject: ' + subject)
                self.printdebug('Message: ' + mbody)
                self.printdebug('ReportRef: ' + reportref)
                self.printdebug('Email List: ' + emaillist)
                
                #Write out to the excel file.
                self.xlssheet.write(index,0,index)
                self.xlssheet.write(index,1,filename)
                self.xlssheet.write(index,2,filepath)
                self.xlssheet.write(index,3,disabled)
                self.xlssheet.write(index,4,runas)
                self.xlssheet.write(index,5,mformat)
                self.xlssheet.write(index,6,subject)
                self.xlssheet.write(index,7,mbody,wrapstyle)
                self.xlssheet.write(index,8,reportref)
                self.xlssheet.write(index,9,emaillist,wrapstyle)
                
            else:
                self.printdebug('IGNORED: ' + xfile)
                continue
            
            
            #Lets save the spreadsheet now we have finished.        
            self.xlsbook.save(self.xlsfile)

    def printdebug(self,message=''):
        '''
           If debug is enabled, then print the message to stdout (this should only be used from the commandline to assist with erroneous data analysis)
        '''
        if self.debug == True:
          print "DEBUG: {0}".format(message)
        
if ( __name__ == "__main__"):
    #Instantiate
    p=WebcatReport()

    #Check if path was supplied as part of the commmand line, if so then override default.
    if len(sys.argv) > 1:
        if not os.path.isdir(sys.argv[1]):
            print "ERROR: Could not locate {0:s}. Please ensure you point to a valid directory containing the webcat files...\n".format(sys.argv[1])
            exit(2)
        else:
            p.basepath=sys.argv[1]
    
    #Generate file list to process
    print "Report file: " + p.xlsfile
    print "\nSearch Path: " + p.basepath
    p.generate_file_list()
    p.parse_files()
