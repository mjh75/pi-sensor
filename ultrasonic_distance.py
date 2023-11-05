#!/usr/bin/env python3
import atexit
#Libraries
import time
import math
import logging
from RPi import GPIO
from gpiozero import DistanceSensor
from pulseio import PulseIn
import board
import adafruit_dht
from gpiozero import CPUTemperature


#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24



def get_environment(dht):
    """
    Read the humidity and temperature from the
    DHT11
    :return:
    """
    retval = {}
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    try:
        retval['humidity'] = dht.humidity
        logging.debug(f"Measured: {retval['humidity']}%")
    except RuntimeError as error:
        retval['humidity'] = 44
        logging.debug(f"Static: {retval['humidity']}%")
    try:
        retval['temperature'] = dht.temperature
        logging.debug(f"Measured: {retval['temperature']}C")
    except RuntimeError as error:
        retval['temperature'] = 25
        logging.debug(f"Static: {retval['temperature']}C")
    return retval


def determine_speed_of_sound(temperature):
    """
    Calculate the speed of sound based on the current temperature
    :param temperature:
    :return:
    """
    speed_of_sound = 331.3 * math.sqrt(1 + (temperature / 273.15))
    logging.debug(f"Calculated speed of sound: {speed_of_sound} m/s")
    return speed_of_sound

def distance(dht):
    """
    Measure the distance
    :return: retval dictionary with measured or calculated values
    """
    retval = {}
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    # save start_time
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.perf_counter_ns()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.perf_counter_ns()

    # time difference between start and arrival
    time_elapsed = stop_time - start_time

    environment = get_environment(dht)
    retval['humidity'] = environment['humidity']
    retval['temperature'] = environment['temperature']
    retval['speed_of_sound'] = determine_speed_of_sound(retval['temperature'])
    retval['distance'] = (time_elapsed / 1000000000 * retval['speed_of_sound']) / 2

    return retval


def cleanup():
    """
    Cleanup on exit
    :return:
    """
    GPIO.cleanup()
    logging.debug("Exiting")

if __name__ == '__main__':
    atexit.register(cleanup)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    # set GPIO direction (IN / OUT)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

    # Configure the DHT sensor
    dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=True)
    while True:
        data = distance(dhtDevice)
        cputemp = CPUTemperature().temperature
        print(f"Distance: {data['distance']:0.10f} m Temp: {data['temperature']:0.5f} C  Humidity: {data['humidity']:0.5f} %  CPU: {cputemp} C")
        time.sleep(1)
