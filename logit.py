#!/usr/bin/env python
"""
   logit  : Python wrapper class for integrating logging into other python programs.
   Author : Nigel Heaney 
   Version: 0.1
   History:
"""
import logging
class logit():
	def __init__(self):
		self.logfilename="/var/log/output.log"
		self.dateformat="%Y-%m-%d_%H-%M-%S"
		self.default_log_level=logging.DEBUG
		self.filemode='w' 		#a,w
	def startlog(self):
		logging.basicConfig(filename=self.logfilename, level=self.default_log_level, datefmt=self.dateformat, format='%(asctime)s:%(levelname)8s: %(message)s', filemode=self.filemode)
		logging.info("Logging started")

	def loginfo(self, output):
		logging.info(output)
		
	def logwarn(self, output):
		logging.warning(output)

	def logcritical(self, output):
		logging.critical(output)

	def logerror(self, output):
		logging.error(output)

	def logdebug(self, output):
		logging.debug(output)
		
if __name__ == '__main__':
	x = logit()
	x.logfilename="./test.log"
	x.startlog()
	x.logwarn("test")
	x.logcritical("test")
	x.loginfo("test")
	x.logdebug("test")

	
