import time
from datetime import datetime, timedelta

import pandas as pd
import pytz
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from html_scraper import scrape_weather_data


def format_date(original_date_string):
    original_date = datetime.strptime(original_date_string, '%Y-%m-%d %I:%M %p')

    # Add a timezone (e.g., UTC)
    timezone = pytz.timezone('CET')
    original_date_with_timezone = timezone.localize(original_date)

    # Format the date to include zero-padding and timezone
    return original_date_with_timezone.strftime('%Y-%m-%d %H:%M:%S %Z')


stations = ["IARDOO6", "IARDOO10", "IPITTE11"]
bucket = "wunderground"
org = "victoor.io"
token = "ZeJgWpsHbzNwsskV5O2ObJaMo2pnd_OlmXYeM6SK-d1-hxMiPSws3cFA3fOKXDlsuYZPkyswqhxm5w_-NsjcIg=="
# Store the URL of your InfluxDB instance
url="http://192.168.1.5:8086"


def get_dates(no_of_days=2):
    # Get the current date
    current_date = datetime.now()
    return [(current_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, no_of_days)]


dates = get_dates(1)
influxdb_client = InfluxDBClient(
   url=url,
   token=token,
   org=org
)
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

for date in dates:
    for station in stations:
        url = f"https://www.wunderground.com/dashboard/pws/{station}/table/{date}/{date}/daily"
        start_time = time.time()
        df = scrape_weather_data(url)
        if df is not None:
            for index, row in df.iterrows():
                timestamp = pd.Timestamp(
                    format_date(f"{date} {row['Time']}")).value
                temperature = row['Temperature']
                humidity = row['Humidity']
                pressure = row['Pressure']
                rain = row['Rain']
                p = (Point(station)
                     .field("temperature", temperature)
                     .field("humidity", humidity)
                     .field("pressure", pressure)
                     .field("rain", rain)
                     .time(timestamp))
                write_api.write(bucket=bucket, org=org, record=p)
        end_time = time.time()
        print(f"Finished scraping {url} in {(end_time - start_time):.2f} seconds")