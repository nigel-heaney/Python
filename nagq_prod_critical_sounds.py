#!/usr/bin/env python
"""
   Purpose      : simple which uses nagquery to pull dataset and present as a html table
                : and return result for further processing.
   Author       : Nigel Heaney
   Version      : 0.1 23092014 initial version
"""
import socket
import time
from nagquery import nagquery as nag

webheader='''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<meta content="text/html; charset=ISO-8859-1"
http-equiv="content-type">
<meta http-equiv="refresh" content="60" />
<html>
<body>
<center>
'''

webpayload='''
<audio autoplay>
  <source src="media/bomb.wav" type="audio/wav">
  Your browser does not support the audio element.
</audio>
'''

webfooter='''
</center>
</body>
</html>
'''

def convert_epoch(epoch):
    """ simply return time now as full string """
    return time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(int(epoch)))


if __name__ == '__main__':
    q = nag()
    result = q.queryfile("./nag-prod-crit-nonack.txt")
	print webheader
    if result is None:
        #print "Nothing to Report"
	print webfooter
    else:
        print webpayload
	print webfooter
	#for row in result:
        #    host_name,description,last_check,perf_data = row[0],row[1],convert_epoch(row[2]),row[3]
        #    print host_name, " | ", description, " | ", last_check," | ", perf_data


