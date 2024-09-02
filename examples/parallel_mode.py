# This example tests and demonstrates the BME68X_PARALLEL_MODE
# Without use of BSEC and
# With use of BSEC

from bme68x import BME68X
import bme68xConstants as cnst
import bsecConstants as bsec
from time import sleep


temp_prof = [320, 100, 100, 100, 200, 200, 200, 320, 320, 320]
dur_prof = [5, 2, 10, 30, 5, 5, 5, 5, 5, 5]

print('PARALLEL MODE W/O BSEC')
sensor = BME68X(cnst.BME68X_I2C_ADDR_HIGH, 0)
print(sensor.set_heatr_conf(cnst.BME68X_ENABLE,
      temp_prof, dur_prof, cnst.BME68X_PARALLEL_MODE))
# print(sensor.get_data())
res = sensor.get_data()
# print('Length ', len(res))
# print(res)
# get_data returns a list of dictionaries, one for each temp/dur profile step: 0-9 
# so below data gets a dictionary in each iteration, which we unpack to get the values
for data in res:
	# print("Line", data)
	sample = "SampleNo: " + "{: ^2d}".format(data['sample_nr'])
	temp = "Temperature: " + "{: ^4.1f}".format(data['raw_temperature']) + " \u00B0"+ "C"
	hum = "Humidity: " +  "{: ^4.1f}".format(data['raw_humidity']) + "%"
	pres = "Pressure: " + "{: ^4.1f}".format(data['raw_pressure'] )  
	gas = "Gas: " + "{: ^4.1f}".format(data['raw_gas'] * 1000)  
	print(sample, temp, hum, pres, gas)

print('\n\nPARALLEL MODE WITH BSEC')
sensor = BME68X(cnst.BME68X_I2C_ADDR_HIGH, 0)
#sensor.set_sample_rate(bsec.BSEC_SAMPLE_RATE_HIGH_PERFORMANCE)
print(sensor.set_heatr_conf(cnst.BME68X_ENABLE,
      temp_prof, dur_prof, cnst.BME68X_PARALLEL_MODE))
sensor.set_sample_rate(bsec.BSEC_SAMPLE_RATE_LP)

def get_data(sensor):
    data = {}
    try:
        data = sensor.get_bsec_data()
    except Exception as e:
        print(e)
        sleep(1)
        return None
    if data == {} or data == None:
        sleep(1)
        return None
    else:
        return data


bsec_data = get_data(sensor)
while bsec_data == None:
	bsec_data = get_data(sensor)
print(bsec_data)
