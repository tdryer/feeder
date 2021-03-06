#!/usr/bin/env python2
"""Hacked-together development server for feedreader.

Runs the feedreader server under the /api prefix, serves URI not containing a
dot public/index.html, servers everything else to public.
"""

import logging

import tornado.ioloop
import tornado.web

from feedreader.config import ConnectionConfig, FeederConfig
import feedreader.config
import feedreader.main


class PrefixedFallbackHandler(tornado.web.FallbackHandler):
    """FallbackHandler that removes the given prefix from requests."""

    def prepare(self):
        # hacky way of removing /api/
        self.request.uri = self.request.uri[4:]
        self.request.path = self.request.path[4:]
        super(PrefixedFallbackHandler, self).prepare()


class SingleFileHandler(tornado.web.StaticFileHandler):
    """FileHandler that only reads a single static file."""

    @classmethod
    def get_absolute_path(cls, root, path):
        return tornado.web.StaticFileHandler.get_absolute_path(root,
                                                               "index.html")


def main():
    logging.basicConfig(format='[%(levelname)s][%(name)s]: %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    feeder_config = FeederConfig.from_args()
    conn_config = ConnectionConfig.from_file(feeder_config.conn_filepath)

    feedreader_app = feedreader.main.get_application(feeder_config,
                                                     conn_config)
    application = tornado.web.Application([
        (r"/api/(.*)", PrefixedFallbackHandler, dict(fallback=feedreader_app)),
        (r"/(.*\..*)", tornado.web.StaticFileHandler, {"path": "public"}),
        (r"/(.*)", SingleFileHandler, {"path": "public"}),
    ])
    application.listen(feeder_config.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
