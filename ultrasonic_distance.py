#!/usr/bin/env python

#Libraries
import RPi.GPIO as GPIO
import Adafruit_DHT
from gpiozero import CPUTemperature
import time
import math
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    speed_of_sound = 331 * math.sqrt ( 1 + (temperature / 273))
    distance = (TimeElapsed * speed_of_sound) / 2
    cputemp = CPUTemperature()
 
    return(distance, temperature, humidity, cputemp.temperature)
 
if __name__ == '__main__':
    dist, temperature, humidity, cputemp = distance()
    print ('Distance: {0:0.2f} m Temp: {1:0.5f} C  Humidity: {2:0.5f} %  CPU: {3:0.5f} C'.format(dist, temperature, humidity, cputemp))
    time.sleep(1)
    GPIO.cleanup()
