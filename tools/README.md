Tools
=====


bmerawdata
---------------

With the BME688 Devkit no longer available, it became increasingly difficult to record data and generate an AI-Model, unless you already have a Devkit. Also the BME690 Devkit does not record data that can be used to generate a model for the BME688.

So in October 2026 we revisited bmerawdata.py and updated it to work with BSEC2 2.6.0.1 and AI Studio v 3.2.1. The fact remains that a single sensor module is a slow data recorder (one to two hours recording is usually sufficient with one sensor), however it works reliably and if you have more than one module they can be used too. Modules usually have 0x76 and 0x77 address options, and with multiple I2C buses on a PI you can host quite a few (run a script for each sensor).

We have tested recording for several hours, and generated AI Models from data entierly recorded by a single sensor.  The Ar-Coffe model which is  included as a zip file contains the Ai Studio project and data (should you want to see it). The ai-model export is also provided along with a python script to run it. 