#!/usr/bin/env python
import logit
		
if __name__ == '__main__':
	x = logit.logit()
	x.logfilename="./test2.log"
	x.startlog()
	x.loginfo("test1")
	x.logwarn("test2")
	x.logcritical("test3")
	x.logerror("test4")
	x.logdebug("test5")

