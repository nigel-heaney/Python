#!/usr/bin/env python -OO
"""
   pydaemon 		: Class to run a function/method in a loop and have controls to dicate how frequent,start,stop,pid
   Author 		: Nigel Heaney 
   Version		: 0.1
   History		:
"""
from epoch import epoch
import time
from logit import logit
import sys,os



__version__='pydaemon v0.1'

class pydaemon():
	def __init__(self):
		self.debug=False
		self.delay=2					#10 second loop, eg execute event at most every 10 seconds
		self.execfunction=self.testfunction		#Set this to the method/fucntion which will be executed every delay seconds
		self.pidfile="/tmp/x.pid"			#location for pidfile
		self.forceexit=False
		self.enablelogging=False
#		if logfile: 
#			self.logfile=logfile
#			self.enablelogging=True
#			self.logoutput(__version__)

#		else:
			#self.logfile=logit()

	def start(self):
		"""start daemon - a wrapper for time based events"""
		timesource=epoch()
		self.create_pid()
		while self.forceexit == False:
				eventstart=timesource.epochnow()
				#do stuff
				x=self.execfunction()
				eventend=timesource.epochnow()
				processtime=eventend - eventstart
				delaytime=self.delay - processtime
				if self.debug:
					print "  start time:", eventstart
					print "    end time: ",eventend
					print "process time:",processtime
					print "  delay time:",delaytime
					print "     logging:", self.enablelogging
					
				time.sleep(self.delay - (eventend - eventstart))

	def stop(self):
		"""stop daemon - a wrapper for time based events"""
		pid=self.loadpid()
		self.logoutput("Stop command issued")
		if not pid:
			return "no pid found, stop failed"
		try:
			os.kill(pid,15)
		except OSError:
			return "process does not exist"
		else:
			self.removepidfile()
			return "process stopped"
			
		
	def status(self):
		"""status of daemon """
		pid=self.loadpid()
		if not pid:
			return "process is not running..."

		try:
			os.kill(pid,0)
		except OSError:
			return "process is not running..."
		else:
			o="process is running...(",pid,")"
			return o
		
		
	def loadpid(self):
		"""validate pid file exists	,then validate pid exist,if not cleanup"""
		pid=self.getpid()
		if not pid:
			self.removepidfile()
			return False
		return pid

	def getpid(self):
		if os.path.isfile(self.pidfile):
			try:
				f=open(self.pidfile,'r')
				pid=int(f.readline())
				f.close()
			except:
				return False
			else:
				return pid
		
	def removepidfile(self):
		if os.path.isfile(self.pidfile): 
			try:
				os.remove(self.pidfile)
			except OSError:
				self.logerror("could not delete pid file")
			
		
	def restart(self):
		self.stop()
		time.sleep(0.5)
		self.start()

	def create_pid(self,pid=False):
		f = open(self.pidfile,'w')
		if not pid: pid=str(os.getpid())
		f.write(pid)
		self.logoutput(os.getpid())
		f.close()
		
			
	def testfunction(self):
		self.logoutput("test")
		time.sleep(0.5)		

	def logoutput(self,output):
		if self.debug:
			print output			

	def logerror(self,output):
		if self.debug:
			print "ERROR -",output			


if __name__ == '__main__':
	x = pydaemon()
	x.pidfile='./x.pid'
	x.start()
	
	
	
