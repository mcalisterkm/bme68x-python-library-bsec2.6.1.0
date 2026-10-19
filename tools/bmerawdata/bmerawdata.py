import sys
import os
from bme68x import BME68X
import bme68xConstants as BME68XCONST
import bsecConstants as BSECCONST
import json
from time import time, sleep
from datetime import datetime, timezone
import random
import string

# Column layout and header fields as written by the BME688 dev kit (AI-Studio 3.x)
FIRMWARE_VERSION = '2.1.5'
DEFAULT_LABEL_TAG = 1001

# Parallel mode limits of the BME68X
PARALLEL_UNIT_MS = 140
MAX_STEP_UNITS = 255
MAX_PROFILE_STEPS = 10
MAX_TEMP_C = 400
_COLS = [
    ('Sensor Index', '', 'integer', 'sensor_index'),
    ('Sensor ID', '', 'integer', 'sensor_id'),
    ('Time Since PowerOn', 'Milliseconds', 'integer', 'timestamp_since_poweron'),
    ('Real time clock', 'Unix Timestamp: seconds since Jan 01 1970. (UTC); 0 = missing', 'integer', 'real_time_clock'),
    ('Temperature', 'DegreesCelcius', 'float', 'temperature'),
    ('Pressure', 'Hectopascals', 'float', 'pressure'),
    ('Relative Humidity', 'Percent', 'float', 'relative_humidity'),
    ('Resistance Gassensor', 'Ohms', 'float', 'resistance_gassensor'),
    ('Heater Profile Step Index', '', 'integer', 'heater_profile_step_index'),
    ('Scanning Mode Enabled', '', 'boolean', 'scanning_enabled'),
    ('Scanning Cycle Index', '', 'integer', 'scanning_cycle_index'),
    ('Label Tag', '', 'integer', 'label_tag'),
    ('Error Code', '', 'integer', 'error_code'),
]
DATA_COLUMNS = [{'name': n, 'unit': u, 'format': f, 'key': k, 'colId': i}
                for i, (n, u, f, k) in enumerate(_COLS, 1)]


class BME68X_AI(BME68X):
    index: int = 0
    ai_conf: dict = {}
    ai_data: dict = {}
    heatr_profile: dict = {}
    duty_cycle: dict = {}
    label_tag: int = 0
    sensor_id = 0
    last_step = None

    def __init__(self, i2c_addr: int, ai_conf: str, index=0):
        super(BME68X_AI, self).__init__(i2c_addr, 0)
        self.index = index
        self.set_ai_conf(ai_conf)
        seed = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        self.ai_data = {
            'rawDataHeader': {
                'counterPowerOnOff': 1, 'seedPowerOnOff': seed, 'counterFileLimit': 1,
                'dateCreated': '', 'dateCreated_ISO': '', 'firmwareVersion': FIRMWARE_VERSION,
                'boardId': ''},
            'rawDataBody': {'dataColumns': DATA_COLUMNS}}
        self.label_tag = DEFAULT_LABEL_TAG
        self.sensor_id = self.get_sensor_id()

    def set_ai_conf(self, ai_conf: str):
        with open(ai_conf, 'r') as conf_file:
            self.ai_conf = json.load(conf_file)
        conf_body = self.ai_conf['configBody']

        # Heater profile and duty cycle both come from this sensor's entry
        sensor_conf = next((sc for sc in conf_body['sensorConfigurations']
                            if sc['sensorIndex'] == self.index), None)
        if sensor_conf is None:
            raise ValueError(f'{ai_conf} has no configuration for sensor index {self.index}')
        self.heatr_profile = next(hp for hp in conf_body['heaterProfiles']
                                  if hp['id'] == sensor_conf['heaterProfile'])
        self.duty_cycle = next(dc for dc in conf_body['dutyCycleProfiles']
                               if dc['id'] == sensor_conf['dutyCycleProfile'])

        temp_prof, dur_prof = self._profile_to_sensor_units(self.heatr_profile)

        # oversampling defaults to 0 (skipped), which leaves T/P/H as constants
        # args: humidity, pressure, temperature (Bosch API example values)
        self.set_conf(BME68XCONST.BME68X_OS_16X, BME68XCONST.BME68X_OS_1X, BME68XCONST.BME68X_OS_2X,
                      BME68XCONST.BME68X_FILTER_OFF, BME68XCONST.BME68X_ODR_NONE)
        self.temp_prof = temp_prof
        self.dur_prof = dur_prof
        self._start_heater()

    @staticmethod
    def _profile_to_sensor_units(profile):
        """Convert an AI Studio heater profile (durations in timeBase ms) into the
        140 ms units that parallel mode needs, rejecting profiles the sensor cannot run."""
        vectors = profile['temperatureTimeVectors']
        time_base = profile['timeBase']
        if not 1 <= len(vectors) <= MAX_PROFILE_STEPS:
            raise ValueError(f"{profile['id']}: needs 1 to {MAX_PROFILE_STEPS} steps, has {len(vectors)}")
        temp_prof, dur_prof = [], []
        for temp, dur in vectors:
            ms = dur * time_base
            units = ms / PARALLEL_UNIT_MS
            if units != int(units) or int(units) < 1:
                raise ValueError(f"{profile['id']}: step of {ms} ms is not a multiple of {PARALLEL_UNIT_MS} ms")
            if units > MAX_STEP_UNITS:
                raise ValueError(
                    f"{profile['id']}: step of {ms / 1000:.1f} s is longer than the sensor's "
                    f"maximum of {MAX_STEP_UNITS * PARALLEL_UNIT_MS / 1000:.1f} s. "
                    "Use examples/burn_in.py for the burn-in profile (HP-001)")
            if not 0 < temp <= MAX_TEMP_C:
                raise ValueError(f"{profile['id']}: temperature {temp} is outside 1 to {MAX_TEMP_C} degC")
            temp_prof.append(temp)
            dur_prof.append(int(units))
        return temp_prof, dur_prof

    def _start_heater(self):
        self.set_heatr_conf(BME68XCONST.BME68X_ENABLE, self.temp_prof,
                            self.dur_prof, BME68XCONST.BME68X_PARALLEL_MODE)

    def get_heatr_profile_dur(self):
        """Length of one scan cycle in seconds"""
        return sum(self.dur_prof) * PARALLEL_UNIT_MS / 1000

    def increase_label_tag(self):
        self.label_tag += 1

    def _open_output(self):
        """Create the output file and write everything up to the start of dataBlock."""
        now = datetime.now(timezone.utc)
        hdr = self.ai_data['rawDataHeader']
        hdr['dateCreated'] = str(int(now.timestamp()))
        hdr['dateCreated_ISO'] = now.isoformat(timespec='seconds')
        hdr['boardId'] = f'{self.sensor_id:012X}'
        file_date = now.strftime('%Y_%m_%d_%H_%M')

        def name():
            return (f"{file_date}_Board_{hdr['boardId']}_PowerOnOff_{hdr['counterPowerOnOff']}"
                    f"_File_{hdr['counterFileLimit']}.bmerawdata")
        # the name has no unique seed, so avoid overwriting a file from the same minute
        while os.path.exists(name()):
            hdr['counterPowerOnOff'] += 1
        self.file_name = name()

        body = {**self.ai_data['rawDataBody'], 'dataBlock': []}
        text = json.dumps({**self.ai_conf, 'rawDataHeader': hdr, 'rawDataBody': body}, indent=3)
        # split at the empty dataBlock so rows can be streamed into it
        idx = text.rfind('[]')
        self.tail = text[idx + 1:]
        self.out = open(self.file_name, 'w')
        self.out.write(text[:idx + 1])
        self.rows_written = 0

    def _write_row(self, row):
        self.out.write(('\n' if self.rows_written == 0 else ',\n') + '         ' + json.dumps(row))
        self.rows_written += 1

    def _close_output(self):
        self.out.write('\n      ' + self.tail + '\n')
        self.out.close()

    def _write_step(self, hp_step, cycle):
        self._write_row([
            self.index,                     # sensor index
            self.sensor_id,                 # sensor id
            hp_step['timestamp'],           # ms since power on
            int(round(time())),             # unix time
            hp_step['raw_temperature'],     # degC
            hp_step['raw_pressure'],        # hPa
            hp_step['raw_humidity'],        # %rH
            hp_step['raw_gas'] * 1000,      # ohm
            hp_step['gas_index'],           # heater step index
            1,                              # scanning enabled
            cycle,                          # scanning cycle index
            self.label_tag,                 # label tag
            0,                              # error code
        ])

    def _sleep_cycles(self):
        """Rest the sensor (heater off) for the duty cycle's sleeping cycles, then restart
        the heater profile so the next scan starts again at step 0"""
        self.sleep_mode()
        sleep(self.duty_cycle['numberSleepingCycles'] * self.get_heatr_profile_dur())
        self._start_heater()

    def record_data(self):
        self._open_output()
        n_steps = len(self.dur_prof)
        n_scans = self.duty_cycle['numberScanningCycles']
        n_sleeps = self.duty_cycle['numberSleepingCycles']
        cycle = 1
        print(f'Recording to {self.file_name}; press Ctrl+C to stop')
        try:
            while True:
                raw_data = self.get_data()
                if not raw_data:
                    sleep(0.1)
                    continue
                for hp_step in raw_data:
                    # A scan cycle must begin at step 0, so drop anything left over
                    if cycle_start_pending(hp_step, self.last_step):
                        if self.last_step is not None:
                            print(f"Missed step after {self.last_step}, restarting scan cycle {cycle}")
                            self.last_step = None
                        continue
                    self._write_step(hp_step, cycle)
                    self.last_step = hp_step['gas_index']
                    if hp_step['gas_index'] == n_steps - 1:
                        self.last_step = None
                        cycle += 1
                        if cycle > n_scans:
                            cycle = 1
                            if n_sleeps:
                                self._sleep_cycles()
                                break
                self.out.flush()
        except KeyboardInterrupt:
            pass
        finally:
            self._close_output()
            print(f"\nSAVED DATA AS\n{self.file_name} ({self.rows_written} rows)")


def cycle_start_pending(hp_step, last_step):
    """True if this step cannot be part of the scan cycle being recorded"""
    if last_step is None:
        return hp_step['gas_index'] != 0
    return hp_step['gas_index'] != last_step + 1


if __name__ == '__main__':
    ai_conf = sys.argv[1] if len(sys.argv) > 1 else '1-7-1-BoardConfiguration.bmeconfig'
    bme68x_ai = BME68X_AI(BME68XCONST.BME68X_I2C_ADDR_LOW, ai_conf)

    print("BSEC VERSION (FROM PYTHON)")
    print(bme68x_ai.get_bsec_version())

    print(bme68x_ai.get_sensor_id())

    bme68x_ai.record_data()
