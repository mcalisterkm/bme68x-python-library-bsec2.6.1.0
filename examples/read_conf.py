# This reads a saved BME688 State file, and loads it to update the sensor state
# Using the sensor state from a time of high quality readings allows the sensor to restart get to a good place quickly.
# Both config and state are Python arrays of int, and the file character strings need to be read and converted.
# See burn_in.py which creates the config and state files.
# TODO: Turn the read file and convert to Int array to a function.

from bme68x import BME68X
import bme68xConstants as cnst
import bsecConstants as bsec
from time import sleep, time
from pathlib import Path
import csv
# Amend this to your state file name
state_file_name = "state_data1644485092616.txt"

# Open the state file, read it stripping the [] first and last characters.
# Split the string on ,
# iterate the list and convert char to int
def readState(state_file_name):
    state_path = str(Path(__file__).resolve().parent.joinpath('conf', state_file_name))
    state_file = open(state_path, 'r')
    # strip the brackets [.....]
    state_str =  state_file.read()[1:-1]
    # split on delimiter ,
    state_list = state_str.split(",")
    state_int = [int(x) for x in state_list]
    return(state_int)
    # Debug - Checking the right types are present
    # print(state_int)
    # print("-----------------\n")
    # print(type(state_int))
    # print(type(state_int[1]))

# Set params
temp_prof = [320, 100, 100, 100, 200, 200, 200, 320, 320, 320]
dur_prof =[5, 2, 10, 30, 5, 5, 5, 5, 5, 5]
# Initialise the sensor
#  BME68X_I2C_ADDR_LOW is the pimoroni BME688 I2C default address
#  BME68X_I2C_ADDR_HIGH is the PI3G BME688 I2C default address
bme = BME68X(cnst.BME68X_I2C_ADDR_LOW, 0)
print(bme.set_heatr_conf(cnst.BME68X_ENABLE, temp_prof, dur_prof, cnst.BME68X_PARALLEL_MODE))
sleep(0.1)
# print(bme.get_bsec_state())
state_int = readState(state_file_name)
print(bme.set_bsec_state(state_int))
print("Config set....")
print(bme.set_sample_rate(bsec.BSEC_SAMPLE_RATE_LP))
print("Rate Set")

def get_data(bme):
    data = {}
    try:
        data = bme.get_bsec_data()
    except Exception as e:
        print(e)
        return None
    if data == None or data == {}:
        sleep(1)
        return None
    else:
        sleep(3)
        return data

while True:
    bsec_data = get_data(bme)
    while bsec_data == None:
        bsec_data = get_data(bme)
    print(bsec_data)
    sleep(1)
