#!/usr/bin/python

from RPi import GPIO
import time

while True:
    #Set pin numbering to Braodcomm mode
    GPIO.setmode(GPIO.BCM)

    #Left motor
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(27, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)

    #Right motor
    GPIO.setup(5, GPIO.OUT)
    GPIO.setup(6, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)

    #Variables to st the speed of the motor
    motor_r = GPIO.PWM(5, 100)
    motor_l = GPIO.PWM(17, 100)

    #Buttons
    GPIO.setup(23, GPIO.IN)
    GPIO.setup(24, GPIO.IN)

    #Sensors
    GPIO.setup(26, GPIO.IN)

    #Set motors to a known state
    GPIO.setup(27, 0)
    GPIO.setup(22, 1)
    GPIO.setup(6, 1)
    GPIO.setup(13, 0)
    motor_l.start(0)
    motor_r.start(0)

    #Check for start button
    print("Press the start button.")
    start_b = GPIO.input(23)
    while start_b  == 1:
       start_b = GPIO.input(23)

    direction = 0
    r_count = 0
    #Run the line follower until the stop button is pressed
    stop_b = GPIO.input(24)
    while stop_b == 1:
       #Get the sensor input
       sensor = GPIO.input(26)
       #Sensor 0 is dark, sensor 1 is light
       if sensor == 1:
	   if direction != 1:
               print("Going straight")
           direction = 1
           #Go slightly left
           motor_l.ChangeDutyCycle(22)
           motor_r.ChangeDutyCycle(25)
           r_count = 0
       else:
           if r_count < 100:
               if direction != 2:
                   print("Going right")
               direction = 2
               #Go right
               motor_l.ChangeDutyCycle(5)
               motor_r.ChangeDutyCycle(65)
               r_count += 1
	   else:
               if direction != 3:
                   print("Going left")
               direction = 3
               #Go left
               motor_l.ChangeDutyCycle(80)
               motor_r.ChangeDutyCycle(10)
       
       time.sleep(0.01)

       #Get the stop button state
       stop_b = GPIO.input(24)

    #We get here when somebody presses the stop button
    print("You are done")
    motor_l.stop()
    motor_r.stop()
    GPIO.cleanup()


