#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  disk-growth - attempts to track disk consumption over time and calculate an approximation of when it will fill up. 
#  

__version__='v0.2'

'''  disk-growth -  capture disk usage and then calculate growth rate. 
'''

import os,sys,re
import csv, time
import cPickle as pickle
from optparse import OptionParser
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

###Globals
fssearchstr='ext3|ext4'			#Filter so we only inspect filesystems we are interested in
growth_threshold=50				#%percent
diskfree_threshold=80			#%percent
diskspace_time_remaining=14400	#seconds (4 hours of disk space left before growth rate will fill the disk)
email_to="root@localhost"

###config
debug=0
datafile=os.path.dirname(os.path.realpath(__file__)) + '/disk-growth.dat'
logfile=os.path.dirname(os.path.realpath(__file__)) + '/disk-growth.log'


def sendMail(to, subject, text, server="localhost"):
	if sys.platform == "linux" or sys.platform == "linux2":
			sender=os.environ['USER'] + '@' + os.environ['HOSTNAME']
	elif sys.platform == "win32":
			sender=os.environ['USERNAME'] + '@' + os.environ['COMPUTERNAME'] + '.' + os.environ['USERDOMAIN']
	msg = MIMEMultipart()
	msg['From'] = sender
	msg['To'] = to
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject
	msg.attach( MIMEText(text) )

	smtp = smtplib.SMTP(server)
	smtp.sendmail(sender, to.split(','), msg.as_string() )
	smtp.close()


def get_free_space_kb(folder):
    """ Return folder/drive free space (in KB)
    """
    st = os.statvfs(folder)
    return st.f_bavail * st.f_frsize/1024

def get_used_space_kb(folder):
    """ Return folder/drive free space (in KB)
    """
    st = os.statvfs(folder)
    return ((st.f_blocks * st.f_frsize) - (st.f_bfree * st.f_frsize))/1024
	
def get_total_space_kb(folder):
    """ Return folder/drive free space (in KB)
    """
    st = os.statvfs(folder)
    return (st.f_blocks * st.f_frsize)/1024


def load_data(filename):
	"""load data file into memory"""
	if not os.path.exists(filename):
		open (filename, 'wb').close()
	file = open(filename)
	try:
		db = pickle.load(file)
	except:
		db = {}
	file.close()
	return db

def save_data(db, filename):
	"""save data file into memory"""
	if not os.path.exists(filename):
		open (filename, 'wb').close()
	file = open(filename, 'wb')
	try:
		pickle.dump(db, file)
	except:
		print "ERROR: problem saving DB"
		exit(255)
	file.close()

def epochnow():
	return int(time.time())


def add_new_fs(db, fs_name, fs):
	'''This function will define the new filesystem and append to the db so it can be saved later. 
	'''
	n = epochnow()
	ds = get_used_space_kb(fs)
	db[fs_name] = {
					'fs':fs, 
					'before_time': n, 
					'before_du': ds, 
					'now_time': n, 
					'now_du': ds, 
					'lt_rate':0, 
					'now_rate':0, 
					'alert_count':0, 
					'alert1_time':0, 
					'alert1_rate':0,
					'alert2_time':0, 
					'alert2_rate':0, 
					'alert3_time':0, 
					'alert3_rate':0,
				}
	return db

def print_fs(db, fs_name):
	'''This function will print out the data entries for a a file_system
	'''
	if debug:
		print "BEBUG: "
		print "DEBUG: Real Filesystem name:", db[fs_name]['fs']
		print "DEBUG:        Previous Time:", db[fs_name]['before_time']
		print "DEBUG:          Previous DU:", db[fs_name]['before_du']
		print "DEBUG:         Current Time:", epochnow()
		print "DEBUG:           Current DU:", get_used_space_kb(db[fs_name]['fs'])
		print "DEBUG:    Average Disk rate:", db[fs_name]['lt_rate']
		print "DEBUG:    Current Disk rate:", db[fs_name]['now_rate']
		print "DEBUG:          Alert1 Time:", db[fs_name]['alert1_time']
		print "DEBUG:          Alert1 Rate:", db[fs_name]['alert1_rate']
		print "DEBUG:          Alert2 Time:", db[fs_name]['alert2_time']
		print "DEBUG:          Alert2 Rate:", db[fs_name]['alert2_rate']
		print "DEBUG:          Alert3 Time:", db[fs_name]['alert3_time']
		print "DEBUG:          Alert3 Rate:", db[fs_name]['alert3_rate']
		print 'DEBUG: ' + '=' * 40
	
def calculate_fs_growth(db, fs_name):
	'''Calculate growth rate and store in DB
	'''
	#move last check stats to before, then calculate new
	db[fs_name]['before_du'] = db[fs_name]['now_du']
	db[fs_name]['before_time'] = db[fs_name]['now_time']
	db[fs_name]['now_time'] = epochnow()
	db[fs_name]['now_du'] = get_used_space_kb(db[fs_name]['fs'])
	
	growth_time_elapsed = db[fs_name]['now_time'] - db[fs_name]['before_time']
	if growth_time_elapsed == 0: growth_time_elapsed = 1			#prevent div0
	
	fs_growth = db[fs_name]['now_du'] - db[fs_name]['before_du']
	if fs_growth < 0: 
		fs_growth = 0								# ignore disk cleanups, fs resizes etc
		growth_time_elapsed = 1

	#Calculate growth in Kbps
	db[fs_name]['now_rate'] = fs_growth / growth_time_elapsed

	#Update long-term (average) growth-rate and previous entries so DB in consistent
	db[fs_name]['lt_rate'] = (db[fs_name]['lt_rate'] + db[fs_name]['now_rate'] ) / 2
	if debug:
		print "DEBUG: FS Growth Kb - ", fs_growth
		print "DEBUG: FS Growth Seconds - ", growth_time_elapsed
		print "DEBUG: FS Growth Rate - ", db[fs_name]['now_rate']
		print "DEBUG: LTR - ", db[fs_name]['lt_rate']
	
	return db

def print_to_logfile(output):
	'''Wrtie to logfile
	'''
	t = time.strftime("%Y-%m-%d@%T| ", time.localtime(time.time()))
	wl = '%s %s\n' % (t, output)
	lf.write(wl)
	

def process_fs_notifications(db,fs_name):
	''' Analyse if thresholds exceeded and send alerts if needed
			Warn: if Growthrate > ltr + threshold% (3rd alert)
			Crit: if Growthrate > ltr + threshold% and diskfree > 80% 
			Crit: if diskfree / growthrate = number of seconds to fill disk (is less than critical_remaining_time=4 hours 14400
	'''
	alert_flag=0
	alert_type="OK"
	alert_msg="Filesystem (%s)Is a OK!\n\nKind Regards\n%s" % (db[fs_name]['fs'], hostname)
	#calculate threshold and set alert types
	if db[fs_name]['now_rate'] > db[fs_name]['lt_rate'] + ((db[fs_name]['lt_rate'] / 100) * growth_threshold):
		#Growth threshold exceeded, setup alert as warning
		alert_flag=1
		alert_type="WARNING - Disk growth exceeds threshold"
		alert_msg="Please check this filesystem (%s), we have detected multiple spikes in IO activity and disk growth is more than normal.  Please login and check the system\n\nKind Regards\n%s" % (db[fs_name]['fs'], hostname)
		if (100 / get_total_space_kb(db[fs_name]['fs'])) * get_free_space_kb(db[fs_name]['fs']) > diskfree_threshold:
			#Threshold exceeed and disk space used is greater than 80
			alert_flag=2
			alert_type="CRITICAL - Disk space low and growth thresholds exceeded"
			alert_msg="Based on current disk consumption, this server could run out soon. Please check the server for activity (backups,rogue processes etc) and look for unusual activity because the disk space is already low and we are seeing write spikes.  If persists contact the customer we are seeing considerable disk growth.\n\nCurrently Filesystem: %s has less than 80\%.\n\nKind Regards\n%s" % (db[fs_name]['fs'], hostname)
		if (get_free_space_kb(db[fs_name]['fs']) / db[fs_name]['lt_rate']) < diskspace_time_remaining:
			#Number of seconds remaining with the current growth rate is less than the threshold i.e less than 4 hours remaining
			alert_flag=2
			alert_type="CRITICAL - Urgent diskspace consumption imminent"
			alert_msg="Based on current disk consumption, this server could run out soon. Please check the server for activity (backups etc and look for unusual activity.  If persists contact the customer we are seeing considerable disk growth.\n\nCurrently Filesystem: %s is predicted to run out in %i seconds.\n\nKind Regards\n%s" % (db[fs_name]['fs'], get_free_space_kb(db[fs_name]['fs']) / db[fs_name]['lt_rate'],hostname)
			
				
	if debug:
		print "DEBUG: Alert Class:", alert_flag
		print "DEBUG: Alert Message:", alert_type
	#output to screen reults
	out = '%15s: %s' % (db[fs_name]['fs'], alert_type)
	print out
	print_to_logfile(out)
	#Lets determine if an email needs to be sent and update the history of alerts if needed.
	if alert_flag == 0:   #0=ok
		#reset the alert history so we start from scratch
		db[fs_name]['alert1_time'] = 0
		db[fs_name]['alert1_rate'] = 0
		db[fs_name]['alert2_time'] = 0
		db[fs_name]['alert2_rate'] = 0
		db[fs_name]['alert3_time'] = 0
		db[fs_name]['alert3_rate'] = 0
		#no email alert required
		#sendMail(email_to, alert_type, alert_msg)
	else:
		if db[fs_name]['alert1_time'] == 0: 		#if not set then add 1st alert in history
			db[fs_name]['alert1_time'] = db[fs_name]['now_time']
			db[fs_name]['alert1_rate'] = db[fs_name]['now_rate']
		elif db[fs_name]['alert2_time'] == 0: 		#if not set then add 2nd alert in history
			db[fs_name]['alert2_time'] = db[fs_name]['now_time']
			db[fs_name]['alert2_rate'] = db[fs_name]['now_rate']

		elif db[fs_name]['alert3_time'] == 0: 		#if not set then add 3rd alert
			db[fs_name]['alert3_time'] = db[fs_name]['now_time']
			db[fs_name]['alert3_rate'] = db[fs_name]['now_rate']
		else:		# Alerts continue, so rotate out history and alert
			db[fs_name]['alert1_time'] = db[fs_name]['alert2_time']
			db[fs_name]['alert1_rate'] = db[fs_name]['alert2_rate']
			db[fs_name]['alert2_time'] = db[fs_name]['alert2_time']
			db[fs_name]['alert2_rate'] = db[fs_name]['alert3_rate']
			db[fs_name]['alert3_time'] = db[fs_name]['now_time']
			db[fs_name]['alert3_rate'] = db[fs_name]['now_rate']
			alert_flag=2
	
	if alert_flag > 1: #Need to send email_alert
		sendMail(email_to, alert_type, alert_msg)
	
		
			
			
#MAIN
if sys.platform == "linux" or sys.platform == "linux2":
	#hostname=os.environ['HOSTNAME']
	hostname='localohst'
elif sys.platform == "win32":
	hostname=os.environ['COMPUTERNAME'] + '.' + os.environ['USERDOMAIN']

lf = open(logfile, 'w')

	
fs_list = load_data(datafile)
file=open("/proc/mounts")
for fs in file.readlines():
	#collate all the filesystems
	fs_name=fs.split()[1]
	fs_name=re.sub("^/", "_", fs_name)
	#only check filesystems we are interested in
	if re.search(fssearchstr,fs):
		if fs_list.has_key(fs_name):
			fs_list = calculate_fs_growth(fs_list, fs_name)
			process_fs_notifications(fs_list,fs_name)
		else:
			#new so add it
			if debug: print "Adding new FS", fs_name, fs.split()[1]
			fs_list = add_new_fs(fs_list, fs_name, fs.split()[1])
		if debug: print_fs(fs_list, fs_name)

file.close()
#save
save_data(fs_list, datafile)
lf.close()
