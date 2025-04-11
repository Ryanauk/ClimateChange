import os
import re
import csv
import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import euclidean
from itertools import combinations


def sanitize_filename(filename):
    """Sanitize the string to be used as a valid filename."""
    return re.sub(r'[^\w\s-]', '', filename.replace(' ', '_'))


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


def plot_climate_heatmap(cities, start_date, end_date):
    """Create a static heatmap to visualize temperature data over time and group the most similar cities."""
    climate_data = []

    # Load data for each city
    for city in cities:
        sanitized_city = sanitize_filename(city)
        csv_folder = "csv"
        anomalies_csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_with_anomalies.csv")

        if not os.path.exists(anomalies_csv_file_path):
            print(f"No data found for {city}. Please fetch the data first.")
            continue

        # Read the CSV file
        data = pd.read_csv(anomalies_csv_file_path)
        data["City"] = city
        data["Date"] = pd.to_datetime(data["Date"]).dt.date  # Keep only the date, remove time
        climate_data.append(data)

    # Combine all city data into a single DataFrame
    if not climate_data:
        print("No data available for visualization.")
        return

    combined_data = pd.concat(climate_data, ignore_index=True)

    # Pivot the data to create a heatmap-friendly format
    heatmap_data = combined_data.pivot(index="City", columns="Date", values="Temperature (C)")

    # Normalize the temperature values for consistent coloring
    heatmap_data_normalized = (heatmap_data - heatmap_data.min().min()) / (heatmap_data.max().max() - heatmap_data.min().min())

    # Plot the heatmap
    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data_normalized, cmap="coolwarm", cbar=True, annot=False, fmt=".1f", linewidths=0.5)
    plt.title("Temperature Heatmap for Selected Cities and Dates")
    plt.xlabel("Date")
    plt.ylabel("City")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Group the most similar cities
    group_most_similar_cities(heatmap_data)


def group_most_similar_cities(heatmap_data):
    """Find and display the two most similar cities based on temperature data."""
    # Drop columns with all NaN values to avoid errors in similarity calculation
    heatmap_data = heatmap_data.dropna(axis=1, how="all")

    # Calculate pairwise distances between cities
    city_pairs = list(combinations(heatmap_data.index, 2))
    distances = {
        pair: euclidean(heatmap_data.loc[pair[0]].fillna(0), heatmap_data.loc[pair[1]].fillna(0))
        for pair in city_pairs
    }

    # Find the pair with the smallest distance
    most_similar_pair = min(distances, key=distances.get)
    print(f"The most similar cities are: {most_similar_pair[0]} and {most_similar_pair[1]}")


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
            #compare_cities(cities, start_date, end_date)
            plot_climate_heatmap(cities, start_date, end_date)
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