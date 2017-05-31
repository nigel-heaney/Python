#!/usr/bin/env python
import os
def list(indent=0,path=None):
	for l in os.listdir(path):
		if indent > 0: print "--" * indent,
		if os.path.isdir(os.path.join(path,l)):
			print "DIR: " + l
			list(indent+1,path=os.path.join(path,l))
		else:
			print "FILE:" + l
			
#main
list(path=".")
