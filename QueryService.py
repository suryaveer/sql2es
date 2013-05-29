#!/usr/bin/python2.7
#
# corenlp  - Python REST server to serve segmentation requests from CMS REST Service.
# Copyright (c) 2013 Suryaveer Lodha

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from simplejson import loads
from tornado.options import define, options
import elseql
from elseql.search import ElseSearch

define("port", default=9288, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'status' : 'FAILED', 'result' : 'GET Not Implemented'})
    def post(self):
        try:
            input = loads(self.request.body)
            result = ElseSearch.getESFormatQuery(input['query'], calledFromREST=True)
            self.write(result)
        except ValueError:
            self.write({'status' : 'FAILED', 'reason' : 'Decoding input JSON has failed' })


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
