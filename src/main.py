import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict

import pandas as pd
import pytz
import typer
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from html_scraper import scrape_weather_data

app = typer.Typer()


def get_dates_to_scrape(no_of_days: int) -> List[str]:
    current_date = datetime.now()
    return [(current_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, no_of_days)]


def scrape_with_retry(url: str, max_retries: int = 3, delay: float = 1.0) -> Optional[pd.DataFrame]:
    """Scrape data with retry logic and exponential backoff."""
    for attempt in range(max_retries):
        try:
            df = scrape_weather_data(url)
            if df is not None and len(df) > 0:
                return df

            # If no data returned, wait before retry
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                typer.echo(f"  No data returned, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                typer.echo(f"  Error: {str(e)}, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                typer.echo(f"  Failed after {max_retries} attempts: {str(e)}")

    return None


@app.command()
def scrape_and_store(
        days: int = typer.Option(60, help="Number of days to scrape"),
        stations: List[str] = typer.Option(..., help="Wunderground weatherstations IDs to scrape"),
        url: str = typer.Option("http://localhost:8086", help="InfluxDB instance URL"),
        org: str = typer.Option(..., help="InfluxDB organization"),
        bucket: str = typer.Option("wunderground", help="InfluxDB bucket name"),
        token: str = typer.Option(..., help="InfluxDB access token"),
        max_retries: int = typer.Option(3, help="Maximum number of retries for failed requests"),
        request_delay: float = typer.Option(1.0, help="Delay between requests in seconds"),
):
    dates = get_dates_to_scrape(days)
    influxdb_client = InfluxDBClient(url=url, token=token, org=org)
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    timezone = pytz.timezone('CET')

    # Track statistics
    stats: Dict[str, List[str]] = {
        'successful': [],
        'failed_scrape': [],
        'failed_write': [],
        'no_data': []
    }
    total_points = 0
    start_time_total = time.time()

    typer.echo(f"Starting scrape of {len(stations)} stations for {len(dates)} days ({len(stations) * len(dates)} total requests)")
    typer.echo("")

    for date in dates:
        for station in stations:
            station_url = f"https://www.wunderground.com/dashboard/pws/{station}/table/{date}/{date}/daily"
            start_time = time.time()

            typer.echo(f"Scraping {station} for {date}...")

            # Scrape with retry logic
            df = scrape_with_retry(station_url, max_retries=max_retries)

            if df is None:
                stats['failed_scrape'].append(f"{station} - {date}")
                typer.echo(f"  ✗ Failed to scrape data")
                time.sleep(request_delay)
                continue

            if len(df) == 0:
                stats['no_data'].append(f"{station} - {date}")
                typer.echo(f"  ⚠ No data available")
                time.sleep(request_delay)
                continue

            # Convert to InfluxDB points
            try:
                points = []
                for index, row in df.iterrows():
                    # Parse the date and time without timezone first
                    naive_datetime = datetime.strptime(f"{date} {row['Time']}", '%Y-%m-%d %I:%M %p')
                    # Localize to CET timezone
                    aware_datetime = timezone.localize(naive_datetime)
                    # Convert to pandas timestamp with proper timezone handling
                    timestamp = pd.Timestamp(aware_datetime).value

                    point = (Point(station)
                         .field("temperature", row['Temperature'])
                         .field("humidity", row['Humidity'])
                         .field("pressure", row['Pressure'])
                         .field("rain", row['Rain'])
                         .time(timestamp))
                    points.append(point)

                # Write to InfluxDB
                write_api.write(bucket=bucket, org=org, record=points)
                total_points += len(points)
                stats['successful'].append(f"{station} - {date}")

                end_time = time.time()
                typer.echo(f"  ✓ Wrote {len(points)} points in {(end_time - start_time):.2f}s")

            except Exception as e:
                stats['failed_write'].append(f"{station} - {date}: {str(e)}")
                typer.echo(f"  ✗ Failed to write to InfluxDB: {str(e)}")

            # Delay between requests to be nice to the server
            time.sleep(request_delay)

    # Print summary
    end_time_total = time.time()
    duration = end_time_total - start_time_total

    typer.echo("")
    typer.echo("=" * 60)
    typer.echo("SUMMARY")
    typer.echo("=" * 60)
    typer.echo(f"Total duration: {duration:.2f}s ({duration/60:.1f} minutes)")
    typer.echo(f"Total data points written: {total_points}")
    typer.echo(f"Successful scrapes: {len(stats['successful'])}")
    typer.echo(f"Failed scrapes: {len(stats['failed_scrape'])}")
    typer.echo(f"No data available: {len(stats['no_data'])}")
    typer.echo(f"Failed writes: {len(stats['failed_write'])}")

    if stats['failed_scrape']:
        typer.echo("")
        typer.echo("Failed scrapes:")
        for item in stats['failed_scrape']:
            typer.echo(f"  - {item}")

    if stats['failed_write']:
        typer.echo("")
        typer.echo("Failed writes:")
        for item in stats['failed_write']:
            typer.echo(f"  - {item}")

    if stats['no_data']:
        typer.echo("")
        typer.echo("No data available:")
        for item in stats['no_data'][:10]:  # Show first 10
            typer.echo(f"  - {item}")
        if len(stats['no_data']) > 10:
            typer.echo(f"  ... and {len(stats['no_data']) - 10} more")

    typer.echo("=" * 60)


if __name__ == "__main__":
    app()
