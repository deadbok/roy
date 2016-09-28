import RPi.GPIO as GPIO

from log import logger


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
        Remove a WebSocket connection front the list of receivers
        
        :param index: The index of the WebSocket to remove.
        '''
        del T9.websocket[index]
        logger.debug("Removed connection number " + str(index))

    def forward(self, lspeed=100, rspeed=75):
        '''
        Make the robot go forward.
        
        :param lspeed: The speed to apply to the left motor.
        :param lspeed: The speed to apply to the right motor.
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
        
        :param lspeed: The speed to apply to the left motor.
        :param lspeed: The speed to apply to the right motor.
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
