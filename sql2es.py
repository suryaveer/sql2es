#!/usr/bin/python2.7
#
# Python RPC-over-HTTP server to convert SQL-like queries into ElasticSearch queries.
#
# Copyright (C) 2013 Zynga Game Network Inc. All rights reserved.
#

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from simplejson import loads, dumps
from tornado.options import define, options
import elseql
from elseql.search import ElseSearch
import daemon
import lockfile
import sys
import os

define("port", default=9288, help="run on the given port", type=int)
define("pidfile", None, str)
define("logfile", None, str)


class PidFile(object):
    def __init__(self,path):
        self.path = path
        self.pidfile = None

    def __enter__(self):
        self.pidfile = open(self.path,"w")
        self.pidfile.write(str(os.getpid()))
        self.pidfile.close()
        return self.pidfile

    def __exit__(self,exc_type=None, exc_value=None, exc_tb=None):
        os.reomve(self.path)


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, search):
        self.search = search
    def get(self):
        self.write({'status' : 'FAILED', 'reason' : 'GET Not Implemented'})
    def post(self):
        try:
            input = loads(self.request.body)
        except ValueError:
            self.write({'status' : 'FAILED', 'reason' : 'Invalid JSON: ' + self.request.body})
            return

        result = self.search.search(input['query'], parseOnly=True)
        if type(result) is dict:
            response = {'status' : 'OK'}
            response['result'] = result
            self.write(response)
        else:
            response = {'status' : 'FAILED'}
            response['reason'] = result
            self.write(response)

def main():
    tornado.options.parse_command_line()
    #context = daemon.DaemonContext(pidfile=options.pidfile)
    #context.open()
    if not options.pidfile:
        print 'PID file  must be defined. Exiting.'
        sys.exit(1)

    if not options.logfile:
        print 'Log file  must be defined. Exiting.'
        sys.exit(1)
    log = open(options.logfile, 'a+')
    context = daemon.DaemonContext(stdout=log, stderr=log, pidfile=PidFile(options.pidfile))
    context.open()
    #with daemon.DaemonContext():
    search = ElseSearch()
    application = tornado.web.Application([
        (r"/", MainHandler, dict(search=search)),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
