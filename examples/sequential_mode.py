# This example tests and demonstrates the BME68X_SEQUENTIAL_MODE
# Without use of BSEC and With use of BSEC
# SEQUENTIAL mode  runs the Temp, Humidity, and Pressure readings before warming the hot plate for gas reading
# As a result these reading may be less affected by the hot plate temperature but that also depends on duty cycle (sleep cycles).
# Note that in SEQUENTIAL mode the heater profile durations are in milliseconds not multiplier units as in PARALLEL mode 

from bme68x import BME68X
import bme68xConstants as cnst
import bsecConstants as bsec
from time import sleep

# It seems that the multiplier profile is not use here and durations are in milliseconds for the API in sequential mode
temp_prof = [320, 100, 100, 100, 200, 200, 200, 320, 320, 320]
dur_prof = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

print('SEQUENTIAL MODE W/O BSEC')
sensor = BME68X(cnst.BME68X_I2C_ADDR_HIGH, 0)
# set_conf params hum, pressi, temp, filter, odr.
print(sensor.set_conf(cnst.BME68X_OS_2X, cnst.BME68X_OS_16X,
      cnst.BME68X_OS_1X, cnst.BME68X_FILTER_SIZE_1,
      cnst.BME68X_ODR_NONE    ))
# Set the heater configuration
print(sensor.set_heatr_conf(cnst.BME68X_ENABLE,
      temp_prof, dur_prof, cnst.BME68X_SEQUENTIAL_MODE))
# Iterate round a few times to get data from the API
# With 10 profiles, need enough iterations to cycle through all of them
for iteration in range(15):
    # First call to get_data() triggers the measurement cycle
    sleep(1)
    #print(f"\n--- Iteration {iteration + 1} ---", flush=True)
    #print("About to call get_data()...", flush=True)
    try:
        res = sensor.get_data()
        #print(f"get_data() returned {len(res) if res else 0} fields", flush=True)
    except Exception as e:
        print(f"ERROR in get_data(): {e}")
        import traceback
        traceback.print_exc()
        break
    # get_data returns a list of dictionaries, one for each temp/dur profile step: 0-9 
    # so below data gets a dictionary in each iteration, which we unpack to get the values
    sleep(1)
    if res is None or len(res) == 0:
        print("Warning: No data received from sensor.get_data()")
    else:
        for data in res:
            # Skip None entries that can occur in sequential mode
            if data is None:
                continue
            # print("Line", data)
            sample = "SampleNo: " + "{: ^2d}".format(data['sample_nr'])
            gas_idx = "GasIdx: " + "{: ^2d}".format(data['gas_index'])
            meas_idx = "MeasIdx: " + "{: ^2d}".format(data['meas_index'])
            temp = "Temperature: " + "{: ^4.1f}".format(data['raw_temperature']) + " \u00B0"+ "C"
            hum = "Humidity: " +  "{: ^4.1f}".format(data['raw_humidity']) + "%"
            pres = "Pressure: " + "{: ^4.1f}".format(data['raw_pressure'] )  
            gas = "Gas: " + "{: ^4.1f}".format(data['raw_gas'] * 1000)  
            print(sample, gas_idx, meas_idx, temp, hum, pres, gas)

print('\n\nSEQUENTIAL MODE WITH BSEC')
temp_prof = [320, 100, 100, 100, 200, 200, 200, 320, 320, 320]
dur_prof = [5, 2, 10, 30, 5, 5, 5, 5, 5, 5]
sensor = BME68X(cnst.BME68X_I2C_ADDR_HIGH, 0)
#sensor.set_sample_rate(bsec.BSEC_SAMPLE_RATE_HIGH_PERFORMANCE)
print(sensor.set_heatr_conf(cnst.BME68X_ENABLE,
      temp_prof, dur_prof, cnst.BME68X_SEQUENTIAL_MODE))
sensor.set_sample_rate(bsec.BSEC_SAMPLE_RATE_LP)

def get_data(sensor):
    data = None
    try:
        data = sensor.get_bsec_data()
    except Exception as e:
        print(e)
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
 