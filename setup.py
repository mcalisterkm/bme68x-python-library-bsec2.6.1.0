from setuptools import setup, Extension, find_packages
from pathlib import Path
import os

# This expects an environment variable to be set to select the BSEC2 library
# If it is not set a 32bit ArmV6 build is carried out. 
# For 64 bit PI4 or PI5  
# BSEC2=64;export BSEC2; python setup.py install
# For 32 bit PI3 or above (Inc PI Zero 2)
# BSEC2=32; export BSEC2; python setup.py install
# For PI Zero and early Arm V6 PI's
# python setup.py install

BSEC2=os.environ.get("BSEC2", None)
# Three PI Architectures are supported by BSEC2.6: PiThree_ArmV6 32 bit,  PiThree_ArmV8 32 bit,  PiFour_ArmV8 64 bit (also works for PI5) 

if BSEC2 == '64':
	algo = 'bsec2-6-1-0_generic_release/algo/bsec_IAQ_Sel/bin/RaspberryPi/PiFour_Armv8'
	# 64 bit Raspbian OS - PI 4 and PI5, ARM V8A, ARM V8.2-A  Must be 64 bit OS

elif BSEC2 == '32':
	algo = 'bsec2-6-1-0_generic_release/algo/bsec_IAQ_Sel/bin/RaspberryPi/PiThree_ArmV8'
	# 32bit Raspbian OS - PI 5 / 4 / 3 /  Zero 2, ARM V8A  Must be 32bit  OS

else:
	algo = 'bsec2-6-1-0_generic_release/algo/bsec_IAQ_Sel/bin/RaspberryPi/PiThree_ArmV6'
	# 32bit Raspbian OS - Pi Zero, Arm V6 Must be 32 bit OS

BSEC = True

if BSEC:
    ext_comp_args = ['-D BSEC ' '-fPIC ']
    libs = ['pthread', 'm', 'rt', 'algobsec']
    lib_dirs = ['/usr/local/lib',
                algo ]
else:
    ext_comp_args = []
    libs = ['pthread', 'm', 'rt']
    lib_dirs = ['/usr/local/lib']

LIBDIR = Path(__file__).parent

README = (LIBDIR / "README.md").read_text()

bme68x = Extension('bme68x',
                   extra_compile_args=ext_comp_args,
                   include_dirs=['/usr/local/include'],
                   libraries=libs,
                   library_dirs=lib_dirs,
                   depends=['BME68x-Sensor-API/bme68x.h', 'BME68x-Sensor-API/bme68x.c',
                            'BME68x-Sensor-API/bme68x_defs.h', 'internal_functions.h', 'internal_functions.c'],
                   sources=['bme68xmodule.c', 'BME68x-Sensor-API/bme68x.c', 'internal_functions.c'])

setup(name='bme68x',
      version='2.6.1',
      description='Python interface for BME68X sensor and BSEC',
      long_description=README,
      long_description_content_type='text/markdown',
      url='https://github.com/pi3g/bme68x-python-library',
      author='Nathan',
      author_email='nathan@pi3g.com',
      license='MIT',
      classifiers=[
           'Development Status :: 4 - Alpha§',
           'Intended Audience :: Developers',
           'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Scientific/Engineering :: Atmospheric Science',
      ],
      keywords='bme68x bme680 bme688 BME68X BME680 BME688 bsec BSEC sensor environment temperature pressure humidity air pollution',
      packages=find_packages(),
      py_modules=['bme68xConstants', 'bsecConstants'],
      package_data={
          'bme68x': [
               'bsec2-6-1-0_generic_release/algo/bsec_IAQ_Sel/config/bme688/bme688_sel_33v_3s_4d/bsec_selectivity.config', 
          ]
      },
      headers=['BME68x-Sensor-API/bme68x.h',
               'BME68x-Sensor-API/bme68x_defs.h', 'internal_functions.h'],
      ext_modules=[bme68x])
