#!/usr/bin/python

import sys
import logging

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

from log import logger, init_file_log, init_console_log, close_log

import RPi.GPIO as GPIO

define("debug", default=False, help="Output debug mesages on console", type=bool)
define("port", default=8080, help="Listen on the given port", type=int)

WS = list()

class T9(object):
    websocket = list()

    def __init__(self, lpins=(17, 22, 27), rpins=(5, 6, 13)):
        self.lenable = lpins[0]
        self.renable = rpins[0]

        self.ld1 = lpins[1]
        self.rd1 = rpins[1]

        self.ld2 = lpins[2]
        self.rd2 = rpins[2]

        GPIO.setup(self.lenable, GPIO.OUT)
        GPIO.setup(self.ld1, GPIO.OUT)
        GPIO.setup(self.ld2, GPIO.OUT)

        GPIO.setup(self.renable, GPIO.OUT)
        GPIO.setup(self.rd1, GPIO.OUT)
        GPIO.setup(self.rd2, GPIO.OUT)

        self.lpwm = GPIO.PWM(self.lenable, 100)
        self.rpwm = GPIO.PWM(self.renable, 100)

    def addWebsocket(self, ws):
        '''
        Add a websocket connection and return its index.
        '''
        T9.websocket.append(ws)
        logger.debug("Added connection number " + str(len(T9.websocket)))
        return(len(T9.websocket) - 1)

    def removeWebsocket(self, index):
        del T9.websocket[index]
        logger.debug("Removed connection number " + str(index))

    def forward(self, speed=50):
        for connection in T9.websocket:
            connection.write_message('Forward: ' + str(speed))
        GPIO.output(self.ld1, 1)
        GPIO.output(self.rd1, 1)
        self.lpwm.start(speed)
        self.rpwm.start(speed)

    def turn(self, lspeed=50, rspeed=50):
        for connection in T9.websocket:
            connection.write_message('Turn: ' + str(lspeed) + ", " + str(rspeed))
        GPIO.output(self.ld1, 1)
        GPIO.output(self.rd1, 1)
        self.lpwm.start(lspeed)
        self.rpwm.start(rspeed)

    def reverse(self, speed):
        for connection in T9.websocket:
            connection.write_message('Reverse: ' + str(speed))
        GPIO.output(self.ld1, 0)
        GPIO.output(self.rd1, 0)
        GPIO.output(self.ld2, 1)
        GPIO.output(self.rd2, 1)
        self.lpwm.start(speed)
        self.rpwm.start(speed)

    def stop(self):
        for connection in T9.websocket:
            connection.write_message('Stop')
        GPIO.output(self.ld1, 0)
        GPIO.output(self.rd1, 0)
        GPIO.output(self.ld2, 0)
        GPIO.output(self.rd2, 0)
        self.lpwm.stop()
        self.rpwm.stop()

class Sensor(object):
    websocket = list()

    def __init__(self, pin=26):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)

    def addWebsocket(self, ws):
        '''
        Add a websocket connection and return its index.
        '''
        Sensor.websocket.append(ws)
        logger.debug("Added connection number " + str(len(T9.websocket)))
        return(len(T9.websocket) - 1)

    def removeWebsocket(self, index):
        del Sensor.websocket[index]
        logger.debug("Removed connection number " + str(index))

    def read(self):
        ret = GPIO.input(self.pin)
        for connection in Sensor.websocket:
            connection.write_message('Sensor: ' + str(ret))

        return ret



class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    robot = None
    sensor = None
    def __init__(self, application, request, **kwargs):
        super(WebSocketHandler, self).__init__(application, request, **kwargs)
        if WebSocketHandler.robot is None:
            WebSocketHandler.robot = T9()
            WebSocketHandler.Sensor = Sensor()
        tornado.ioloop.IOLoop.instance().add_callback(self.read_sensor())

    def open(self):
        logger.info("New connection was opened")
        self.rid = WebSocketHandler.robot.addWebsocket(self)
        self.sid = WebSocketHandler.sensor.addWebsocket(self)

    def on_message(self, message):
        logger.info('Incoming message: ' + message)
        for command in message.split('\n'):
            command = command.lower().strip()
            logger.debug("Command " + command)
            if (command == "forward"):
                WebSocketHandler.robot.forward()

            if (command == "left"):
                WebSocketHandler.robot.turn(50, 5)

            if (command == "right"):
                WebSocketHandler.robot.turn(5, 50)

            if (command == "reverse"):
                WebSocketHandler.robot.reverse(50)

            if (command == "stop"):
                WebSocketHandler.robot.stop()

    def on_close(self):
        logger.info("Connection closed")
        WebSocketHandler.robot.removeWebsocket(self.rid)
        WebSocketHandler.robot.removeWebsocket(self.sid)

    def read_sensor(self):
        if WebSocketHandler.sensor is not None:
            val = WebSocketHandler.sensor.read()
            logger.debug("Read sensor value: " + str(val))
        tornado.ioloop.IOLoop.instance().add_callback(self.read_sensor())


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

    # GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    http_server = tornado.httpserver.HTTPServer(APP)
    http_server.listen(options.port)
    logger.info("Listening on port: " + str(options.port))
    tornado.ioloop.IOLoop.instance().start()

    close_log()

if __name__ == "__main__":
    main()
