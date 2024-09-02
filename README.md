# BME68X and BSEC2.5.0.2 for Python

Bosch Sensortec released BSEC2 v2.6.1.0 in July 2024, and bme68x-python-library provides a Python 3.x wrapper for the binary library available from BoschSensortec. 
BSEC2 2.6.1.0 provides two versions of the binary BSEC2, a smaller set of binaries supporting IAQ only and a larger set of binaries supporting full functionality which is the one we use here. 

PI3G originally created this library, however changes/updates to support  Bosch Sensortec BSEC2 updates have been a community effort.  Each annual release is typically a breaking release with config and status files from previous versions not loading (a version header is present). Also note that there are version requirements/dependencies across the BoschSensortec software set from Bosch Sensortec to support BSEC2 2.6.1.0 

* BME AI Studio v2.3.4
* BME Development Kit firmware v2.1.5 
* BME AI Studio Mobile App v2.4.16 

BSEC 2.4.0.0 introduced support for multiple sensors which this python wrapper does not yet support. BSEC2.6 has changes to cope with the effects of board temperature on Temp and Rh and is said to stabilise quicker.

The original PI3G repository is available [here] (https://github.com/pi3g/bme68x-python-library) which works with the BSEC 2.0.6.1 release.

### Pre-requisites

The BME688 uses SPI and/or I2C which will need to be enabled on the target PI and can be enabled using raspi-config and its "Interface Options" menu.  i2c-tools (apt install i2c-tools)is a useful utility to validate the I2C port your sensor is working on (i2cdetect -y 1). 

The Raspbian Bookworm Lite OS requires the python3 development package to be installed. (sudo apt install python3-dev)

### How to install the extension with BSEC
- clone [this repo](https://github.com/pi3g/bme68x-python-library) to a desired location on you hard drive
- download the licensed BSEC2 library [from BOSCH](https://www.bosch-sensortec.com/software-tools/software/bme688-software/)<br>
- unzip it into the *bme68x-python-library-bsec2.6.1.0* folder, next to this *README.md*
- open a new terminal window inside the *bme68x-python-library-bsec2.6.1.0* folder
Note: Only the bsec2-6-1-0_generic_release.zip (July 2024) is supported by this release.


As of BSEC 2.6.1.0 there is support for 64bit and two 32bit architectures.
To support multiple architectures, an environment variable is set to identify the PI architecture that you are building for.  If it is not set a 32bit ArmV6 build is carried out.

# This expects an environment variable to be set to select the BSEC2 library
# If it is not set a 32bit ArmV6 build is carried out.
# For 64 bit PI5
# BSEC2=64;export BSEC2; python setup.py install
# For 32 bit PI3 or above (Inc PI Zero 2)
# BSEC2=32; export BSEC2; python setup.py install
# For PI Zero and early Arm V6 PI's
# python setup.py install

1. For 32 bit PI3 or above (Inc PI Zero 2)
```bash
sudo BSEC2=32; export BSEC2; python setup.py install
```
or to install under venv use
```bash
BSEC2=32; export BSEC2; path/to/venv/bin/python3 setup.py install
```

2. For PI4 or PI5 running Raspbian 64 bit
# BSEC2=64;export BSEC2; python setup.py install

```bash
sudo BSEC2=64; export BSEC2; python setup.py install
```
or to install under venv use
```bash
BSEC2=64; export BSEC2; path/to/venv/bin/python3 setup.py install
```
3. For PI Zero and early Arm V6 PI's, no environment variable is set

```bash
sudo python3 setup.py install
```
or to install under venv use
```bash
path/to/venv/bin/python3 setup.py install
```
Be aware that from Raspbian Bookworm (Debian 12) you must use a virtual environment (venv).
Let's review how to create a virtual env called myvenv
````
$ python -m venv --system-site-packages </path/to/myvenv>
````
To invoke a virtual env
````
$ source </path/to/myvenv>/bin/activate
$(myenv) 
````

To exit a virtual env
````
$(myenv) deactivate
$
````
To remove a virtual environment, first deactivate, then delete it (rm -rf <path)


### How to use the extension
- to import in Python
```python
import bme68x
```
or
```python
from bme68x import BME68X
```
- see PythonDocumentation.md for reference
- to test the installation make sure you connected your BME68X sensor via I2C
- run the following code in a Python3 interpreter
```python
from bme68x import BME68X

# Replace I2C_ADDR with the I2C address of your sensor
# Either 0x76 (default for BME680) or 0x77 (default for BME688)
bme68x = BME68X(I2C_ADDR, 0)
bme68x.set_heatr_conf(1, 320, 100, 1)
data = bme68x.get_data()
```

The examples folder has been expanded to include burning in a sensor, using ultra low power mode, and saving and loading config and state data for a sensor. 
The tools folder has been changed to provide a sample AI Model and code to use a sensor to classify smells. Collecting data is best done with the 8 sensor BOSCH Sensortec DevKit


### A walk through of a 32bit PI4 installation follows.
```
$ sudu apt install i2c-tools
$ i2cdetect -y 1
0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- 77 
```
The BME688 module is showing up on port 0x77 which is the default for the example code.
If it fails to show up check connections and the module documentation. 

Install "Python3-dev" package (If you miss this step you may see a Python.h missing error)
```
$ sudo apt install python3-dev
```

As I am using Raspbian bookworm a virtual environment is required.
```
$ python -m venv --system-site-packages 68X
$ cd 68X
$ source bin/activate
<user>:~/68X $
```
Next clone this repo into the virtual environment 
```
(68X)<user>:~/68X $ ls -l
total 20
drwxr-xr-x  2 kpi kpi 4096 Jun 23 23:22 bin
drwxr-xr-x 11 kpi kpi 4096 Jun 23 23:32 bme68x-python-library-bsec2.5.0.0
drwxr-xr-x  3 kpi kpi 4096 Jun 23 23:22 include
drwxr-xr-x  3 kpi kpi 4096 Jun 23 23:22 lib
-rw-r--r--  1 kpi kpi  173 Jun 23 23:22 pyvenv.cfg
```

Now copy the BoschSensortech BSEC 2.5 (bsec_v2-5-0-2) into the bmx68x repo clone. 
It should look like this.

```
(68X)<user>:~/68X $ cd bme68x-python-library-bsec2.5.0.0/
(68X) kpi@pi-3:~/68X/bme68x-python-library-bsec2.5.0.0 $ ls -l
total 176
-rw-r--r-- 1 kpi kpi  2863 Jun 23 23:32 bme68xConstants.py
drwxr-xr-x 2 kpi kpi  4096 Jun 23 23:32 bme68x.egg-info
-rw-r--r-- 1 kpi kpi 76995 Jun 23 23:32 bme68xmodule.c
-rw-r--r-- 1 kpi kpi   378 Jun 23 23:32 bme68x-python-library-bsec2.5.0.0.iml
drwxr-xr-x 3 kpi kpi  4096 Jun 23 23:32 BME68x-Sensor-API
-rw-r--r-- 1 kpi kpi   571 Jun 23 23:32 bsecConstants.py
drwxr-xr-x 6 kpi kpi  4096 Jun 23 23:32 bsec_v2-5-0-2
drwxr-xr-x 7 kpi kpi  4096 Jun 23 23:32 build
drwxr-xr-x 2 kpi kpi  4096 Jun 23 23:32 dist
-rw-r--r-- 1 kpi kpi 12843 Jun 23 23:32 Documentation.md
drwxr-xr-x 3 kpi kpi  4096 Jun 23 23:32 examples
-rw-r--r-- 1 kpi kpi 17522 Jun 23 23:32 internal_functions.c
-rw-r--r-- 1 kpi kpi  2518 Jun 23 23:32 internal_functions.h
-rw-r--r-- 1 kpi kpi  1065 Jun 23 23:32 LICENSE
-rw-r--r-- 1 kpi kpi  4279 Jun 23 23:32 README.md
-rw-r--r-- 1 kpi kpi  2296 Jun 23 23:32 setup.copy
-rw-r--r-- 1 kpi kpi  3242 Jun 23 23:32 setup.py
drwxr-xr-x 3 kpi kpi  4096 Jun 23 23:32 tools

```
From here run the installer with the 32bit env set for my Pi 4 board and 32 bit raspbian.

```
(68X) <user>:~/68X/bme68x-python-library-bsec2.5.0.0 $ BSEC2=32; export BSEC2; python3 setup.py install
```

There are a bunch of warnings about unused variables, and it should complete with the last few lines looking like this:
```
Installed /home/kpi/68X/lib/python3.11/site-packages/bme68x-1.4.0-py3.11-linux-aarch64.egg
Processing dependencies for bme68x==1.4.0
Finished processing dependencies for bme68x==1.4.0
(68X) <user>:~/68X/bme68x-python-library-bsec2.5.0.0 $

```

Change to the examples directory and run the forced mode example:
```
(68X) <user>:~/68X/bme68x-python-library-bsec2.5.0.0 $ cd examples/
(68X) <user>:~/68X/bme68x-python-library-bsec2.5.0.0/examples $ ls
airquality.py  conf            force_ulp.py      parallel_mode_ulp.py  pm25.py       README.md
burn_in.py     forced_mode.py  parallel_mode.py  pm25-nolog.py         read_conf.py
(68X) <user>:~/68X/bme68x-python-library-bsec2.5.0.0/examples $ python3 forced_mode.py 
TESTING FORCED MODE WITHOUT BSEC
INITIALIZED BME68X
VARIANT BME688
INITIALIZED BSEC
BSEC VERSION: 2.5.0.2
SET HEATER CONFIG (FORCED MODE)
{'sample_nr': 1, 'timestamp': 1807319, 'raw_temperature': 33.44466018676758, 'raw_pressure': 699.2025146484375, 'raw_humidity': 100.0, 'raw_gas': 61.77606201171875, 'status': 160}

TESTING FORCED MODE WITH BSEC
INITIALIZED BME68X
VARIANT BME688
INITIALIZED BSEC
BSEC VERSION: 2.5.0.2
SET BME68X CONFIG
SET HEATER CONFIG (FORCED MODE)
SET BME68X CONFIG
SET HEATER CONFIG (FORCED MODE)
{'sample_nr': 1, 'timestamp': 36173116135177, 'iaq': 50.0, 'iaq_accuracy': 0, 'static_iaq': 50.0, 'static_iaq_accuracy': 0, 'co2_equivalent': 500.0, 'co2_accuracy': 0, 'breath_voc_equivalent': 0.49999991059303284, 'breath_voc_accuracy': 0, 'raw_temperature': 29.216562271118164, 'raw_pressure': 101652.2578125, 'raw_humidity': 48.701637268066406, 'raw_gas': 5684.84619140625, 'stabilization_status': 0, 'run_in_status': 0, 'temperature': 24.216562271118164, 'humidity': 65.35968017578125, 'gas_percentage': 0.0, 'gas_percentage_accuracy': 0}
```

As the status and accuracy are all zero it is time to burn in this sensor for 24 hours. 