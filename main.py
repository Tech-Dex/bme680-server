import datetime
import logging
import time

import bme680
from bme680 import constants as bme680_constants
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "bucket"
org = "org"
token = "token"
url = "http://influxdb:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

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

datetime_format = "%Y-%m-%d,%H:%M:%S"
temperature_precision = "{:.2f}"
pressure_precision = "{:.2f}"
humidity_precision = "{:.3f}"

try:
    while True:
        if sensor.get_sensor_data():
            point = (
                Point("environment_data")
                .tag("location", "your_location")
                .field("temperature", sensor.data.temperature)
                .field("pressure", sensor.data.pressure)
                .field("humidity", sensor.data.humidity)
                .field("gas_resistance", sensor.data.gas_resistance)
                .time(datetime.datetime.now(datetime.UTC), WritePrecision.NS)
            )
            write_api.write(bucket=bucket, org=org, record=point)

        time.sleep(5)
except KeyboardInterrupt:
    pass
