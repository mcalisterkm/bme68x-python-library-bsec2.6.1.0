# This example tests and demonstrates the BME68X_PARALLEL_MODE with ULP (300 sec low power)
# With use of BSEC

from bme68x import BME68X
import bme68xConstants as cnst
import bsecConstants as bsec
from time import sleep


temp_prof = [320, 100, 100, 100, 200, 200, 200, 320, 320, 320]
dur_prof = [5, 2, 10, 30, 5, 5, 5, 5, 5, 5]

print('\n\nPARALLEL MODE WITH BSEC')
sensor = BME68X(cnst.BME68X_I2C_ADDR_HIGH, 0)
# Set the heater up
print(sensor.set_heatr_conf(cnst.BME68X_ENABLE,
      temp_prof, dur_prof, cnst.BME68X_PARALLEL_MODE))
# set ULP sample rate
sensor.set_sample_rate(bsec.BSEC_SAMPLE_RATE_ULP)

def get_data(sensor):
    data = {}
    try:
        data = sensor.get_bsec_data()
    except Exception as e:
        print(e)
        sleep(1)
        return None
    if data == {} or data == None:
        sleep(300)
        return None
    else:
        return data

while True:
	bsec_data = get_data(sensor)
	while bsec_data == None:
		print("Looping zero data")
		bsec_data = get_data(sensor)
	print(bsec_data)
