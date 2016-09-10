#!/usr/bin/python

import RPi.GPIO as GPIO
from sys import stdin, stdout

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

# Run through input from the WebSocket
# for color in stdin:
#    pass
#    color = color.lower().strip()
#    print(color)
#     if (color == "red"):
#         print('{ "red": ' + str(GPIO.input(22)) + ', "yellow": ' +
#               str(GPIO.input(27)) + ', "green": ' + str(GPIO.input(17)) + ' }')
#         GPIO.output(22, 1 - GPIO.input(22))
#         print('{ "red": ' + str(GPIO.input(22)) + ', "yellow": ' +
#               str(GPIO.input(27)) + ', "green": ' + str(GPIO.input(17)) + ' }')
#
#     if (color == "yellow"):
#         print('{ "red": ' + str(GPIO.input(22)) + ', "yellow": ' +
#               str(GPIO.input(27)) + ', "green": ' + str(GPIO.input(17)) + ' }')
#         GPIO.output(27, 1 - GPIO.input(27))
#         print('{ "red": ' + str(GPIO.input(22)) + ', "yellow": ' +
#               str(GPIO.input(27)) + ', "green": ' + str(GPIO.input(17)) + ' }')
#
#     if (color == "green"):
#         print('{ "red": ' + str(GPIO.input(22)) + ', "yellow": ' +
#               str(GPIO.input(27)) + ', "green": ' + str(GPIO.input(17)) + ' }')
#         GPIO.output(17, 1 - GPIO.input(17))
#         print('{ "red": ' + str(GPIO.input(22)) + ', "yellow": ' +
#               str(GPIO.input(27)) + ', "green": ' + str(GPIO.input(17)) + ' }')

print('{ "red": ' + str(GPIO.input(22)) + ', "yellow": ' +
      str(GPIO.input(27)) + ', "green": ' + str(GPIO.input(17)) + ' }')

# stdout.flush()
