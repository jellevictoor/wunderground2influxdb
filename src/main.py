from datetime import datetime, timedelta

import pandas as pd
import pytz

from html_scraper import scrape_weather_data


def format_date(original_date_string):
    original_date = datetime.strptime(original_date_string, '%Y-%m-%d %I:%M %p')

    # Add a timezone (e.g., UTC)
    timezone = pytz.timezone('CET')
    original_date_with_timezone = timezone.localize(original_date)

    # Format the date to include zero-padding and timezone
    return original_date_with_timezone.strftime('%Y-%m-%d %H:%M:%S %Z')


stations = ["IARDOO6", "IARDOO10", "IPITTE11"]


def get_dates():
    # Get the current date
    current_date = datetime.now()
    return [(current_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 31)]


dates = get_dates()

for station in stations:
    for date in dates:
        url = f"https://www.wunderground.com/dashboard/pws/{station}/table/{date}/{date}/daily"
        df = scrape_weather_data(url)

        # Iterate through the rows and generate InfluxDB INSERT statements

        for index, row in df.iterrows():
            timestamp = pd.Timestamp(
                format_date(f"{date} {row['Time']}")).value  # Assuming 'Time' is a column with timestamps
            temperature = row['Temperature']
            humidity = row['Humidity']
            pressure = row['Pressure']
            rain = row['Rain']

            # Format the INSERT statement
            influx_insert = (
                # f"influx -precision rfc3339 -database wunderground "
                f'{station} '
                f'temperature={temperature},humidity={humidity},'
                f'pressure={pressure},'
                f'rain={rain} {timestamp}'
            )

            print(influx_insert)
