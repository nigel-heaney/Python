#!/usr/bin/env python
"""
   wssfktools  : Module to interface with fkhistory
   Author      : Nigel Heaney 
   Version     : 0.1
"""
import re
import os
import sys
import glob
import time
import shutil
if sys.platform == "linux" or sys.platform == "linux2":
	import be
	import tarfile
elif sys.platform == "win32":
	import be_win as be

class wssfktools():
	def __init__(self):
		if sys.platform == "linux" or sys.platform == "linux2":
			self.fkhistorycmd='$FK_HOME/bin/fkhistory'
			self.isappserver=1
		elif sys.platform == "win32":
			self.fkhistorycmd='%FK_HOME%\\bin\\fkhistory'
			self.isappserver=0
		self.debug=0

	def collect_fkhistory(self):
		'''execute fkhistory and then convert to a structured format so it can be sorted by date of install.
		   Structure: package, version, date_install_string, date_install_epoch
		'''
		#fkhistraw=subprocess.check_output(self.fkhistorycmd.split(),shell=True)
		fkhistraw=os.popen(self.fkhistorycmd).read()
		self.db={}
		for l in fkhistraw.split('\n'):
			#ignore ONEOFF, failed,unknown, rolled back,header and 13001 packages
			#package,version,date,status,env
			status=''
			package=l.split(' - ')
			
			if not len(package) < 4:
				if re.search("Reading|Status|Package", l):
					continue
				if re.search("ONEOFF|13001|Failed|Rollback|Unknown", l,re.I):
					status="IGNORE"
				else:
					status="OK"
				self.db[package[0].rstrip()] = {
					'name':package[0].rstrip(),
					'version':package[1].lstrip(),
					'install_time_string':package[2].lstrip(),
					'install_time': self.convert_full(package[2], "%Y-%m-%d %H:%M:%S"),
					'status': status
				}
				if self.debug:
					print self.db[package[0].rstrip()]['name'],'-',
					print self.db[package[0].rstrip()]['version'],'  -->  ',
					print self.db[package[0].rstrip()]['install_time_string'],'(' + str(self.db[package[0].rstrip()]['install_time']) + ')  -> ',
					print self.db[package[0].rstrip()]['status']
		return self.db
		
	def generate_refresh_package(self,db,checkonly=False):	
		'''
			generate the package refresh contents (packages + configdata (if node0))
		'''
		#create package directory
		dpath=os.environ['FK_IDENT'] + '_package_list_' + time.strftime("%Y-%m-%d")
		if not checkonly:
			if not os.path.exists(dpath): 
				os.makedirs(dpath)
				os.makedirs(os.path.join(dpath, 'configdata'))
			packagefile = open(os.path.join(dpath, 'packages.txt'),'w')
		#gather packages in the order they are applied
		package_order = sorted(self.db, key=lambda x: (self.db[x]['install_time']))
		for p in package_order:
			be.set_colour('white')
			print "{0:<25s} - {1:<15s}- {2:17s} -> ".format(self.db[p]['name'],self.db[p]['version'],self.db[p]['install_time_string']),
			if self.db[p]['status'] == 'OK': 
				be.set_colour('green')
				#lets find the package in the archive directory
				pfile=glob.glob('archive/' + self.db[p]['name'] + '*' + self.db[p]['version'] + '.zip')
				if pfile:
					if not checkonly: shutil.copy(pfile[0], dpath)
					if os.path.isfile(os.path.join(dpath, os.path.split(pfile[0])[1])) or checkonly:
						print "OK"
						if not checkonly:
							packagefile.write(os.path.split(pfile[0])[1] + '\n')
					else:
						be.set_colour('red')
						print "ERROR - file copy failed" 
				else:
					be.set_colour('red')
					print "ERROR - Package not found in archive" 
			else: 
				be.set_colour('grey')
				print self.db[p]['status']
			be.reset_colour()
		if not checkonly: 
			packagefile.close()
			#create configdata if app and node = 0
			if self.isappserver:
				#check node name if exists
				nodeid=os.environ['FK_NODE_ID']
				if not nodeid or nodeid == '0':
					be.set_colour('white')
					print "\nCreating backup of Configuration data... ",
					cmmtar = tarfile.open(os.path.join(dpath, 'configdata', os.environ['FK_IDENT'] + '_configdata_' + time.strftime("%Y-%m-%d") + ".tar.gz"), "w:gz")
					olddir=os.getcwd()
					os.chdir(os.environ['CMM_HOME'])
					cmmtar.add('./ConfigurationData')
					cmmtar.close()
					os.chdir(olddir)
					be.set_colour('green')
					print "OK"
					be.reset_colour()
			
			#create install script for packages
			os.chdir(dpath)
			be.set_colour('white')
			print "\nGenerating install script : ",
			if self.isappserver:
				#create install script for linux
				installfile=open('install.sh', 'w')
				installfile.write('#!/bin/bash\n')
				installfile.write('#Automatically generated!\n')
				installfile.write('echo Installing packages...\n')
				installfile.write('for p in `cat packages.txt`; do\n')
				installfile.write('        ../deploy_packages.sh $p\n')
				installfile.write('done\n')
				installfile.write('cp -prf log ..\n')
				installfile.write('fkhistory | sort -k 5\n')
				installfile.close()
				os.chmod('install.sh', 0755)
			else:
				#create install script for windows
				installfile=open('install.bat', 'w')
				installfile.write('@echo off\n')
				installfile.write('for /F "tokens=*" %%P in (packages.txt) do @call ..\deploy_packages.bat "%%P" \n')
				installfile.write('xcopy /Q /Y /E  log* ..\\\n')
				installfile.write('xcopy /Q /Y /E  log\\* ..\\log\n')
				installfile.write('fkhistory\n')
				installfile.close()
			be.set_colour('green')
			print "OK"
			be.set_colour('white')
			print "Generated Package Location: ",
			be.set_colour('green')
			print dpath
			be.set_colour('white')

	def validate_fkhistory(self,db):
		''' 
			display fkhistory with package validation check but dont create a package repository.
		'''
		self.generate_refresh_package(db,checkonly=True)
		
	def convert_full(self,fulltimestamp,format="%a %b %d %H:%M:%S %Y"):
		'''
		   return strimg timestamp as epoch
		'''
		#trap for older fkinstall which dont output seconds
		if not re.search("..:..:..", fulltimestamp): 
			fulltimestamp += ':00'
		return int(time.mktime(time.strptime(fulltimestamp, format)))
				

#by default this class/script will perform generate refresh package
if __name__ == "__main__":
	p=wssfktools()
	db=p.collect_fkhistory()
	p.generate_refresh_package(db)
	#p.validate_fkhistory(db)
	
