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
import logging
log = logging.getLogger('SQL2ES')

define("port", default=9288, help="run on the given port", type=int)

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
    search = ElseSearch()
    tornado.options.parse_command_line()
    
    import daemon
    ctx = daemon.DaemonContext()
    ctx.open()
        
    application = tornado.web.Application([
        (r"/", MainHandler, dict(search=search)),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
