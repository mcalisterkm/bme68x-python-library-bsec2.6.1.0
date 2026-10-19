#  Bmerawdata

This tool allows you to record and save data with your [BME688 Breakout Board](https://buyzero.de/products/luftqualitatssensor-bosch-bme688-breakout-board?_pos=2&_sid=985505100&_ss=r), so that it can be imported by [Boschs AI Studio](https://www.bosch-sensortec.com/software-tools/software/bme688-software/).
To use the smell detection feature of the BME688 you need to train an algorithm in AI Studio.
The algorithm requires lots of training and testing data, which you can record using this tool.

There is more on training a model using AI Studio and the BME 688 Devkit [here:](https://github.com/mcalisterkm/teach-your-pi-to-sniff-with-bme688) and [here:](https://picockpit.com/raspberry-pi/teach-bme688-how-to-smell/) for detailed instructions.

## How to use the script

- Make sure your sensor is connected and working properly (check out the forced_mode.py  example in the examples folder to confirm, and the i2cdetect -y 1 command to validate the I2C id)
- The command is Python3 bmerawdata.py <board config> and here is an example.

(venv prompt)<user>$ python3 bmerawdata.py sample/BoardConfigurationRDC1-1HP-354.bmeconfig
prompt 

There are a selection of board config files in the samples folder, and you can create your own on AI Studio. 

To stop recording type Ctl-C, and the application will close the file and provide its name. 

## AI Studio

- Open a new project in AI Studio (we tested with AI Studio Desktop v3.2.1) 
- (Optional) If you want to use your own configuration
  - Press Configure BME Board and save the Configuration file
  - Copy the newly created **.bmeconfig** file into the bmerawdata folder
- Execute `python bmerawdata.py <your-config>.bmeconfig` to start recording data (the sample configs are in the sample folder)
- Press **Ctrl+C** to terminate the script
- The captured data will be saved as a **.bmerawdata** file that starts with the timestamp of creation
- Import that **.bmerawdata** file into AI Studio and label your specimen (You can record multiple specimens in one session, but you have to manually label them in AI Studio)

Notes
- BME AI Studio supports the official devkits, so the data output looks like an 8 sensor devkit with only the first sensor working. 
- The script uses the heater profile and duty cycle of sensor 0 in the config. Use the same config, with one heater profile and one duty cycle, for every recording in a session; the model generator only combines data recorded with the same profile, so this keeps it simple.
- The BME688 breakout is a single sensor, but the config describes an 8 sensor board, so AI Studio will show only sensor 0 with data.
- Heater step durations are converted from the config's `timeBase` to the 140 ms units of parallel mode. The sensor cannot run a step longer than 255 units (35.7 s), so the HP-001 burn in profile is rejected. Use examples/burn_in.py for burn in.
- During the sleeping cycles of a duty cycle the heater is switched off and the scan then restarts at step 0.
