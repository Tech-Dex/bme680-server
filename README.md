# BME680 InfluxDB and Grafana Setup

This repository contains the code and configuration necessary to set up a system that reads data from a BME680 sensor, stores it in an InfluxDB database, and visualizes it with Grafana. The setup uses Docker Compose to manage the services.

## Prerequisites

- Docker
- Docker Compose
- A BME680 sensor
- A Raspberry Pi/Arduino/ESP8266/ESP32 or any other microcontroller that can read data from the BME680 sensor

## Getting Started

### 1. Clone the repository

```sh
git clone https://github.com/yourusername/bme680-influxdb-grafana.git
cd bme680-influxdb-grafana
```

### 2. Create a .env file & configure the environment variables

```sh
cp docker-compose.env .env
```

### 3. Build and run the containers
```sh
source .env
docker compose up -d
```
This will start three services:

- server: The service that reads data from the BME680 sensor and writes it to InfluxDB.
- influxdb: The InfluxDB database.
- grafana: The Grafana service for visualizing the data.
- telegraf: The Telegraf service for collecting system metrics. Custom exec for rpi temp (Optional)

### 4. Configure Grafana
Once the containers are running, you can access Grafana at http://localhost:3000. Follow these steps to configure it:

1. Log in: Default username and password are admin.
2. Add InfluxDB data source:
   - Navigate to Configuration > Data Sources.
   - Click Add data source and select InfluxDB.
   - Set the URL to http://influxdb:8086.
   - Enter the organization, bucket, and token from your .env file.
   - Save & test the data source.
3. Create a dashboard:
   - Import json file from the `grafana` directory.
   - Or create a new dashboard and add panels to visualize the data from the BME680 sensor.


### 5. Volume Mounts Permissions
If you encounter permission issues with the volume mounts, you can change the permissions of the `data` directory:

```sh
sudo chown -R 472:472 data

# example on my case
cd /var/lib/docker/volumes
sudo chown -R 472:472 bme680-server_grafana-data/
sudo chown -R 472:472 bme680-server_influxdb-data/
```


##### Notes:

- The dashboard for metrics is a modified smaller version of the [Telegraf: system dashboard](https://grafana.com/grafana/dashboards/928-telegraf-system-dashboard/)
- Why use env_file in telegraf? I have no idea why the env vars are not substituted properly when passed in environment: ;
for some reason passing in env_file works. [Reference](https://community.influxdata.com/t/telegraf-docker-container-and-env-file-etc-default-telegraf/20170)