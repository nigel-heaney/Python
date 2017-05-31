#!/usr/bin/env python
# scp.py - wrapper to launch winscp with wallix credentials

import re
import os
import getopt
import sys
import subprocess
if sys.platform == "linux" or sys.platform == "linux2":
	import be
elif sys.platform == "win32":
	import be_win as be

dbfile=r'remotelist.csv'
debug=0

def usage():
	be.cprint("white","Wallix SCP launcher\n")
	be.cprint("White","-------------------\n\n")
	be.reset_colour
	print " -h | --help                      Show this help"
	print " -l | --list <search1> <search2>  List entries in the DB which match search criteria"
	print " <server name>                    Connect to this server"
	

def searchdb(db,findstr,findstr2=''):
	'''search db for matching entries and display them'''
	be.cprint("white", "{0:^15s} | {1:^10s} | {2:^8s} | {3:^10s} | {4:^10s} | {5:^30s} | {6:^14s} | {7:^30s}|\n".format("Server", "Customer","Env","Type","User","Connection String","NAT","Description"))
	be.cprint("white", "{0:<15s}-|-{1:<10s}-|-{2:<8s}-|-{3:<10s}-|-{4:<10s}-|-{5:<30s}-|-{6:<14s}-|-{7:<30s}|\n".format("-" *15, "-"*10,"-"*8,"-"*10,"-"*10,"-"*30,"-"*14,"-"*30))
	for i in db:
		#convert record to long string and look for str matches
		recstr=""
		for r in i.split('|'): 
			recstr+=r.lower() + "|"
		found=False
		if re.search(findstr,recstr):
			found=True
			#look for second if exists
			if not recstr == '':
				if not re.search(findstr2,recstr): found=False
		if found:
			server,cust,custenv,stype,user,connstr,wabserver,wssnat,desc=i.split('|')
			c="grey"
			if custenv == "TEST": c="green"
			if custenv == "PROD": c="cyan"
			if custenv == "DR": c="red"
			be.cprint(c, "{0:<15s} | {1:<10s} | {2:<8s} | {3:<10s} | {4:<10s} | {5:<30s} | {6:<14s} | {7:<30s}|\n".format(server.rstrip(), cust.rstrip(),custenv.rstrip(),stype.rstrip(),user.rstrip(),connstr.rstrip()[:30],wssnat.rstrip(),desc.rstrip()[:30]))
			be.reset_colour()

def launch(db,server,user=''):
	'''search db for matching entry and launch - this can use any part of the string but mainly use server name or wallixid'''
	for i in db:
		#convert record to long string and look for str matches
		recstr=""
		for r in i.split('|'): 
			recstr+=r.lower() + "|"
		if re.search(server,recstr):
			#Launch and exit
			if user == '': user = i.split('|')[4]
			
			if sys.platform == "linux" or sys.platform == "linux2":
				print "TBA"
				cmd=['cat', '/dev/null']
			elif sys.platform == "win32":
				cmd=[ 'winscp.exe',  user + '@' + re.sub(':','%3A',i.split('|')[5]) + '@' + i.split('|')[6] ]
				
			
			if debug: print cmd
			subprocess.Popen(cmd,shell=True)
			be.reset_colour()
			sys.exit()
			
		
def loaddb():
	db=[]
	file = open(dbfile)
	for l in file.readlines(): db.append(l)
	return db
	
def main():
	db=loaddb()
	opts, args = getopt.getopt(sys.argv[1:], "hl", ["help", "list"])
	if debug: print "Options:", opts
	if debug: print "Args:",args
	for o,a in opts:
		if debug: print "O:", o
		if o in ("-h", "--help"):
			usage()
			print "help"
			sys.exit()
		elif o in ("-l", "--list"):
			if len(args) < 2: args.append('')
			#if len(args) < 3: args.append('')
			searchdb(db,args[0].lower(),args[1].lower())
			sys.exit()
	#connect to argument as arg2 if specified
	if debug: print "num args:",len(args)
	if len(args) < 1: 
		be.cprint("red", "Error: must specify server to connect to.\n\n")
		usage()
		sys.exit()
	if len(args) < 2: args.append('')
	launch(db,args[0].lower(),args[1])

if __name__ == "__main__":
	main()
	
