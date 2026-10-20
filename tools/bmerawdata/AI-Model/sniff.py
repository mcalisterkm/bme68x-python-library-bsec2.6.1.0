#!/usr/bin/python3
# Sniff air / ethanol
# Keith McAlister 6th May 2023 based on the PI3G Meat and Cheese code.

from bme68x import BME68X
import bme68xConstants as cst
import bsecConstants as bsec
from time import sleep
from pathlib import Path
import json

# The exported model from AI Studio must be for BSEC2.6.1.0 the first four bytes of the .config file indicate the version number.
# The .h and .c that studio exports with the config file also have a reference to bsec_config_selectivity[1974] = ...
# So whilst BSEC can use multiple config files we use only one config and this function chops off the 1974 header - strictly speaking is chops off the first 4 bytes in the slicer [4:].


# This is the config file output by AI_Studio
config_file = 'Air-Coffee_354_11.config'
config_path = str(Path(__file__).resolve().parent.joinpath(config_file))
def read_conf(path: str):
    with open(path, 'rb') as ai_conf:
        conf = [int.from_bytes(bytes([b]), 'little') for b in ai_conf.read()]
        conf = conf[4:]
    return conf

def main():
    # Open the I2C communications and set the operating mode
    bme = BME68X(cst.BME68X_I2C_ADDR_LOW, 0)
    bme.set_sample_rate(bsec.BSEC_SAMPLE_RATE_LP)
    # report on the BME688 and BSEC version
    print(f'SENSOR: {bme.get_variant()} BSEC: {bme.get_bsec_version()}')

    ai_model_weights = read_conf(config_path)
    print(f'SET BSEC CONF {bme.set_bsec_conf(ai_model_weights)}')

    # Air and Coffee - two subscriptions (0,1)
    print(f'SUBSCRIBE GAS ESTIMATES {bme.subscribe_gas_estimates(2)}')

    # initialise the sensor
    print(f'INIT BME68X {bme.init_bme68x()}')

    print('\n\nSTARTING MEASUREMENT\n')

    while(True):
        # print(bme.get_bsec_data())
        try:
            data = bme.get_digital_nose_data()
        except Exception as e:
            print(e)
            main()
        if data:
            # for entry in bme.get_digital_nose_data():
            entry = data[-1]
            # print(f'{entry}')
            print(f'NORMAL AIR {entry["gas_estimate_1"]:.1%}\nCOFFEE {entry["gas_estimate_2"]:.1%}')
            print()

            NormalAir = "{:.1%}".format(entry["gas_estimate_1"])
            Coffee = "{:.1%}".format(entry["gas_estimate_2"])

            # This bit is from the Meat and Cheese PI3G demo - ist writes out the data to file as JASON
            d = {
                'NormalAir': NormalAir,
                'Coffee': Coffee,
            }

            with open('/home/kpi/sniff-data.json', 'w') as file:
                json.dump(d, file)



if __name__ == '__main__':
    main()
