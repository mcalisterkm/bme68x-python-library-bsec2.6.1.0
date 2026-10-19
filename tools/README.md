Tools
======

I bmerawdata
---------------

With the BME688 Devkit no longer available, it is increasingly difficult to record data and generate an AI-Model, unless you already have a Devkit. Worse the BME690 Devkit does not record data that can be used to generate a model for the BME688. 

So we have in October 2026 revisited bmerawdata.py and updated it to work with BSEC2 2.6.0.1 and AI Studio v 3.2.1.
The fact remains that a single sensor module is a slow data recorder, however it works and if you have more than one module they can be used too. Modules usually have 0x76 and 0x77 address options, and with multiple I2C buses on a PI you can host quite a few. 
