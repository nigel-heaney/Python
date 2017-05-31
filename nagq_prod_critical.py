#!/usr/bin/env python
"""
   Purpose      : simple program which uses nagquery to pull dataset and present as a html 
		: table and return result for further processing.
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
<head>
<link rel="stylesheet" type="text/css" href="wss-nagmon.css">
</head>
<body>
<center>
<H1>PRODUCTION: Critical Service Alerts</H1>
<p>
<br>
'''
webpayload='''
<audio autoplay>
  <source src="media/notify.wav" type="audio/wav">
  Your browser does not support the audio element.
</audio>
'''

webfooter='''
</p>
</center>
</body>
</html>
'''

table_header_names="Host,Service Check"
table_header_names_host="Host"
sound_enabled=True
add_webpayload=0

def convert_epoch(epoch):
    """ simply return time now as full string """
    return time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(int(epoch)))


if __name__ == '__main__':
	q = nag()
	result = q.queryfile("/usr/local/bin/nag-prod-crit-noack.txt")
	print webheader
	if not result:
		print "Nothing to Report"
	else:
		print "<table><tr>"
		for row in table_header_names.split(','):
			print "<th>" + row + "</th>"
		print "</tr>"
		for row in result:
			host_name,description,last_check,perf_data = row[0],row[1],convert_epoch(row[2]),row[3]
			print "<tr><td>" + host_name + "</td>"
			print "<td>" + description + "</td>"
			#print "<td>" + last_check + "</td>"
			#print "<td>" + perf_data + "</td></tr>"
		print "</table>"
		if sound_enabled: add_webpayload = 1

	print "<H1>PRODUCTION: Hosts Down</H1>"
	result = q.queryfile("/usr/local/bin/nag-prod-hosts-down-nonack.txt")
	if not result:
		print "Nothing to Report"
	else:
		print "<table><tr>"
		for row in table_header_names_host.split(','):
			print "<th>" + row + "</th>"
		print "</tr>"
		for row in result:
			name,last_check = row[0],convert_epoch(row[1])
			print "<tr><td>" + name + "</td>"
			#print "<td>" + last_check + "</td>"
		print "</table>"
		if sound_enabled: add_webpayload = 1
	if add_webpayload == 1: print webpayload
	print webfooter


