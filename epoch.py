#!/usr/bin/env python
"""
   epoch  : Module to deal with epoch calculations and conversion
   Author : Nigel Heaney 
   Version: 0.1
"""
import time
import math

class epoch():
	# defaults
	
	#methods
	def __init__(self):
		self.lenyr=365.25		#31549824		#365.25 days
		self.lenmon=30.43		#2629152		#30.43 days
		self.lenday=86400
		self.lenhr=3600
		self.lenmin=60
		self.dateformat="%Y-%m-%d_%H-%M-%S"
		self.debug=0
		
	def elapsed_time(self, epoch1, epoch2):
		"""
		   calculate the difference between 2 epoch time stamps and return a friendly string
		"""
		days = hours = minutes = seconds = 0
		if epoch1 > epoch2:
			epoch1, epoch2 = epoch2, epoch1
		diff = int(math.floor(epoch2 - epoch1))
		if diff == 0: return "0 secs"

		if diff > self.lenday:
			days = diff / self.lenday
			diff = diff % self.lenday	

		if diff > self.lenhr:
			hours = diff / self.lenhr
			diff = diff % self.lenhr	

		if diff > self.lenmin:
			minutes = diff / self.lenmin
			diff = diff % self.lenmin	

		seconds = diff
		if days: 
			output = "{0} days, {1} hours, {2} mins and {3} secs".format(days,hours,minutes,seconds)
		else:
			if hours: 
				output = "{1} hours, {2} mins and {3} secs".format(days,hours,minutes,seconds)
			else:
				if minutes: 
					output = "{2} mins and {3} secs".format(days,hours,minutes,seconds)
				else:
					output = "{3} secs".format(days,hours,minutes,seconds)
		return output

	def elapsed_time_full(self, epoch1, epoch2):
		"""
		   calculate the difference between 2 epoch time stamps and return a friendly string
		"""
		years = months = days = hours = minutes = seconds = 0
		if epoch1 > epoch2: epoch1, epoch2 = epoch2, epoch1

		diff = int(math.floor(epoch2 - epoch1))
		if diff == 0: return "0 secs"

		#calculate days hours mins, secs
		if diff > self.lenday:
			days = diff / self.lenday
			diff = diff % self.lenday	

		if diff > self.lenhr:
			hours = diff / self.lenhr
			diff = diff % self.lenhr	

		if diff > self.lenmin:
			minutes = diff / self.lenmin
			diff = diff % self.lenmin	
		seconds = diff

		if days > self.lenyr:
			years = int(days / self.lenyr)
			days = days % self.lenyr

		if days > self.lenmon:
			months = int(days / self.lenmon)
			days = int(days % self.lenmon)
		
		if years: 
			output = "{0} years, {1} months, {2} days, {3} hours, {4} mins and {5} secs".format(years,months,days,hours,minutes,seconds)
		else:
			if months: 
				output = "{1} months, {2} days, {3} hours, {4} mins and {5} secs".format(years,months,days,hours,minutes,seconds)
			else:
				if days: 
					output = "{0} days, {1} hours, {2} mins and {3} secs".format(days,hours,minutes,seconds)
				else:
					if hours: 
						output = "{1} hours, {2} mins and {3} secs".format(days,hours,minutes,seconds)
					else:
						if minutes: 
							output = "{2} mins and {3} secs".format(days,hours,minutes,seconds)
						else:
							output = "{3} secs".format(days,hours,minutes,seconds)
		return output
		
	def epochnow(self):
		"""
		   return time now as epoch
		"""
		return time.time()
		
	def datenow(self):
		"""
		   return time now as full string
		"""
		return time.ctime(time.time())
		 
	def convert_epoch(self,epoch):
		"""
		   return given epoch time as full string
		"""
		return time.ctime(epoch)
	
	 	
	def convert_full(self,fulltimestamp,format="%a %b %d %H:%M:%S %Y"):
		"""
		   return strimg timestamp as epoch
		"""
		return int(time.mktime(time.strptime(fulltimestamp, format)))
		
		
		
if __name__ == '__main__':
	x = epoch()
	enow=x.epochnow()
	print enow
	print x.convert_epoch(enow)
	print x.datenow()

	ediff=x.elapsed_time_full(0, enow)
	print ediff
	for y in range(1, 5+1):
		ediff=x.elapsed_time(enow, (enow - y))
		print ediff
	print x.convert_full(x.datenow())
	
	
	
