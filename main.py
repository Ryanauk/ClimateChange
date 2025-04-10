import requests
import csv
import re
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd


# Link to see what you can do with the API
# https://www.weatherapi.com/my/fields.aspx

def sanitize_filename(filename):
    """Sanitize the string to be used as a valid filename."""
    return re.sub(r'[^\w\s-]', '', filename.replace(' ', '_'))


def get_weather_by_city_and_save(city_name):
    api_key = "a1ca27fc575e4a54b6b03433251004"  # API key is hard coded here
    sanitized_city = sanitize_filename(city_name)
    csv_file_path = f"{sanitized_city}_weather_data.csv"

    base_url = "https://api.weatherapi.com/v1/forecast.json"  # Changed to HTTPS
    parameters = {
        "key": api_key,
        "q": city_name,
        "days": 1,
        "aqi": "yes",
        "alerts": "yes"
    }

    try:
        response = requests.get(base_url, params=parameters)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()

        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["City", "Temperature (C)", "Condition", "Air Quality Index", "Alerts"])

            current = data['current']
            alerts = data.get('alerts', {}).get('alert', [])
            alert_text = ', '.join([alert['headline'] for alert in alerts]) if alerts else "No Alerts"

            writer.writerow([
                city_name,
                current['temp_c'],
                current['condition']['text'],
                current['air_quality']['us-epa-index'],
                alert_text
            ])

        print("Weather data fetched and saved to CSV.")
    except requests.RequestException as error:
        print(f"Error occurred: {error}")


def get_past_year_weather_by_city_and_save(city_name):
    api_key = "a1ca27fc575e4a54b6b03433251004"  # API key is hard coded here
    sanitized_city = sanitize_filename(city_name)
    csv_file_path = f"{sanitized_city}_weather_data.csv"

    base_url = "https://api.weatherapi.com/v1/history.json"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    try:
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["City", "Date", "Temperature (C)", "Condition", "Air Quality Index", "Alerts"])

            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                parameters = {
                    "key": api_key,
                    "q": city_name,
                    "dt": date_str,
                    "aqi": "yes"
                }

                response = requests.get(base_url, params=parameters)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                data = response.json()

                day = data['forecast']['forecastday'][0]['day']
                alerts = data.get('alerts', {}).get('alert', [])
                alert_text = ', '.join([alert['headline'] for alert in alerts]) if alerts else "No Alerts"

                writer.writerow([
                    city_name,
                    date_str,
                    day['avgtemp_c'],
                    day['condition']['text'],
                    day.get('air_quality', {}).get('us-epa-index', "N/A"),
                    alert_text
                ])

                # print(f"Fetched data for {date_str}")
                current_date += timedelta(days=1)

        print("Weather data for the past year fetched and saved to CSV.")
    except requests.RequestException as error:
        print(f"Error occurred: {error}")


def get_past_week_weather_by_city_and_save(city_name):
    api_key = "a1ca27fc575e4a54b6b03433251004"  # API key is hard coded here
    sanitized_city = sanitize_filename(city_name)

    # Ensure the 'csv' folder exists
    csv_folder = "csv"
    os.makedirs(csv_folder, exist_ok=True)

    # Save the CSV file in the 'csv' folder
    csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_data.csv")

    base_url = "https://api.weatherapi.com/v1/history.json"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)  # Fetch data for the past 7 days

    try:
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                ["City", "Date", "Temperature (C)", "Condition", "Air Quality Index", "Alerts", "Sunrise", "Sunset"])

            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                parameters = {
                    "key": api_key,
                    "q": city_name,
                    "dt": date_str,
                    "aqi": "yes"
                }

                response = requests.get(base_url, params=parameters)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                data = response.json()

                day = data['forecast']['forecastday'][0]['day']
                astro = data['forecast']['forecastday'][0]['astro']  # Extract sunrise and sunset
                alerts = data.get('alerts', {}).get('alert', [])
                alert_text = ', '.join([alert['headline'] for alert in alerts]) if alerts else "No Alerts"

                writer.writerow([
                    city_name,
                    date_str,
                    day['avgtemp_c'],
                    day['condition']['text'],
                    day.get('air_quality', {}).get('us-epa-index', "N/A"),
                    alert_text,
                    astro['sunrise'],  # Add sunrise
                    astro['sunset']  # Add sunset
                ])

                print(f"Fetched data for {date_str}")
                current_date += timedelta(days=1)

        print(f"Weather data for the past week fetched and saved to {csv_file_path}.")
    except requests.RequestException as error:
        print(f"Error occurred: {error}")


def get_weather_by_city_and_date_range(city_name, start_date, end_date):
    """Fetch weather data for a city within a specified date range."""
    api_key = "a1ca27fc575e4a54b6b03433251004"  # API key is hard coded here
    sanitized_city = sanitize_filename(city_name)

    # Ensure the 'csv' folder exists
    csv_folder = "csv"
    os.makedirs(csv_folder, exist_ok=True)

    # Save the CSV file in the 'csv' folder
    csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_data.csv")

    base_url = "https://api.weatherapi.com/v1/history.json"

    try:
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                ["City", "Date", "Temperature (C)", "Condition", "Air Quality Index", "Alerts", "Sunrise", "Sunset"])

            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

            while current_date <= end_date_obj:
                date_str = current_date.strftime('%Y-%m-%d')
                parameters = {
                    "key": api_key,
                    "q": city_name,
                    "dt": date_str,
                    "aqi": "yes"
                }

                response = requests.get(base_url, params=parameters)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                data = response.json()

                day = data['forecast']['forecastday'][0]['day']
                astro = data['forecast']['forecastday'][0]['astro']  # Extract sunrise and sunset
                alerts = data.get('alerts', {}).get('alert', [])
                alert_text = ', '.join([alert['headline'] for alert in alerts]) if alerts else "No Alerts"

                writer.writerow([
                    city_name,
                    date_str,
                    day['avgtemp_c'],
                    day['condition']['text'],
                    day.get('air_quality', {}).get('us-epa-index', "N/A"),
                    alert_text,
                    astro['sunrise'],  # Add sunrise
                    astro['sunset']  # Add sunset
                ])

                print(f"Fetched data for {date_str}")
                current_date += timedelta(days=1)

        print(f"Weather data for {city_name} from {start_date} to {end_date} fetched and saved to {csv_file_path}.")
    except requests.RequestException as error:
        print(f"Error occurred: {error}")
    except ValueError as error:
        print(f"Invalid date format: {error}")


def predict_temperature(city_name, start_date, end_date):
    """Predict the temperature for the week after the queried range using the last 10 years of historical data."""
    api_key = "a1ca27fc575e4a54b6b03433251004"  # API key is hard coded here
    sanitized_city = sanitize_filename(city_name)

    # Ensure the 'csv' folder exists
    csv_folder = "csv"
    os.makedirs(csv_folder, exist_ok=True)

    # Save the CSV file in the 'csv' folder
    csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_predicted_weather.csv")

    base_url = "https://api.weatherapi.com/v1/history.json"

    try:
        # Parse the start and end dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        prediction_start_date = end_date_obj + timedelta(days=1)
        prediction_end_date = prediction_start_date + timedelta(days=6)

        # Collect data for the last 10 years
        historical_data = {day: [] for day in range(7)}  # Store temperatures for each day of the prediction week

        for year_offset in range(1, 11):  # Last 10 years
            for day_offset in range(7):  # 7 days of prediction
                query_date = (prediction_start_date - timedelta(days=365 * year_offset) + timedelta(
                    days=day_offset)).strftime('%Y-%m-%d')

                parameters = {
                    "key": api_key,
                    "q": city_name,
                    "dt": query_date,
                    "aqi": "no"
                }

                try:
                    response = requests.get(base_url, params=parameters)
                    response.raise_for_status()
                    data = response.json()
                    day = data['forecast']['forecastday'][0]['day']
                    historical_data[day_offset].append(day['avgtemp_c'])
                except requests.RequestException as error:
                    print(f"Error fetching data for {query_date}: {error}")
                    continue

        # Calculate the average temperature for each day of the prediction week
        predicted_temperatures = [sum(temps) / len(temps) if temps else None for temps in historical_data.values()]

        # Save the predicted data to a CSV file
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Predicted Temperature (C)"])

            for day_offset, temp in enumerate(predicted_temperatures):
                prediction_date = (prediction_start_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')
                writer.writerow([prediction_date, temp])

        print(f"Predicted temperatures for {city_name} saved to {csv_file_path}.")
        return predicted_temperatures, prediction_start_date, prediction_end_date
    except requests.RequestException as error:
        print(f"Error occurred: {error}")
        return None, None, None


def plot_weather_data(city_name):
    """Plot the weather data from the CSV file."""
    sanitized_city = sanitize_filename(city_name)
    csv_folder = "csv"
    csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_data.csv")

    if not os.path.exists(csv_file_path):
        print(f"No data found for {city_name}. Please fetch the data first.")
        return

    # Read the CSV file
    data = pd.read_csv(csv_file_path)

    # Plot the temperature data
    plt.figure(figsize=(10, 6))
    plt.plot(data["Date"], data["Temperature (C)"], marker='o', label="Temperature (C)")
    plt.title(f"Weather Data for {city_name}")
    plt.xlabel("Date")
    plt.ylabel("Temperature (C)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_weather_with_prediction(city_name, start_date, end_date, predicted_temperatures, prediction_start_date):
    """Plot the weather data along with the predicted temperatures."""
    sanitized_city = sanitize_filename(city_name)
    csv_folder = "csv"
    csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_data.csv")

    if not os.path.exists(csv_file_path):
        print(f"No data found for {city_name}. Please fetch the data first.")
        return

    # Read the CSV file
    data = pd.read_csv(csv_file_path)

    # Plot the actual temperature data
    plt.figure(figsize=(12, 6))
    plt.plot(data["Date"], data["Temperature (C)"], marker='o', label="Actual Temperature (C)", color="blue")

    # Plot the predicted temperatures
    prediction_dates = [(prediction_start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    plt.plot(prediction_dates, predicted_temperatures, marker='o', label="Predicted Temperature (C)", color="orange")

    # Add labels, title, and legend
    plt.title(f"Weather Data and Predictions for {city_name}")
    plt.xlabel("Date")
    plt.ylabel("Temperature (C)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# Example usage
city = input("Enter the city name: ")
start_date = input("Enter the start date (YYYY-MM-DD): ")
end_date = input("Enter the end date (YYYY-MM-DD): ")

# Fetch and plot actual data
get_weather_by_city_and_date_range(city, start_date, end_date)

# Predict and plot future data
predicted_temperatures, prediction_start_date, prediction_end_date = predict_temperature(city, start_date, end_date)
if predicted_temperatures:
    plot_weather_with_prediction(city, start_date, end_date, predicted_temperatures, prediction_start_date)