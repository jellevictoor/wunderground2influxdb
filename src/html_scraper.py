import pandas as pd
import requests
from bs4 import BeautifulSoup


def scrape_weather_data(url):
    # Send an HTTP GET request to fetch the webpage content
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table with the class 'history-table'
        table = soup.select_one('.history-table.desktop-table')
        if table is not None:
            # Initialize lists to store the extracted data
            times = []
            temperature_c = []
            humidity_percent = []
            wind_speed_kph = []
            pressure_hpa = []
            rain_mm = []

            # Find all rows in the table (you may need to adjust the selector)
            rows = table.find_all('tr')

            # Loop through the rows and extract data from each cell
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 9:
                    try:
                        time = cells[0].strong.text.strip()
                        temperature = parse_value(cells[1].span.span.text.strip())
                        humidity = parse_value(cells[3].span.span.text.strip())
                        pressure = parse_value(cells[7].span.span.text.strip())
                        rain = parse_value(cells[9].span.span.text.strip())

                        # Append the data to respective lists
                        times.append(time)
                        temperature_c.append((temperature - 32) * 5 / 9)
                        humidity_percent.append(humidity)
                        pressure_hpa.append(pressure * 33.863889532610884)
                        rain_mm.append(rain * 25.4)
                    except:
                        print(f"Error parsing row for {url}")
            data = {
                'Time': times,
                'Temperature': temperature_c,
                'Humidity': humidity_percent,
                'Pressure': pressure_hpa,
                'Rain': rain_mm
            }
            try:
                df = pd.DataFrame(data)
                return df
            except:
                print(f"Error creating dataframe for {url}")
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")


def parse_value(value):
    try:
        return float(value)

    except ValueError:
        return
