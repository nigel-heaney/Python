#!/usr/bin/env python
"""
############################################################################
# Filename:     go
# Written by:   Nigel Heaney
# Decription:   Simple tool to aid directory traversal within large file structures
#		Just edit alias list
# Version:      1.0
# Date:         10/Nov/2012
#
############################################################################
"""
import re,os,sys

#build hash table
dirhash = {
    '/data01/app/config/dir1/dir2/dir3/dir4/dir5/dir6/dir7':"d7|dir7",
    '$HOME':"h|home",
    '/tmp':"tmp",
    '/data01':"1|d1|data01",
    '/data02':"2|d2|data02",
    '/data03':"3|d3|data03",
    '/data04':"4|d4|data04",
    '$APPDIR_HOME':"wh|whome|w",
    '$APPDIR_HOME/var/logs':"^logs$|^l$",
    '$CMM_HOME/ConfigurationData':"configdata|configurationdata|cmmdata|cmm_data|cd",
    '$APPDIR_HOME/var/appservers/glassfish/bin':"gladmin|glassfish-bin|glassfishbin|glbin",
    '$APPDIR_HOME/var/appservers/glassfish/domains':"glassfish-domains|glassfishdomains|gldomains|domains",
    '$APPDIR_HOME/var/active-mq':"amq|activemq",
    '~/Monitoring/parser/':"parser",
    '~/Monitoring/mon_scripts_conf/':"monconf"


}
extra=""

def showusage():
        print "go <directory alias>"
        exit(1)
## MAIN
if len(sys.argv) < 2:
        showusage()

udir = sys.argv[1].lower()
if re.search("\/",udir):
        temp=re.sub("\/.*","",udir)
        extra=re.sub(temp,"",udir)
        udir=temp

for l in dirhash:
    if re.search(dirhash[l],udir):
              if extra:
                print l + extra
              else:
                print l

#setup bash function
#function go() {
#    eval cd `python go.py $1`
#}

