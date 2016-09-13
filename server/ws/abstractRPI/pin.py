'''
Abstract Raspberry Pi pin.
'''
from log import logger

try:
    import RPi.GPIO
    
    GPIOIN = GPIO.IN
    GPIOOUT = GPIO.OUT
except ImportError:
    logger.warning("Could not import RPi.GPIO")
    # Set some nice values if we're emulating
    GPIOIN = 0
    GPIOOUT = 1

class Pin(object):
    '''
    Abstraction of a pin on the RPI GPIO header.
    '''
    # Direction values.
    IN = GPIOIN
    OUT = GPIOOUT
    
    def __init__(self, number = 0, emulate = False):
        '''
        Construtor.
        
        :param number: Broadcomm style pin number.
        :param debug: Enable debug output to the console.
        :param emulate: Only print the RPI GPIO operations on the console. Do not actually execute it on the hardware.
        '''
        logger.debug("Contructing pin: " + str(number))
        # Keep track of wether the pin has pin setip
        self.setup_done = False
        # Default direction is input
        self.direction = Pin.IN
        # The actual pin state.
        self.state = 0
        # The pin number using braodcommm numbering.
        self.number = number
        # 4 r331?
        self.emulate = emulate
         
    
    def setup(self, direction):
        '''
        Setup th I/O direction of the pin.
        
        :param direction: IN/OUT.
        '''
        self.direction  = direction
        if direction == GPIO.IN:
            str_dir = "input"
        else:
            str_dir = "output"
        logger.debug("Setting pin " + str(self.number) + " direction to " + str_dir)
        if not self.emulate:
            GPIO.setup(self.number, direction)
            
        self.setup_done = True

    def set(self, state):
        '''
        Set the state of a pin.
        '''
        # Check for setup
        if not self.setup_done:
            print("Warning: using default pin configuration.") 
        # Check direction
        if self.direction == Pin.OUT:
            print("Error: trying to write to an input pin.")
            return 0
        
        if state > 0:
            self.state = 1
        else:
            self.state = 0
            
        logger.debug("Setting pin " + str(self.number) + " to state " + str(self.state))
        if not self.emulate:
            GPIO.output(self.number, self.state)
            
    def get(self):
        '''
        Get the state of a pin.
        '''
        # Check for setup
        if not self.setup_done:
            print("Warning: using default pin configuration.") 

        if not self.emulate:
            self.state = GPIO.input(self.number)        
        
        logger.debug("Getting pin " + str(self.number) + " state " + str(self.state))

        return(self.state)
        