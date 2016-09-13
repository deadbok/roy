#!/usr/bin/python

import sys
import logging

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

from log import logger, init_file_log, init_console_log, close_log

from abstractRPI.pins import Pins

# Emulate if the RPi.GPIO package is not available
try:
    import RPi.GPIO
    
    EMU = False
except ImportError:
    logger.warning("Could not import RPi.GPIO")
    EMU = True


define("debug", default=False, help="Output dbug mesages on console", type=bool)
define("emulate", default=False, help="Only emulate hardware calls", type=bool)    
define("port", default=8080, help="Listen on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        logger.debug("New connection was opened")

    def on_message(self, message):
        logger.debug("Incoming message: " + message)

    def on_close(self):
        logger.debug("Connection closed")


APP = tornado.web.Application(handlers=[(r"/", IndexHandler),
                                        (r"/ws", WebSocketHandler)],
                                      autoreload=True)


def main():
    '''
    Main entry point, start the server.
    '''
    global EMU
    tornado.options.parse_command_line()
    
    # Init logging to file
    init_file_log(logging.DEBUG)
    # Set the console logging level
    if options.debug:
        logging.StreamHandler(sys.stdout).setLevel(logging.DEBUG)
    else:
        init_console_log(logging.INFO)
        
    logger.info("Project intro WebSocket server.")
    
    rpio_pins = Pins(options.emulate or EMU)  

    http_server = tornado.httpserver.HTTPServer(APP)
    http_server.listen(options.port)
    logger.info("Listening on port: " + str(options.port))
    tornado.ioloop.IOLoop.instance().start()
        
    close_log()  

if __name__ == "__main__":
    main()