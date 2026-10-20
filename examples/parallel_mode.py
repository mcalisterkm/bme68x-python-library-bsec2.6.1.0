# This example tests and demonstrates the BME68X_PARALLEL_MODE
# Without use of BSEC and
# With use of BSEC

from bme68x import BME68X
import bme68xConstants as cnst
import bsecConstants as bsec
from time import sleep

i = 0
temp_prof = [320, 100, 100, 100, 200, 200, 200, 320, 320, 320]
# Durations in parallel mode are units of 140ms
dur_prof = [5, 2, 10, 30, 5, 5, 5, 5, 5, 5]

print('PARALLEL MODE W/O BSEC')
sensor = BME68X(cnst.BME68X_I2C_ADDR_LOW, 0)
print("Initialised ", sensor.get_chip_id(), sensor.get_variant())
print(sensor.set_heatr_conf(cnst.BME68X_ENABLE,
      temp_prof, dur_prof, cnst.BME68X_PARALLEL_MODE))
sleep(2)
# get_data returns a list of dictionaries, one for each profile step (gas_index 0-9)
# that completed since the last call. The list is often empty, so poll a fixed
# number of times (about 3 full profile cycles of ~10.8 s each).
ITERATIONS = 50
for _ in range(ITERATIONS):
    for data in sensor.get_data():
        step = "Step: " + "{: ^2d}".format(data['gas_index'])
        sample = "SampleNo: " + "{: ^2d}".format(data['sample_nr'])
        temp = "Temperature: " + "{: ^4.1f}".format(data['raw_temperature']) + " \u00B0"+ "C"
        hum = "Humidity: " +  "{: ^4.1f}".format(data['raw_humidity']) + "%"
        pres = "Pressure: " + "{: ^4.1f}".format(data['raw_pressure'])
        gas = "Gas: " + "{: ^4.1f}".format(data['raw_gas']) + " kOhm"
        print(step, sample, temp, hum, pres, gas)
    sleep(0.2)

print('\n\nPARALLEL MODE WITH BSEC')
sensor = BME68X(cnst.BME68X_I2C_ADDR_LOW, 0)
print(sensor.set_heatr_conf(cnst.BME68X_ENABLE, temp_prof, dur_prof, cnst.BME68X_PARALLEL_MODE))
print(sensor.set_sample_rate(bsec.BSEC_SAMPLE_RATE_LP))

def get_data(sensor):
    data = {}
    try:
        data = sensor.get_bsec_data()
    except Exception as e:
        print(e)
        sleep(0.1)
        return None
    if data == {} or data == None:
        sleep(0.1)
        return None
    else:
        return data


while i < 5 :
    bsec_data = get_data(sensor)
    while bsec_data == None:
        bsec_data = get_data(sensor)
    print(bsec_data)
    i +=  1
