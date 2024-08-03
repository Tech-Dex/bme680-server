import datetime
import logging
import os
import time

import bme680
from bme680 import constants as bme680_constants
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_URL = f"{os.getenv('INFLUXDB_PROTOCOL')}://{os.getenv('INFLUXDB_HOST')}:{os.getenv('INFLUXDB_PORT')}"

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
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
sensor.set_temp_offset(int(os.getenv("BME680_SENSOR_TEMP_OFFSET")))
sensor.set_filter(bme680_constants.FILTER_SIZE_3)
sensor.set_gas_status(bme680_constants.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(int(os.getenv("BME680_SENSOR_GAS_HEATER_TEMP")))
sensor.set_gas_heater_duration(int(os.getenv("BME680_SENSOR_GAS_HEATER_DURATION")))
sensor.select_gas_heater_profile(int(os.getenv("BME680_SENSOR_GAS_HEATER_PROFILE")))

HUMIDITY_BASELINE = float(os.getenv("BME680_SENSOR_HUMIDITY_BASELINE"))
HUMIDITY_WEIGHTING = float(os.getenv("BME680_SENSOR_HUMIDITY_WEIGHTING"))
BURN_IN_TIME = int(os.getenv("BME680_SENSOR_BURN_IN_TIME"))

START_TIME = time.time()
NOW = time.time()
BURN_IN_DATA = []

while NOW - START_TIME < BURN_IN_TIME:
    NOW = time.time()
    if sensor.get_sensor_data() and sensor.data.heat_stable:
        BURN_IN_DATA.append(sensor.data.gas_resistance)
        time.sleep(1)

GAS_BASELINE = sum(BURN_IN_DATA[-50:]) / 50.0


def calculate_iaq(
    humidity, gas_resistance, gas_baseline, humidity_baseline, humidity_weighting
):
    gas_offset = gas_baseline - gas_resistance
    hum_offset = humidity - humidity_baseline

    if hum_offset > 0:
        hum_score = (
            (100 - humidity_baseline - hum_offset)
            / (100 - humidity_baseline)
            * (humidity_weighting * 100)
        )
    else:
        hum_score = (
            (humidity_baseline + hum_offset)
            / humidity_baseline
            * (humidity_weighting * 100)
        )

    if gas_offset > 0:
        gas_score = (gas_resistance / gas_baseline) * (100 - (humidity_weighting * 100))
    else:
        gas_score = 100 - (humidity_weighting * 100)

    air_quality_score = hum_score + gas_score

    return air_quality_score


try:
    while True:
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            point = (
                Point("environment_data")
                .tag("location", "your_location")
                .field("temperature", sensor.data.temperature)
                .field("pressure", sensor.data.pressure)
                .field("humidity", sensor.data.humidity)
                .field("gas_resistance", sensor.data.gas_resistance)
                .field(
                    "iaq",
                    calculate_iaq(
                        sensor.data.humidity,
                        sensor.data.gas_resistance,
                        GAS_BASELINE,
                        HUMIDITY_BASELINE,
                        HUMIDITY_WEIGHTING,
                    ),
                )
                .time(datetime.datetime.now(datetime.UTC), WritePrecision.NS)
            )
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        time.sleep(1)
except KeyboardInterrupt:
    pass
