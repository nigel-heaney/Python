#!/usr/bin/env python
"""
   nagquery     : simple class to execute nagios query against livestatus
                : and return result for further processing.
   Author       : Nigel Heaney
   Version      : 0.1 23092014 initial version
"""
import socket

class nagquery():
    def __init__(self):
        self.debug=False
        self.socket_path = "/var/nagios/rw/live"


    def query(self,query="Get hosts\n"):
        """Process a query and return the resulting dataset"""
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.socket_path)
        s.send(query)
        s.shutdown(socket.SHUT_WR)
        result = s.recv(100000000)
        return [ line.split(';') for line in result.split('\n')[:-1] ]

    def queryfile(self,query_file=""):
        """Load a query from file and return the resulting dataset"""
        query=""
        file = open(query_file)
        for l in file.readlines(): query += l
        file.close()
        return self.query(query)

if __name__ == '__main__':
    q=""
    q+="GET services\n"
    q+="Columns: host_name description last_check perf_data\n"
    q+="Filter: host_name ~ -T-\n"
    q+="Filter: acknowledged = 0\n"
    q+="Filter: state = 2\n"
    x = nagquery()
    #result = x.query(query=q)
    result = x.queryfile("./query1.txt")
    print result
