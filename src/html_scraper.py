import pandas as pd
import requests
from bs4 import BeautifulSoup


def scrape_weather_data(url, timeout=30):
    # Send an HTTP GET request to fetch the webpage content
    response = requests.get(url, timeout=timeout)

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
                if len(cells) >= 10:
                    try:
                        # Extract time from first cell
                        time_elem = cells[0].find('strong')
                        if not time_elem:
                            continue
                        time = time_elem.text.strip()

                        # Extract values from wu-value spans
                        temp_elem = cells[1].find('span', class_='wu-value')
                        humidity_elem = cells[3].find('span', class_='wu-value')
                        pressure_elem = cells[7].find('span', class_='wu-value')
                        rain_elem = cells[9].find('span', class_='wu-value')

                        if not all([temp_elem, humidity_elem, pressure_elem, rain_elem]):
                            continue

                        temperature = parse_value(temp_elem.text.strip())
                        humidity = parse_value(humidity_elem.text.strip())
                        pressure = parse_value(pressure_elem.text.strip())
                        rain = parse_value(rain_elem.text.strip())

                        if temperature is None or humidity is None or pressure is None or rain is None:
                            continue

                        # Append the data to respective lists
                        times.append(time)
                        temperature_c.append((temperature - 32) * 5 / 9)
                        humidity_percent.append(humidity)
                        pressure_hpa.append(pressure * 33.863889532610884)
                        rain_mm.append(rain * 25.4)
                    except Exception as e:
                        print(f"Error parsing row for {url}: {e}")
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
    except (ValueError, TypeError):
        return None
