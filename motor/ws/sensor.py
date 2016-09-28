import RPi.GPIO as GPIO

from log import logger


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
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.event_dispatch, bouncetime=100)

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
            connection.write_message('Sensor (pin ' + str(self.pin) + '): ' + str(ret))

        return ret
    
    def event_dispatch(self, pin):
        '''
        Called on both rising and falling edge. Dispatch to the right handler.
        '''
        val = GPIO.input(self.pin)
        
        for connection in Sensor.websocket:
            connection.write_message('Sensor event (pin ' + str(self.pin) + '): ' + str(val))
            
        if val == 0:
            if self.light_callback is not None:
                self.light_callback()
        else:
            if self.dark_callback is not None:
                self.dark_callback()