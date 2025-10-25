# Wunderground2Influx

This project is a Python-based CLI tool that scrapes weather data from Weather Underground personal weather stations and stores it in an InfluxDB database. It uses Typer for the command-line interface, making it easy to configure and run.

## Features

- Scrapes weather data (temperature, humidity, pressure, and rainfall) from multiple Weather Underground stations
- Stores data in InfluxDB for easy querying and visualization
- Configurable date range for data collection
- **Robust error handling** with automatic retry and exponential backoff
- **Request rate limiting** to be respectful to Weather Underground servers
- **Comprehensive summary reports** showing success/failure statistics
- Docker support for easy deployment
- Command-line interface for easy use and integration into scripts

## Prerequisites

### Option 1: Using Docker (Recommended)
- Docker and Docker Compose

### Option 2: Using uv
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) for dependency management

## Installation

### Using Docker

1. Clone this repository:
   ```bash
   git clone https://github.com/jellevictoor/wunderground2influx.git
   cd wunderground2influx
   ```

2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Using uv

1. Clone this repository:
   ```bash
   git clone https://github.com/jellevictoor/wunderground2influx.git
   cd wunderground2influx
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
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

### Using Docker

The Docker container will automatically run with the settings from your `.env` file:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Using uv

To run the scraper directly with uv:

```bash
uv run python src/main.py --stations STATION1 --stations STATION2 --org your-org --token your-token --url https://your-influx-instance.com
```

### Options

- `--days INTEGER`: Number of days to scrape (default: 60)
- `--bucket TEXT`: InfluxDB bucket name (default: "wunderground")
- `--org TEXT`: InfluxDB organization [required]
- `--token TEXT`: InfluxDB access token [required]
- `--url TEXT`: InfluxDB instance URL (default: "http://localhost:8086")
- `--stations TEXT`: Weather stations to scrape (can be specified multiple times) [required]
- `--max-retries INTEGER`: Maximum retry attempts for failed requests (default: 3)
- `--request-delay FLOAT`: Delay between requests in seconds (default: 1.0)

### Example

To scrape data for the last 30 days and store it in a custom bucket:

```bash
uv run python src/main.py \
  --days 30 \
  --bucket my_weather_data \
  --org my-org \
  --token your_influxdb_token_here \
  --url https://influx.example.com \
  --stations STATION1 \
  --stations STATION2 \
  --stations STATION3
```

## Environment Variables

When using Docker, configure these variables in your `.env` file:

- `STATION_1`, `STATION_2`, `STATION_3`: Weather Underground station IDs
- `INFLUX_URL`: InfluxDB instance URL
- `INFLUX_ORG`: InfluxDB organization name
- `INFLUX_TOKEN`: InfluxDB access token
- `INFLUX_BUCKET`: InfluxDB bucket name (default: wunderground)
- `DAYS`: Number of days to scrape (default: 60)
- `MAX_RETRIES`: Number of retry attempts for failed requests (default: 3)
- `REQUEST_DELAY`: Delay between requests in seconds (default: 1.0)

## Error Handling & Reliability

The scraper includes robust error handling to ensure reliable operation:

- **Automatic Retries**: Failed requests are automatically retried up to 3 times (configurable)
- **Exponential Backoff**: Retry delays increase exponentially (1s, 2s, 4s) to handle temporary issues
- **Timeout Protection**: HTTP requests timeout after 30 seconds to prevent hanging
- **Continue on Failure**: Individual failures don't stop the entire scraping process
- **Comprehensive Reporting**: After completion, you'll see a detailed summary including:
  - Total data points written
  - Successful vs failed scrapes
  - Specific stations/dates that failed
  - InfluxDB write failures (if any)

### Example Summary Output

```
============================================================
SUMMARY
============================================================
Total duration: 45.23s (0.8 minutes)
Total data points written: 2457
Successful scrapes: 27
Failed scrapes: 0
No data available: 3
Failed writes: 0
============================================================
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.