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


# Setup "debug" and "port" as extra command line options.
define("debug", default=False, help="Output debug mesages on console", type=bool)
define("port", default=8080, help="Listen on the given port", type=int)


LEFT_MOTOR = (17, 22, 17)
RIGHT_MOTOR = (5, 6, 13)
LIGHT_SENSOR = 26
START_BUTTON = 23
STOP_BUTTON =24


class T9(object):
    '''
    This class is the interface to the L293D H-bridge and the motors connected to it.
    '''
    websocket = list()
    '''
    Keep a list of WebSocket connections, to send the current status to.
    '''
    def __init__(self, lpins=(17, 22, 27), rpins=(5, 6, 13)):
        '''
        Construct a T9 motor controller instance.
         
        :param lpins: Tuple of the enable and direction pins of the left motor using Bradcomm numbering.
        :param rpins: Tuple of the enable and direction pins of the right motor using Bradcomm numbering.
        '''
        # Save the pin-mapping of the enable pins.
        self.lenable = lpins[0]
        self.renable = rpins[0]

        # Save the pin-mapping of the directional pins.
        self.ld1 = lpins[1]
        self.rd1 = rpins[1]
        self.ld2 = lpins[2]
        self.rd2 = rpins[2]

        # Set all left motor pins as output
        GPIO.setup(self.lenable, GPIO.OUT)
        GPIO.setup(self.ld1, GPIO.OUT)
        GPIO.setup(self.ld2, GPIO.OUT)
        # Set all right motor pins as output
        GPIO.setup(self.renable, GPIO.OUT)
        GPIO.setup(self.rd1, GPIO.OUT)
        GPIO.setup(self.rd2, GPIO.OUT)

        # Use pulse width modulation on the enable pins of both motors.
        self.lpwm = GPIO.PWM(self.lenable, 100)
        self.rpwm = GPIO.PWM(self.renable, 100)

    def addWebsocket(self, ws):
        '''
        Add a WebSocket connection and return its index.
        
        :param ws: WebSocket connection.
        :type ws: tornado.websocket.WebSocketHandler
        '''
        # Add the new websocker to the list of receivers.
        T9.websocket.append(ws)
        logger.debug("Added connection number " + str(len(T9.websocket)))
        # Return the position in the list of the new receiver.
        return(len(T9.websocket) - 1)

    def removeWebsocket(self, index):
        '''
        Remove a websocker connection front the list of receivers
        
        :param index: The index of the WebSocket to remove.
        '''
        del T9.websocket[index]
        logger.debug("Removed connection number " + str(index))

    def forward(self, lspeed=100, rspeed=75):
        '''
        Make the robot go forward, using th same speed for both motors.
        
        :param speed: The speed to pply to both motors.
        '''
        # Tell the connected clients what we're about to do
        for connection in T9.websocket:
            connection.write_message('Forward: ' + str(lspeed) + ', ' + str(rspeed))
        # Set both motors to forward direction.
        GPIO.output(self.ld1, 1)
        GPIO.output(self.rd1, 1)
        GPIO.output(self.ld2, 0)
        GPIO.output(self.rd2, 0)
        # Apply the same speed to both motors
        self.lpwm.start(lspeed)
        self.rpwm.start(rspeed)

    def reverse(self, lspeed=75, rspeed=100):
        '''
        Make the robot go backwards
        
        :param speed: The speed applied to both motors.
        '''
        # Tell the connected clients what we're about to do
        for connection in T9.websocket:
            connection.write_message('Reverse: ' + str(lspeed) + ', ' + str(rspeed))
        # Set the direction of the motor to backwards
        GPIO.output(self.ld1, 0)
        GPIO.output(self.rd1, 0)
        GPIO.output(self.ld2, 1)
        GPIO.output(self.rd2, 1)
        # Apply the same speed to both motors
        self.lpwm.start(lspeed)
        self.rpwm.start(rspeed)

    def stop(self):
        # Tell the connected clients what we're about to do
        for connection in T9.websocket:
            connection.write_message('Stop')
        # Set all directional outputs to off
        GPIO.output(self.ld1, 0)
        GPIO.output(self.rd1, 0)
        GPIO.output(self.ld2, 0)
        GPIO.output(self.rd2, 0)
        # Shut off the PWM signal.
        self.lpwm.stop()
        self.rpwm.stop()


class Sensor(object):
    '''
    This class is the interface to the comparator board and IR sensor
    '''
    websocket = list()
    '''
    Keep a list of WebSocket connections, to send the current status to.
    '''
    def __init__(self, pin=26, light_callback=None, dark_callback=None):
        '''
        Construct an object for a sensor connected to "pin"
        
        :param pin: The pin that the sensor board is connected to, using Broadcomm numbering.
        '''
        # Save the pin number
        self.pin = pin
        # Save the callback functions
        self.light_callback = light_callback
        self.dark_callback = dark_callback
        # Set the pin as an input
        GPIO.setup(self.pin, GPIO.IN)
        #Setup event handling on the sensor
        if self.light_callback is not None:
            GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.light_callback, bouncetime=100)
        if self.dark_callback is not None:
            GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.dark_callback, bouncetime=100)

    def addWebsocket(self, ws):
        '''
        Add a WebSocket connection and return its index.
        '''
        Sensor.websocket.append(ws)
        logger.debug("Added connection number " + str(len(Sensor.websocket)))
        return(len(Sensor.websocket) - 1)

    def removeWebsocket(self, index):
        '''
        Remove a WebSocket connection from the list of clients.
        '''
        del Sensor.websocket[index]
        logger.debug("Removed connection number " + str(index))

    def read(self):
        '''
        Read the state of the sensor.
        
        :return: 0 for low, 1 for high
        '''
        ret = GPIO.input(self.pin)
        for connection in Sensor.websocket:
            connection.write_message('Sensor: ' + str(ret))

        return ret
    

class Button(object):
    '''
    This class is the interface to a button connected to the RPi
    '''
    websocket = list()
    '''
    Keep a list of WebSocket connections, to send the current status to.
    '''
    def __init__(self, pin=23, press_callback=None, release_callback=None):
        '''
        Construct an object for a button connected to "pin"
        
        :param pin: The pin that the button is connected to, using Broadcomm numbering.
        '''
        # Save the pin number
        self.pin = pin
        # Save the callback functions
        self.press_callback = press_callback
        self.release_callback = release_callback
        # Set the pin as an input
        GPIO.setup(self.pin, GPIO.IN)
        #Setup event handling on the sensor
        if self.press_callback is not None:
            GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.press_callback, bouncetime=200)
        if self.release_callback is not None:
            GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.release_callback, bouncetime=200)

    def addWebsocket(self, ws):
        '''
        Add a WebSocket connection and return its index.
        '''
        Button.websocket.append(ws)
        logger.debug("Added connection number " + str(len(Button.websocket)))
        return(len(Button.websocket) - 1)

    def removeWebsocket(self, index):
        '''
        Remove a WebSocket connection from the list of clients.
        '''
        del Button.websocket[index]
        logger.debug("Removed connection number " + str(index))

    def read(self):
        '''
        Read the state of the button.
        
        :return: 1 for pressed, 0 otherwise
        '''
        ret = GPIO.input(self.pin)
        for connection in Button.websocket:
            connection.write_message('Sensor: ' + str(ret))

        return ret



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
    light_btn = None
    '''
    Calibrate light value button.
    '''
    dark_btn = None
    '''
    Calibrate dark button.
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
            WebSocketHandler.sensor = Sensor(pin=LIGHT_SENSOR, light_callback=self.event_light(), dark_callback=self.event_dark())
            WebSocketHandler.start_btn = Button(pin=START_BUTTON, press_callback=self.event_run())
            WebSocketHandler.stop_btn = Button(pin=STOP_BUTTON, press_callback=self.event_stop())
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
            logger.debug("Read is seeing light: " + str(val))

        if self.running:
            WebSocketHandler.robot.forward(25, 50)

    def event_dark(self):
        '''
        Called when the sensor input detects a rising edge (turning dark)
        '''
        # Tell the value to any connected client.
        # the input should be zero since we're called on the falling edge.
        if WebSocketHandler.sensor is not None:
            logger.debug("Read is seeing darkness: " + str(val))
        
        if self.running:
            WebSocketHandler.robot.forward(50, 25)
            
    def event_run(self):
        '''
        Start the line following routines.
        '''
        WebSocketHandler.running = True;

    def event_stop(self):
        '''
        Stop the line following routines.
        '''
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
