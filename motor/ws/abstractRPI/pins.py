'''
Abstract Raspberry Pi pin header
'''
from log import logger
from pin import Pin

try:
    import RPi.GPIO
except ImportError:
    logger.warning("Could not import RPi.GPIO")


class Pins(object):
    def __init__(self, emulate=False):
        logger.debug("Constructing pins")
        self.pin = list()
        # Append nothing at the zero'th index to align with hardware pin count.
        self.pin.append(None)

        # Create the pins
        for i in range(1, 28):
            self.pin.append(Pin(number=i, emulate=emulate))

        logger.debug("Turning off GPIO warnings.")
        if not emulate:
            GPIO.setwarnings(False)
        logger.debug("Setting Broadcomm pin numbering scheme.");
        if not emulate:
            GPIO.setmode(GPIO.BCM)

        self.emulate = emulate

    def print_pin_states(self):
        '''
        Do a pretty print of all I/O pins state.
        '''
        lines = ["", "", "", ""]
        for i in range(1, 13):
            npin = str(i)
            if len(npin) == 1:
                npin = " " + npin
            npin = " " + npin

            pstate = "  " + str(self.pin[i].get())

            lines[0] += npin
            lines[1] += pstate

        for i in range(14, 26):
            npin = str(i)
            if len(npin) == 1:
                npin = " " + npin
            npin = " " + npin

            pstate = "  " + str(self.pin[i].get())

            lines[2] += pstate
            lines[3] += npin

        for line in lines:
            logger.info(line)

