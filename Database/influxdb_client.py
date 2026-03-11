import os
from influxdb_client import InfluxDBClient
from utils.env_loader import load_env

load_env()

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://devraq.rcvdev.team/influxdb/")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "9c00d5b8def8d01d15034e9ad5157f306b8dd8e9056a020cb74ba47538a23f2e")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "RCV-Vamanit-ORG")

def get_influxdb_client():
    return InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)