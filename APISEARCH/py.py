import requests
import csv
import re
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from pandas.plotting import parallel_coordinates


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


def get_weather_with_anomalies(city_name, start_date, end_date):
    """Fetch weather data for a city within a specified date range and flag anomalies."""
    api_key = "a1ca27fc575e4a54b6b03433251004"  # API key is hard coded here
    sanitized_city = sanitize_filename(city_name)

    # Ensure the 'csv' folder exists
    csv_folder = "csv"
    os.makedirs(csv_folder, exist_ok=True)

    # Save the CSV file in the 'csv' folder
    csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_with_anomalies.csv")

    base_url = "https://api.weatherapi.com/v1/history.json"

    try:
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                ["City", "Date", "Temperature (C)", "Condition", "Air Quality Index", "Alerts", "Sunrise", "Sunset", "Anomaly"])

            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

            while current_date <= end_date_obj:
                date_str = current_date.strftime('%Y-%m-%d')
                historical_temperatures = []

                # Fetch data for the same date over the past 10 years
                for year_offset in range(1, 11):
                    query_date = (current_date - timedelta(days=365 * year_offset)).strftime('%Y-%m-%d')
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
                        historical_temperatures.append(day['avgtemp_c'])
                    except requests.RequestException as error:
                        print(f"Error fetching data for {query_date}: {error}")
                        continue

                # Calculate the average temperature and anomaly range
                if historical_temperatures:
                    avg_temp = sum(historical_temperatures) / len(historical_temperatures)
                    anomaly_range = (avg_temp - 3, avg_temp + 3)  # Adjusted to ±3°C
                else:
                    avg_temp = None
                    anomaly_range = (None, None)

                # Fetch current date's data
                parameters = {
                    "key": api_key,
                    "q": city_name,
                    "dt": date_str,
                    "aqi": "yes"
                }

                response = requests.get(base_url, params=parameters)
                response.raise_for_status()
                data = response.json()

                day = data['forecast']['forecastday'][0]['day']
                astro = data['forecast']['forecastday'][0]['astro']  # Extract sunrise and sunset
                alerts = data.get('alerts', {}).get('alert', [])
                alert_text = ', '.join([alert['headline'] for alert in alerts]) if alerts else "No Alerts"

                # Check if the temperature is an anomaly
                is_anomaly = "Yes" if avg_temp and (day['avgtemp_c'] < anomaly_range[0] or day['avgtemp_c'] > anomaly_range[1]) else "No"

                writer.writerow([
                    city_name,
                    date_str,
                    day['avgtemp_c'],
                    day['condition']['text'],
                    day.get('air_quality', {}).get('us-epa-index', "N/A"),
                    alert_text,
                    astro['sunrise'],
                    astro['sunset'],
                    is_anomaly
                ])

                print(f"Fetched data for {date_str} (Anomaly: {is_anomaly})")
                current_date += timedelta(days=1)

        print(f"Weather data with anomalies for {city_name} from {start_date} to {end_date} fetched and saved to {csv_file_path}.")
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


def plot_weather_with_anomalies(city_name):
    """Plot the weather data and highlight anomalies."""
    sanitized_city = sanitize_filename(city_name)
    csv_folder = "csv"
    csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_with_anomalies.csv")

    if not os.path.exists(csv_file_path):
        print(f"No data found for {city_name}. Please fetch the data first.")
        return

    # Read the CSV file
    data = pd.read_csv(csv_file_path)

    # Separate anomalies from normal data
    anomalies = data[data["Anomaly"] == "Yes"]
    normal_data = data[data["Anomaly"] == "No"]

    # Plot the temperature data
    plt.figure(figsize=(12, 6))
    plt.plot(normal_data["Date"], normal_data["Temperature (C)"], marker='o', label="Normal Temperature (C)", color="blue")
    plt.scatter(anomalies["Date"], anomalies["Temperature (C)"], color="red", label="Anomalies", zorder=5)

    # Add labels, title, and legend
    plt.title(f"Weather Data with Anomalies for {city_name}")
    plt.xlabel("Date")
    plt.ylabel("Temperature (C)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_weather_with_anomalies_and_predictions(city_name, predicted_temperatures, prediction_start_date):
    """Plot the weather data, highlight anomalies, and include predicted temperatures in the correct date order."""
    sanitized_city = sanitize_filename(city_name)
    csv_folder = "csv"
    anomalies_csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_with_anomalies.csv")

    if not os.path.exists(anomalies_csv_file_path):
        print(f"No data found for {city_name}. Please fetch the data first.")
        return

    # Read the anomalies CSV file
    data = pd.read_csv(anomalies_csv_file_path)

    # Prepare the actual data
    data["Color"] = data["Anomaly"].apply(lambda x: "red" if x == "Yes" else "blue")
    data["Type"] = "Actual"

    # Prepare the predicted data
    prediction_dates = [(prediction_start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    predicted_data = pd.DataFrame({
        "Date": prediction_dates,
        "Temperature (C)": predicted_temperatures,
        "Color": ["yellow"] * len(predicted_temperatures),
        "Type": ["Predicted"] * len(predicted_temperatures)
    })

    # Combine actual and predicted data
    combined_data = pd.concat([data, predicted_data], ignore_index=True)
    combined_data["Date"] = pd.to_datetime(combined_data["Date"])
    combined_data = combined_data.sort_values(by="Date")

    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.plot(combined_data["Date"], combined_data["Temperature (C)"], color="black", linestyle="-", label="Temperature Line")

    # Plot points with different colors
    plt.scatter(combined_data[combined_data["Color"] == "blue"]["Date"],
                combined_data[combined_data["Color"] == "blue"]["Temperature (C)"],
                color="blue", label="Normal Data", zorder=5)

    plt.scatter(combined_data[combined_data["Color"] == "red"]["Date"],
                combined_data[combined_data["Color"] == "red"]["Temperature (C)"],
                color="red", label="Anomalies", zorder=5)

    plt.scatter(combined_data[combined_data["Color"] == "yellow"]["Date"],
                combined_data[combined_data["Color"] == "yellow"]["Temperature (C)"],
                color="yellow", label="Predicted Data", zorder=5)

    # Add labels, title, and legend
    plt.title(f"Weather Data, Anomalies, and Predictions for {city_name}")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.xticks(combined_data["Date"], combined_data["Date"].dt.strftime('%Y-%m-%d'), rotation=45)  # Show every date
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def compare_cities(cities, start_date, end_date):
    """Compare climate data for multiple cities and visualize clusters with Parallel Coordinates."""
    climate_data = []

    for city in cities:
        # Load the anomalies CSV file for each city
        sanitized_city = sanitize_filename(city)
        csv_folder = "csv"
        anomalies_csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_with_anomalies.csv")

        if not os.path.exists(anomalies_csv_file_path):
            print(f"No data found for {city}. Please fetch the data first.")
            continue

        # Read the CSV file
        print(f"Reading data from {anomalies_csv_file_path}...")
        data = pd.read_csv(anomalies_csv_file_path)
        print(f"Data read successfully for {city}:")
        print(data.head())  # Print the first few rows of the data for debugging

        # Ensure the Temperature (C) column is numeric
        data["Temperature (C)"] = pd.to_numeric(data["Temperature (C)"], errors="coerce")
        print(f"Temperature (C) column after conversion to numeric:")
        print(data["Temperature (C)"])

        # Drop rows with missing or invalid temperature values
        data = data.dropna(subset=["Temperature (C)"])
        print(f"Data after dropping rows with invalid temperatures:")
        print(data)

        # Calculate summary statistics for comparison
        avg_temp = data["Temperature (C)"].mean()
        anomaly_count = data[data["Anomaly"] == "Yes"].shape[0]
        print(f"Average Temperature for {city}: {avg_temp}")
        print(f"Anomaly Count for {city}: {anomaly_count}")
        climate_data.append([city, avg_temp, anomaly_count])

    # Convert to DataFrame
    climate_df = pd.DataFrame(climate_data, columns=["City", "Avg Temperature (C)", "Anomaly Count"])
    print("Final Climate DataFrame:")
    print(climate_df)

    # Normalize the data for clustering and visualization
    scaler = MinMaxScaler()
    normalized_data = scaler.fit_transform(climate_df[["Avg Temperature (C)", "Anomaly Count"]])
    climate_df[["Normalized Temp", "Normalized Anomalies"]] = normalized_data

    # Perform K-Means clustering
    n_clusters = min(len(cities), 3)  # Dynamically adjust the number of clusters
    if n_clusters < 2:
        print("Not enough cities to perform clustering. Please add more cities.")
        return

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    climate_df["Cluster"] = kmeans.fit_predict(climate_df[["Normalized Temp", "Normalized Anomalies"]])

    # Visualize clusters with Parallel Coordinates
    visualize_parallel_coordinates(climate_df)


def visualize_parallel_coordinates(climate_df):
    """Visualize climate data clusters using Parallel Coordinates."""
    # Prepare the data for parallel coordinates
    parallel_data = climate_df[["City", "Normalized Temp", "Normalized Anomalies", "Cluster"]].copy()
    parallel_data["Cluster"] = parallel_data["Cluster"].astype(str)  # Convert cluster to string for color coding

    # Plot Parallel Coordinates
    plt.figure(figsize=(12, 6))
    parallel_coordinates(parallel_data, class_column="Cluster", cols=["Normalized Temp", "Normalized Anomalies"], color=sns.color_palette("husl", len(parallel_data["Cluster"].unique())))
    plt.title("Parallel Coordinates Plot of Climate Data Clusters")
    plt.xlabel("Metrics")
    plt.ylabel("Normalized Values")
    plt.legend(title="Cluster", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


# Store cities entered by the user
cities = []

# Get the date range input once
start_date = input("Enter the start date 2020+ (YYYY-MM-DD): ")
end_date = input("Enter the end date (YYYY-MM-DD): ")

while True:
    # Get user input for the city
    city = input("Enter the city name (or type 'compare' to analyze or 'exit' to quit): ")
    if city.lower() == "exit":
        print("Exiting the program. Goodbye!")
        break
    elif city.lower() == "compare":
        if len(cities) < 2:
            print("Please enter at least two cities before comparing.")
        else:
            compare_cities(cities, start_date, end_date)
        continue

    # Add city to the list
    cities.append(city)

    # Fetch and save weather data with anomalies
    get_weather_with_anomalies(city, start_date, end_date)

    # Predict future temperatures
    predicted_temperatures, prediction_start_date, prediction_end_date = predict_temperature(city, start_date, end_date)

    # Ask the user if they want to see the plot
    show_plot = input(f"Do you want to see the plot for {city}? (yes/no): ").strip().lower()
    if show_plot == "yes":
        if predicted_temperatures:
            plot_weather_with_anomalies_and_predictions(city, predicted_temperatures, prediction_start_date)