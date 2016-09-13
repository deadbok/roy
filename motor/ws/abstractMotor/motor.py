from log import logger

from abstractRPI.pins import Pin

class Motor(object):
    '''
    Simple motor model, no PWM yet.
    '''
    FORWARD = 0
    REVERSE = 1

    def __init__(self, pins, enable, in1, in2):
        """
        Construct a Motor object.
        
        :param pins: Object to provide access to RPi GPIO pins.
        :type pins: abstractRPI.pin.Pins
        :param enable: Broadcomm number of the enable pin connection.
        :type enable: int
        :param in1: Broadcomm number of the first driver input pin connection.
        :type in1: int
        :param in2: Broadcomm number of the second driver input pin connection.
        :type in2: int
        """
        logger.debug("Constructing motor.")
        self.enable = False
        self.direction = Motor.FORWARD
        self.speed = 0

        self.pins = pins
        self.enable_pin = enable
        self.input1_pin = in1
        self.input2_pin = in2

        self.pins.pin[self.enable_pin].setup(Pin.OUT)
        self.pins.pin[self.enable_pin].enable_pwm()
        self.pins.pin[self.input1_pin].setup(Pin.OUT)
        self.pins.pin[self.input2_pin].setup(Pin.OUT)

    def set_speed(self, speed):
        """
        Set the motor speed in percent.
        
        :param speed: Speed in percent.
        :type speed: int
        """
        logger.debug("Setting motor speed to " + str(speed) + "%")
        self.speed = speed
        self.pins.pin[self.enable_pin].duty(speed)

    def get_speed(self):
        """
        Get the motor speed in percent.
        """
        logger.debug("Getting motor speed " + str(self.speed) + "%")
        return self.speed

    def set_direction(self, direction):
        """
        Set the motor direction.
        
        :param direction: Motor.FORWARD or Motor.REVERSE
        :type direction: int
        """
        if direction == Motor.FORWARD:
            logger.debug("Setting motor direction to forward")
            self.pins.pin[self.input1_pin].set(1)
            self.pins.pin[self.input2_pin].set(0)
        elif direction == Motor.REVERSE:
            self.pins.pin[self.input1_pin].set(0)
            self.pins.pin[self.input2_pin].set(1)
            logger.debug("Setting motor direction to reverse")
        else:
            logger.warning("Invalid motor direction")
            return

        self.direction = direction

    def get_direction(self):
        """
        Get the motor direction.
        """
        if self.direction == Motor.FORWARD:
            logger.debug("Getting motor direction forward")
        elif self.direction == Motor.REVERSE:
            logger.debug("Getting motor direction reverse")
        else:
            logger.warning("Invalid motor direction")

        return self.direction

    def set_enable(self, enable):
        """
        Turn the motor on or off.
        
        :param enable: True to start the motor, False to stop it.
        :type enable: Booloean
        """
        if enable:
            logger.debug("Turning motor on.")
            self.set_direction(self.direction)
            self.pins.pin[self.enable_pin].set(True)
        else:
            logger.debug("Turning motor off")
            self.pins.pin[self.enable_pin].set(False)

        self.enable = enable

    def get_enable(self):
        """
        Get the motor state.
        """
        if self.enable:
            logger.debug("Motor is running.")
        else:
            logger.debug("Motor is not running")

        return self.enable
