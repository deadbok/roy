import RPi.GPIO as GPIO

from log import logger


class Button(object):
    '''
    This class is the interface to a button connected to the RPi
    '''
    websocket = list()
    '''
    Keep a list of WebSocket connections, to send the current status to.
    '''
    def __init__(self, pin=23, inv=False, press_callback=None, release_callback=None):
        '''
        Construct an object for a button connected to "pin"
        
        :param pin: The pin that the button is connected to, using Broadcomm numbering.
        '''
        # Save the pin number
        self.pin = pin
        # Save the callback functions
	if inv != True:
            self.press_callback = press_callback
            self.release_callback = release_callback
        else:
            self.press_callback = release_callback
            self.release_calback = press_callback
        # Set the pin as an input
        GPIO.setup(self.pin, GPIO.IN)
        #Setup event handling on the sensor
        if self.press_callback is not None:
            GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.event_dispatch, bouncetime=200)

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
            connection.write_message('Button (pin ' + str(self.pin) + '): ' + str(ret))

        return ret
    
    def event_dispatch(self, pin):
        '''
        Called on both rising and falling edge. Dispatch to the right handler.
        '''
	logger.debug('Input on button.')
        val = GPIO.input(self.pin)
        
        for connection in Button.websocket:
            connection.write_message('Button event (pin ' + str(self.pin) + '): ' + str(val))
        
        if val == 0:
            if self.press_callback is not None:
                self.press_callback()
        else:
            if self.release_callback is not None:
                self.release_callback()   
