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
from abstractMotor.motor import Motor


# Emulate if the RPi.GPIO package is not available
try:
    import RPi.GPIO as GPIO

    EMU = False
except ImportError:
    logger.warning("Could not import RPi.GPIO")
    EMU = True


define("debug", default=False, help="Output debug mesages on console", type=bool)
define("emulate", default=False, help="Only emulate hardware calls", type=bool)
define("port", default=8080, help="Listen on the given port", type=int)

# Motor instances-
MOTOR_ONE = None
MOTOR_TWO = None


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        logger.debug("New connection was opened")

    def on_message(self, message):
        print('Incoming message: ' + message)
        for command in message.split('\n'):
            command = command.lower().strip()
            logger.debug("Command " + command)
            if (command == "forward"):
                MOTOR_ONE.set_direction(Motor.FORWARD)
                MOTOR_TWO.set_direction(Motor.FORWARD)
                MOTOR_ONE.set_enable(True)
                MOTOR_TWO.set_enable(True)

            if (command == "left"):
                MOTOR_ONE.set_enable(False)
                MOTOR_TWO.set_direction(Motor.FORWARD)
                MOTOR_TWO.set_enable(True)

            if (command == "right"):
                MOTOR_ONE.set_direction(Motor.FORWARD)
                MOTOR_ONE.set_enable(True)
                MOTOR_TWO.set_enable(False)

            if (command == "reverse"):
                MOTOR_ONE.set_direction(Motor.FORWARD)
                MOTOR_TWO.set_direction(Motor.FORWARD)
                MOTOR_ONE.set_enable(True)
                MOTOR_TWO.set_enable(True)

            if (command == "stop"):
                MOTOR_ONE.set_enable(False)
                MOTOR_TWO.set_enable(False)

    def on_close(self):
        logger.debug("Connection closed")


APP = tornado.web.Application(handlers=[(r"/", IndexHandler),
                                        (r"/ws", WebSocketHandler)],
                                      autoreload=True)


def main():
    '''
    Main entry point, start the server.
    '''
    global EMU, MOTOR_ONE, MOTOR_TWO

    tornado.options.parse_command_line()

    # Init logging to file
    init_file_log(logging.DEBUG)
    # Set the console logging level
    if options.debug:
        logger.setLevel(logging.DEBUG)
        options.logging = "debug"
        tornado.log.enable_pretty_logging(options,
                                          logging.getLogger("tornado.access"))
        tornado.log.enable_pretty_logging(options,
                                          logging.getLogger("tornado.application"))
        tornado.log.enable_pretty_logging(options,
                                          logging.getLogger("tornado.general"))
    else:
        logger.setLevel(logging.INFO)

    logger.info("Project intro WebSocket server.")
    if options.emulate or EMU:
	logger.info("RPi GPIO's are emulated")
    rpio_pins = Pins(options.emulate or EMU)

    MOTOR_ONE = Motor(rpio_pins, 17, 22, 27)
    MOTOR_TWO = Motor(rpio_pins, 5, 6, 13)

    http_server = tornado.httpserver.HTTPServer(APP)
    http_server.listen(options.port)
    logger.info("Listening on port: " + str(options.port))
    tornado.ioloop.IOLoop.instance().start()

    close_log()

if __name__ == "__main__":
    main()
