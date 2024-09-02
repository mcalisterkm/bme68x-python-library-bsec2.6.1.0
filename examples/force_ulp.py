# This example demonstrates the FORCED MODE

from bme68x import BME68X
import bme68xConstants as cst
import bsecConstants as bsec
from time import sleep

print('\nTESTING FORCED MODE WITH BSEC')
bme = BME68X(cst.BME68X_I2C_ADDR_HIGH, 0)
# Temp and Dur single values in Forced mode
bme.set_heatr_conf(cst.BME68X_ENABLE, 320, 100, cst.BME68X_FORCED_MODE)
bme.set_sample_rate(bsec.BSEC_SAMPLE_RATE_ULP)


def get_data(sensor):
    data = {}
    try:
        data = bme.get_bsec_data()
    except Exception as e:
        print(e)
        sleep(1)
        return None
    if data == None or data == {}:
        sleep(300)
        return None
    else:
        return data


while True:
        bsec_data = get_data(bme)
        while bsec_data == None:
                print("Looping zero data")
                bsec_data = get_data(bme)
        print(bsec_data)
