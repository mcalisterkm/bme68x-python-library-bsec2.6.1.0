# This example demonstrates burn in of a BME688 with BSEC enabled
# It runs for 24 hr and waits for quality to reach 3
# Then it writes config and status to file.
# Status is useful when a sensor is restarted - faster to achieve quality data.
#
# Run me like this and I will run for around 24 hrs as a background task then finish
# $ nohup python3 burn_in.py &
# It is essential to provide bad and clean air during the 24 hours run-in.
# One successful approach is to put hand sanitiser (~60% ethyl alcohol) on a paper towel by the sensor for at least 30 min.
# TODO: Assumes a conf directory exists, would be better to test and create if it does not.
#

from bme68x import BME68X
import bme68xConstants as cnst
import bsecConstants as bsec
from time import sleep, time
from pathlib import Path
import os, errno

# Set up patameters.
temp_prof = [320, 100, 100, 100, 200, 200, 200, 320, 320, 320]
dur_prof =[5, 2, 10, 30, 5, 5, 5, 5, 5, 5]

# Check for conf directory and create if not present
try: os.makedirs("conf", mode=0o755, exist_ok = True)
except OSError as err:
# Reraise the error unless it's about an already existing directory
    if err.errno != errno.EEXIST or not os.path.isdir(newdir):
       raise

# Initialise the bme688 sensor
#  BME68X_I2C_ADDR_LOW is the pimoroni BME688 I2C default address
#  BME68X_I2C_ADDR_HIGH is the PI3G BME688 I2C default address
bme = BME68X(cnst.BME68X_I2C_ADDR_HIGH, 0)
print(bme.set_heatr_conf(cnst.BME68X_ENABLE, temp_prof, dur_prof, cnst.BME68X_PARALLEL_MODE))
sleep(0.1)
# This sets the rate for all virtual sensors
print(bme.set_sample_rate(bsec.BSEC_SAMPLE_RATE_LP))
# time.time() returns seconds since epoch
start_time = time()

# Function to get data from the sensor
def get_data(bme):
    data = {}
    try:
        # Read BSEC data
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

# Main loop
while True:
    # Read data  If null returned, read again, loop until data is returned
    bsec_data = get_data(bme)
    while bsec_data == None:
        bsec_data = get_data(bme)
    #
    print(bsec_data)
    sleep(1)
    # Run the sensor for 24 hours and check the IAQ qulity is 3 (Best Quality)
    # 24 hours in seconds is 86400
    # If the test succeeds write out the state and config data to files in the conf subdirectory.
    # The config files are written as print(<state>, <file_handle>) - readable strings.
    # The files are closed.
    # The break command ends the loop and the script terminates
    if  ((time() - start_time > 86400) and (bsec_data['iaq_accuracy'] == 3)):
        # write config, avoid name clash by using timestamp in filename
        conf_name = "conf_data" + str(int((time()) * 1000)) + ".txt"
        conf_path = str(Path(__file__).resolve().parent.joinpath('conf', conf_name))
        conf_file = open(conf_path, 'w')
        conf_file.write(str(bme.get_bsec_conf()))
        # write state, avoid name clash by using timestamp in filename
        state_name = "state_data" + str(int((time()) * 1000)) + ".txt"
        state_path = str(Path(__file__).resolve().parent.joinpath('conf', state_name))
        state_file = open(state_path, 'w')
        state_file.write(str(bme.get_bsec_state()))
        state_file.close()
        conf_file.close()
        break
    else:
        # If we get here the test for accuracy or time failed so loop again.
        continue
