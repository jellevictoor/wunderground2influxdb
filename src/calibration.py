from influxdb_client import InfluxDBClient
import pandas as pd
import statistics

# InfluxDB connection settings
org = "victoor.io"
token = "ZeJgWpsHbzNwsskV5O2ObJaMo2pnd_OlmXYeM6SK-d1-hxMiPSws3cFA3fOKXDlsuYZPkyswqhxm5w_-NsjcIg=="
# Store the URL of your InfluxDB instance
url="http://192.168.1.5:8086"

# Create an InfluxDB client
client = InfluxDBClient(
   url=url,
   token=token,
   org=org,
    timeout=30_000
)

# Flux query
flux_query = '''
ventilation = from(bucket: "wunderground")
  |> range(start: 2024-01-01T00:00:00Z, stop: 2024-01-09T00:00:00Z)
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> drop(columns: ["_measurement"])
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)

station = from(bucket: "homeassistant")
  |> range(start: 2024-01-01T00:00:00Z, stop: 2024-01-09T00:00:00Z)
  |> filter(fn: (r) => r["entity_id"] == "nilan_temp_t1_outdoor")
  |> filter(fn: (r) => r["_field"] == "value")
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)

join(
  tables: {ventilation: ventilation, station: station},
  on: ["_time"],
)
|> map(fn: (r) => ({
      _time: r._time,
      _value: r._value_station - r._value_ventilation
  }))
|> yield(name: "difference")
'''

# Execute the Flux query
query_api = client.query_api()
result = query_api.query_data_frame( query=flux_query)

# Filter out outliers based on standard deviation
mean_difference = statistics.mean(result['_value'])
std_deviation = statistics.stdev(result['_value'])
threshold = 4 * std_deviation  # Adjust the threshold as needed

filtered_result = result[(result['_value'] >= mean_difference - threshold) & (result['_value'] <= mean_difference + threshold)]

# Calculate the standard deviation and correction factor for the filtered data
filtered_difference_values = filtered_result['_value'].tolist()
filtered_std_deviation = statistics.stdev(filtered_difference_values)
filtered_correction_factor = statistics.mean(filtered_difference_values)

# Print the results for filtered data
print(f"Filtered Standard Deviation: {filtered_std_deviation}")
print(f"Filtered Correction Factor: {filtered_correction_factor}")