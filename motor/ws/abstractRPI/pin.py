'''
Abstract Raspberry Pi pin.
'''
from log import logger

try:
    import RPi.GPIO

    GPIOIN = GPIO.IN
    GPIOOUT = GPIO.OUT
    EMU = False
except ImportError:
    logger.warning("Could not import RPi.GPIO")
    # Set some nice values if we're emulating
    GPIOIN = 0
    GPIOOUT = 1
    EMU = True

class Pin(object):
    '''
    Abstraction of a pin on the RPI GPIO header.
    '''
    # Direction values.
    IN = GPIOIN
    OUT = GPIOOUT

    def __init__(self, number=0, pwm=False, emulate=False, pwm_freq=100):
        '''
        Construtor.
        
        :param number: Broadcomm style pin number.
        :param pwm: True to enable Pulse Width Modulation.
        :param emulate: Only print the RPI GPIO operations on the console. Do not actually execute it on the hardware.
        :param pwm_freq: Modulation frequency in hertz.
        '''
        logger.debug("Constructing pin: " + str(number))
        # Keep track of wether the pin has pin setip
        self.setup_done = False
        # Default direction is input
        self.direction = Pin.IN
        # The actual pin state.
        self.state = 0
        # The pin number using broadcommm numbering.
        self.number = number
        # 4 r331?
        self.emulate = emulate or EMU
        # PWM
        if pwm:
            logger.debug("Setting PWM on pin " + str(self.number))
            if not self.emulate:
                self.pwm = GPIO.setup(self.number, pwm_freq)
        else:
            self.pwm = None
        # Duty cycle
        self.duty = 0

    def setup(self, direction):
        '''
        Setup th I/O direction of the pin.
        
        :param direction: IN/OUT.
        '''
        self.direction = direction
        if direction == GPIOIN:
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
            logger.warning("(pin: " + str(self.number) +
                  "): using default pin configuration.")
        # Check direction
        if self.direction == GPIOIN:
            logger.warning("(pin: " + str(self.number) +
                  ")trying to write to an input pin.")
            return 0

        if state > 0:
            self.state = 1
        else:
            self.state = 0

        if self.pwm is not None:
            if state > 0:
                logger.debug("Starting PWM on pin " + str(self.number))
                if not self.emulate:
                    self.pwm.start()
            else:
                logger.debug("Stopping PWM on pin " + str(self.number))
                if not self.emulate:
                    self.pwm.stop()
        else:
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

    def set_direction(self, direction):
        self.direction = direction
        if direction == GPIOIN:
            str_dir = "input"
        else:
            str_dir = "output"
        logger.debug("Setting pin " + str(self.number) + " direction to " + str_dir)
        if not self.emulate:
            GPIO.setup(self.number, direction)

    def set_duty(self, duty):
        '''
        Set the duty cycle.
        '''
        if self.pwm is not None:
            logger.debug("Setting pin " + str(self.number) + " duty cycle to " +
                         str(duty) + "%")
            self.duty = duty
        else:
            logger.warning("(pin: " + str(self.number) +
                           ") Cannot set duty cycle for pin " +
                           str(self.number) + ", PWM is not enabled")

    def enable_pwm(self):
        if self.pwm is None:
            logger.debug("Enabling PWM on pin " + str(self.number))
            if not self.emulate:
                self.pwm = GPIO.setup(self.number, pwm_freq)
            else:
                self.pwm = 1
        else:
            logger.warning("(pin: " + str(self.number) +
                           ") PWM is all ready enabled.")
