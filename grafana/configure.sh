#!/bin/sh

# Modify the defaults.ini file with the environment variables
sed -i "s/^;admin_user = admin/admin_user = ${GRAFANA_USERNAME}/" /usr/share/grafana/conf/defaults.ini
sed -i "s/^;admin_password = admin/admin_password = ${GRAFANA_PASSWORD}/" /usr/share/grafana/conf/defaults.ini

# Start Grafana
/usr/sbin/grafana-server --homepath=/usr/share/grafana
