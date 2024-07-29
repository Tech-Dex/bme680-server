import datetime
import logging
import time

import bme680
from bme680 import constants as bme680_constants

try:
    sensor = bme680.BME680(bme680_constants.I2C_ADDR_PRIMARY)
except Exception as e:
    if not (isinstance(e, IOError) or isinstance(e, RuntimeError)):
        logging.error(f"Unexpected error: {e}")
        raise e
    sensor = bme680.BME680(bme680_constants.I2C_ADDR_SECONDARY)

sensor.set_humidity_oversample(bme680_constants.OS_2X)
sensor.set_pressure_oversample(bme680_constants.OS_4X)
sensor.set_temperature_oversample(bme680_constants.OS_8X)
sensor.set_temp_offset(-4)
sensor.set_filter(bme680_constants.FILTER_SIZE_3)
sensor.set_gas_status(bme680_constants.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

datetime_format = '%Y-%m-%d,%H:%M:%S'
temperature_precision = "{:.2f}"
pressure_precision = "{:.2f}"
humidity_precision = "{:.3f}"

try:
    while True:
        if sensor.get_sensor_data():
            output = (f"{datetime.datetime.now(datetime.UTC).strftime(datetime_format)}: "
                      f"Temperature: {temperature_precision.format(sensor.data.temperature)} °C, "
                      f"Pressure: {pressure_precision.format(sensor.data.pressure)} hPa, "
                      f"Humidity: {humidity_precision.format(sensor.data.humidity)} %, "
                      f"Gas: {sensor.data.gas_resistance} Ohms")

            print(output)
        time.sleep(1)
except KeyboardInterrupt:
    pass

#TODO : Add InfluxDB in docker-compose, Insert in InfluxDB.
