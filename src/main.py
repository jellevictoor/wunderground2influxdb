import time
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import pytz
import typer
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from html_scraper import scrape_weather_data

app = typer.Typer()


def format_date(original_date_string: str) -> str:
    original_date = datetime.strptime(original_date_string, '%Y-%m-%d %I:%M %p')
    timezone = pytz.timezone('CET')
    original_date_with_timezone = timezone.localize(original_date)
    return original_date_with_timezone.strftime('%Y-%m-%d %H:%M:%S %Z')


def get_dates_to_scrape(no_of_days: int) -> List[str]:
    current_date = datetime.now()
    return [(current_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, no_of_days)]


@app.command()
def scrape_and_store(
        days: int = typer.Option(60, help="Number of days to scrape"),
        stations: List[str] = typer.Option(..., help="Wunderground weatherstations IDs to scrape"),
        url: str = typer.Option("http://localhost:8086", help="InfluxDB instance URL"),
        org: str = typer.Option(..., help="InfluxDB organization"),
        bucket: str = typer.Option("wunderground", help="InfluxDB bucket name"),
        token: str = typer.Option(..., help="InfluxDB access token"),
):
    dates = get_dates_to_scrape(days)
    influxdb_client = InfluxDBClient(url=url, token=token, org=org)
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

    for date in dates:
        for station in stations:
            station_url = f"https://www.wunderground.com/dashboard/pws/{station}/table/{date}/{date}/daily"
            start_time = time.time()

            df = scrape_weather_data(station_url)

            if df is None:
                continue

            points = []
            for index, row in df.iterrows():
                timestamp = pd.Timestamp(format_date(f"{date} {row['Time']}")).value
                point = (Point(station)
                     .field("temperature", row['Temperature'])
                     .field("humidity", row['Humidity'])
                     .field("pressure", row['Pressure'])
                     .field("rain", row['Rain'])
                     .time(timestamp))
                points.append(point)
            write_api.write(bucket=bucket, org=org, record=points)
            end_time = time.time()

            typer.echo(f"Finished scraping {station_url} in {(end_time - start_time):.2f} seconds")


if __name__ == "__main__":
    app()
