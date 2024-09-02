#!/usr/bin/python3
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
#
# Modified to use a separate I2C-3 bus to be run at 100 KHz (slow) for the PM2.5 sensor
# This allows running other I2C sensors (BME688) on the standard I2C bus a lot faster.
# To use I2C-3 the Adafruit ExtendedI2C library is required
# To display results on an OLED screen I use Luma and PIL.
# Keith McAlister 2022

"""
Example sketch to connect to PM2.5 sensor with either I2C or UART.
"""

# pylint: disable=unused-import
import time
import csv
import board
# import busio
from adafruit_extended_bus import ExtendedI2C as I2C
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
from pathlib import Path
from PIL import ImageFont
from luma.core.render import canvas
from luma.core.interface.serial import i2c as l_i2c
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106, ws0010

reset_pin = None
# If you have a GPIO, its not a bad idea to connect it to the RESET pin
# reset_pin = DigitalInOut(board.G0)
# reset_pin.direction = Direction.OUTPUT
# reset_pin.value = False


# For use with a computer running Windows:
# import serial
# uart = serial.Serial("COM30", baudrate=9600, timeout=1)

# For use with microcontroller board:
# (Connect the sensor TX pin to the board/computer RX pin)
# uart = busio.UART(board.TX, board.RX, baudrate=9600)

# For use with Raspberry Pi/Linux:
# import serial
# uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)

# For use with USB-to-serial cable:
# import serial
# uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.25)

# Connect to a PM2.5 sensor over UART
# from adafruit_pm25.uart import PM25_UART
# pm25 = PM25_UART(uart, reset_pin)

# Create library object, use 'slow' 100KHz frequency!
# i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
i2c = I2C(3, frequency=100000) # Device is /dev/i2c-3
# Connect to a PM2.5 sensor over I2C
pm25 = PM25_I2C(i2c, reset_pin)
# Open log file for writing data
log_file = "pm_data" + str(int((time.time()) * 1000)) + ".csv"
log_path = str(Path(__file__).resolve().parent.joinpath('log', log_file))
pm_log = open(log_path, 'w')
writer = csv.writer(pm_log)
header = ['timestamp', 'pm10', 'pm25', 'pm100']
writer.writerow(header)
# All set
print("Found PM2.5 sensor, reading data...")

def get_screen1():
    serial = l_i2c(port=1, address=0x3C)
    disp_device1 = sh1106(serial, width=128, height=64, rotate=2)
    return disp_device1

def disp_template_1(pm10_env, pm25_env, pm100_env, note, disp_device1):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 13)
    with canvas(disp_device1) as draw:
        draw.rectangle(disp_device1.bounding_box, outline="white", fill="black")
        draw.text((5, 2), pm10_env, font=font2, fill="white")
        draw.text((5, 14), pm25_env, font=font2, fill="white")
        draw.text((5, 26), pm100_env, font=font2, fill="white")
        draw.text((5, 42), note, font=font2, fill="white")

disp_device1 = get_screen1()
while True:
    time.sleep(30)

    try:
        aqdata = pm25.read()
        # print(aqdata)
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        continue
    # finally:
    #    pm_log.close()

   # print()
   # print("Concentration Units (standard)")
   # print("---------------------------------------")
   # print(
   #     "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
   #     % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
   # )
   # print("Concentration Units (environmental)")
   # print("---------------------------------------")
   # print(
   #     "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
   #     % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
   # )
   # print("---------------------------------------")
   # print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
   # print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
   #

    if aqdata == None or aqdata == {}:
        sleep(0.1)
    else:
        print (str(time.strftime("%a %b %d %H:%M:%S %Y GMT", time.gmtime())))
        print(
              "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
              % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
             )

        pm10_env = "PM 1.0 : " + "{:,}".format(aqdata["pm10 env"]) + " \u00B5" + "g/m" + "\u00B3"
        pm25_env = "PM 2.5 : " + "{:,}".format(aqdata["pm25 env"]) + " \u00B5" + "g/m" + "\u00B3"
        pm100_env = "PM 10.0 : " + "{:,}".format(aqdata["pm100 env"]) + " \u00B5" + "g/m" + "\u00B3"
        note = "2.5>25 BAD, 10>50 BAD"

        row_data =[(str(time.strftime("%a %b %d %H:%M:%S %Y GMT", time.gmtime()))), aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"]]
        writer.writerow(row_data)
        pm_log.flush()
        # disp_template_1(pm10_env, pm25_env, pm100_env, note, disp_device1=get_screen1())
        disp_template_1(pm10_env, pm25_env, pm100_env, note, disp_device1)