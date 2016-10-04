#!/usr/bin/python

from RPi import GPIO

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
motor_l = GPIO.PWM(17, 100)
motor_r = GPIO.PWM(5, 100)

#Buttons
GPIO.setup(23, GPIO.IN)
GPIO.setup(24, GPIO.IN)

#Sensors
GPIO.setup(26, GPIO.IN)


#Check for start button
print("Press the start button.")
start_b = GPIO.input(23)
while start_b  == 0:
   start_b = GPIO.input(23)


#Run the line follower until the stop button is pressed
stop_b = GPIO.input(24)
while stop_b == 0:
   #Get the sensor input
   sensor = GPIO.sensor(26)
   #Sensor 0 is dark, sensor 1 is light
   if sensor == 0:
       print("Going left")
       #Go slightly left
       GPIO.output(27, 1)
       GPIO.output(6, 1)
       motor_l.start(90)
       motor_r.start(100)
   else:
       print("Going right")
       #Go right
       GPIO.output(27, 1)
       GPIO.output(6, 1)
       motor_l.start(100)
       motor_r.start(70)

   #Get the stop button state
   stop_b = GPIO.input(24)

#We get here when somebody presses the stop button
print("You're done")
GPIO.output(27, 0)
GPIO.output(6, 0)
motor_l.stop()
motor_r.stop()
motor_l.cleanup()
motor_r.cleanup()
GPIO.cleanup()

