#!/usr/bin/env python
# test start pydaemon
from pydaemon import pydaemon

x = pydaemon()
x.pidfile="x.pid"
print x.stop()
