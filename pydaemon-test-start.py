#!/usr/bin/env python
# test start pydaemon
from pydaemon import pydaemon
from logit import logit
import time

def test():
	print "tick"
	time.sleep(0.5)
	
	
lf=logit()
lf.logfilename="./pydaemon-testz.log"
lf.startlog()

x = pydaemon()
lf.loginfo("init")

x.pidfile='x.pid'
x.execfunction=test
x.start()
