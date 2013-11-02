"""Main entry point for API server."""

import tornado.ioloop
import tornado.web
import sys


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("Hello, world")


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    application.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.instance().start()
