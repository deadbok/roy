#!/usr/bin/python

import sys
import logging

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

import RPi.GPIO as GPIO

from t9 import T9
from sensor import Sensor
from button import Button

from log import logger, init_file_log, init_console_log, close_log


# Setup "debug" and "port" as extra command line options.
define("debug", default=False, help="Output debug messages on console", type=bool)
define("port", default=8080, help="Listen on the given port", type=int)


LEFT_MOTOR = (17, 22, 17)
RIGHT_MOTOR = (5, 6, 13)
LIGHT_SENSOR = 26
START_BUTTON = 23
STOP_BUTTON =24


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        '''
        Show the index.html page
        '''
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    '''
    Handle the WebSocket connections from the web frontend.
    '''
    robot = None
    '''
    Robot or motor controller instance.
    '''
    sensor = None
    '''
    Sensor instance.
    '''
    start_btn = None
    '''
    Start button.
    '''
    stop_btn = None
    '''
    Stop button.
    '''
    running = False
    '''
    True when the line follower program is running
    '''
    def __init__(self, application, request, **kwargs):
        '''
        Constructor for the WebSocket handler.
        '''
        # If there is no robot instance create both that and the sensor instance.
        if WebSocketHandler.robot is None:
            WebSocketHandler.robot = T9(lpins=LEFT_MOTOR, rpins=RIGHT_MOTOR)
            WebSocketHandler.sensor = Sensor(pin=LIGHT_SENSOR, light_callback=self.event_light, dark_callback=self.event_dark)
            WebSocketHandler.start_btn = Button(pin=START_BUTTON, press_callback=self.event_run)
            WebSocketHandler.stop_btn = Button(pin=STOP_BUTTON, press_callback=self.event_stop)
        # Call the parent constructor.
        super(WebSocketHandler, self).__init__(application, request, **kwargs)

    def open(self):
        '''
        This is called when someone opens a connection.
        '''
        logger.info("New connection was opened")
        # Add the connection to the robot and sensor, so that the may cry out.
        self.rid = WebSocketHandler.robot.addWebsocket(self)
        self.sid = WebSocketHandler.sensor.addWebsocket(self)

    def on_message(self, message):
        '''
        This is called whenever a Websocket messages arrives.
        '''
        logger.info('Incoming message: ' + message)
        # Isolate the command, and call the actual handler in the robot class.
        for command in message.split('\n'):
            command = command.lower().strip()
            logger.debug("Command " + command)
            if (command == "forward"):
                WebSocketHandler.robot.forward(100, 90)

            if (command == "left"):
                WebSocketHandler.robot.forward(100, 50)

            if (command == "right"):
                WebSocketHandler.robot.forward(50, 100)

            if (command == "reverse"):
                WebSocketHandler.robot.reverse(100, 80)

            if (command == "stop"):
                WebSocketHandler.robot.stop()

    def on_close(self):
        '''
        Called when the WebSocket connection is closed
        '''
        logger.info("Connection closed")
        if self.sid is not None:
            WebSocketHandler.robot.removeWebsocket(self.rid)
            WebSocketHandler.robot.removeWebsocket(self.sid)

    def event_light(self):
        '''
        Called when the sensor input detects a falling edge (turning light)
        '''
        # Tell the value to any connected client.
        # the input should be zero since we're called on the falling edge.
        if WebSocketHandler.sensor is not None:
            logger.debug("Sensor is seeing light")

        if self.running:
            WebSocketHandler.robot.forward(25, 50)

    def event_dark(self):
        '''
        Called when the sensor input detects a rising edge (turning dark)
        '''
        logger.debug("Sensor event.")
        # Tell the value to any connected client.
        # the input should be zero since we're called on the falling edge.
        if WebSocketHandler.sensor is not None:
            logger.debug("Sensor is seeing darkness")
        
        if self.running:
            WebSocketHandler.robot.forward(50, 25)
            
    def event_run(self):
        '''
        Start the line following routines.
        '''
        logger.debug("Start button pressed")
        WebSocketHandler.running = True;

    def event_stop(self):
        '''
        Stop the line following routines.
        '''
        logger.debug("Stop button pressed")
        WebSocketHandler.running = False;


# Instantiate the Tornado application.
APP = tornado.web.Application(handlers=[(r"/", IndexHandler),
                                        (r"/ws", WebSocketHandler)],
                                      autoreload=True)


def main():
    '''
    Main entry point, start the server.
    '''
    # Tell Tornado to parse the command line for us.
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

    # Intital setup of the Raspberry Pi.
    # GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Create a Tornado HTTP and WebSocket server.
    http_server = tornado.httpserver.HTTPServer(APP)
    http_server.listen(options.port)
    logger.info("Listening on port: " + str(options.port))

    # Start the Tornado event loop.
    tornado.ioloop.IOLoop.instance().start()

    # Close the log if we're done.
    close_log()

if __name__ == "__main__":
    main()
