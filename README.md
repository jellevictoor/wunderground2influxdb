# Wunderground2Influx

This project is a Python-based CLI tool that scrapes weather data from Weather Underground personal weather stations and stores it in an InfluxDB database. It uses Typer for the command-line interface, making it easy to configure and run.

## Features

- Scrapes weather data (temperature, humidity, pressure, and rainfall) from multiple Weather Underground stations
- Stores data in InfluxDB for easy querying and visualization
- Configurable date range for data collection
- Command-line interface for easy use and integration into scripts

## Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/jellevictoor/wunderground2influx.git
   cd wunderground2influx
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

This will create a virtual environment and install all required dependencies.

## Dependencies

This project uses the following main dependencies:

- pandas: Data manipulation and analysis
- beautifulsoup4: Web scraping library
- requests: HTTP library for making requests
- lxml: XML and HTML processing library
- influxdb-client: Client for interacting with InfluxDB
- typer: Library for building CLI applications

For a full list of dependencies, see the `pyproject.toml` file.

## Usage

To run the scraper, use Poetry to execute the script:

```
poetry run python wunderground2influx/main.py
```

### Options

- `--days INTEGER`: Number of days to scrape (default: 60)
- `--bucket TEXT`: InfluxDB bucket name (default: "wunderground")
- `--org TEXT`: InfluxDB organization [required]
- `--token TEXT`: InfluxDB access token [required]
- `--url TEXT`: InfluxDB instance URL (default: "http://localhost:8086")
- `--stations TEXT`: Weather stations to scrape [required]

### Example

To scrape data for the last 30 days and store it in a custom bucket:

```
poetry run python wunderground2influx/main.py --days 30 --bucket my_weather_data --token your_influxdb_token_here
```

To use custom weather stations:

```
poetry run python wunderground2influx/main.py --stations STATION1 --stations STATION2 --stations STATION3 --token your_influxdb_token_here
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
