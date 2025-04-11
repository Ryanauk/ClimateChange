import os
import re
import csv
import io
import base64
import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for server environments
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import euclidean
from itertools import combinations
from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = "some_secret_key"  # Replace with a secure secret key in production

# ------------------------------
# Helper Functions
# ------------------------------

def sanitize_filename(filename):
    """Sanitize a string to use as a valid filename."""
    return re.sub(r'[^\w\s-]', '', filename.replace(' ', '_'))

def get_weather_with_anomalies(city_name, start_date, end_date):
    """Fetch weather data for a city over a date range and flag anomalies.
       The data is saved as a CSV in the 'csv' folder."""
    api_key = "a1ca27fc575e4a54b6b03433251004"
    sanitized_city = sanitize_filename(city_name)
    csv_folder = "csv"
    os.makedirs(csv_folder, exist_ok=True)
    csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_with_anomalies.csv")
    base_url = "https://api.weatherapi.com/v1/history.json"

    try:
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["City", "Date", "Temperature (C)", "Condition", "Air Quality Index", "Alerts", "Sunrise", "Sunset", "Anomaly"])
            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            while current_date <= end_date_obj:
                date_str = current_date.strftime('%Y-%m-%d')
                historical_temperatures = []
                # Fetch data for the same date over the past 10 years.
                for year_offset in range(1, 11):
                    query_date = (current_date - timedelta(days=365 * year_offset)).strftime('%Y-%m-%d')
                    parameters = {
                        "key": api_key,
                        "q": city_name,
                        "dt": query_date,
                        "aqi": "no"
                    }
                    try:
                        response = requests.get(base_url, params=parameters, timeout=10)
                        response.raise_for_status()
                        data = response.json()
                        day = data['forecast']['forecastday'][0]['day']
                        historical_temperatures.append(day['avgtemp_c'])
                    except requests.RequestException as error:
                        print(f"Error fetching data for {query_date}: {error}")
                        continue
                # Calculate average temperature and set anomaly range (±3°C)
                if historical_temperatures:
                    avg_temp = sum(historical_temperatures) / len(historical_temperatures)
                    anomaly_range = (avg_temp - 3, avg_temp + 3)
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
                response = requests.get(base_url, params=parameters, timeout=10)
                response.raise_for_status()
                data = response.json()
                day = data['forecast']['forecastday'][0]['day']
                astro = data['forecast']['forecastday'][0]['astro']
                alerts = data.get('alerts', {}).get('alert', [])
                alert_text = ', '.join([alert['headline'] for alert in alerts]) if alerts else "No Alerts"
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
        print(f"Weather data with anomalies for {city_name} from {start_date} to {end_date} saved to {csv_file_path}.")
    except requests.RequestException as error:
        print(f"Error occurred: {error}")
    except ValueError as error:
        print(f"Invalid date format: {error}")

def predict_temperature(city_name, start_date, end_date):
    """Predict the temperature for the week following the queried range using the last 10 years of data.
       The predicted data is saved as a CSV and the function returns the predictions and the prediction start date."""
    api_key = "a1ca27fc575e4a54b6b03433251004"
    sanitized_city = sanitize_filename(city_name)
    csv_folder = "csv"
    os.makedirs(csv_folder, exist_ok=True)
    csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_predicted_weather.csv")
    base_url = "https://api.weatherapi.com/v1/history.json"

    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        prediction_start_date = end_date_obj + timedelta(days=1)
        historical_data = {day: [] for day in range(7)}
        for year_offset in range(1, 11):
            for day_offset in range(7):
                query_date = (prediction_start_date - timedelta(days=365 * year_offset) + timedelta(days=day_offset)).strftime('%Y-%m-%d')
                parameters = {
                    "key": api_key,
                    "q": city_name,
                    "dt": query_date,
                    "aqi": "no"
                }
                try:
                    response = requests.get(base_url, params=parameters, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    day = data['forecast']['forecastday'][0]['day']
                    historical_data[day_offset].append(day['avgtemp_c'])
                except requests.RequestException as error:
                    print(f"Error fetching data for {query_date}: {error}")
                    continue
        predicted_temperatures = [sum(temps) / len(temps) if temps else None for temps in historical_data.values()]
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Predicted Temperature (C)"])
            for day_offset, temp in enumerate(predicted_temperatures):
                prediction_date = (prediction_start_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')
                writer.writerow([prediction_date, temp])
        print(f"Predicted temperatures for {city_name} saved to {csv_file_path}.")
        return predicted_temperatures, prediction_start_date, None  # end date not needed for plotting prediction
    except requests.RequestException as error:
        print(f"Error occurred: {error}")
        return None, None, None

def generate_weather_plot(city_name, predicted_temperatures, prediction_start_date):
    """Generate a line and scatter plot for a single city's data and return it as a Base64 string."""
    sanitized_city = sanitize_filename(city_name)
    csv_folder = "csv"
    anomalies_csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_with_anomalies.csv")
    if not os.path.exists(anomalies_csv_file_path):
        print(f"No data found for {city_name}. Please fetch the data first.")
        return None
    data = pd.read_csv(anomalies_csv_file_path)
    data["Color"] = data["Anomaly"].apply(lambda x: "red" if x == "Yes" else "blue")
    data["Type"] = "Actual"
    prediction_dates = [(prediction_start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    predicted_data = pd.DataFrame({
        "Date": prediction_dates,
        "Temperature (C)": predicted_temperatures,
        "Color": ["yellow"] * len(predicted_temperatures),
        "Type": ["Predicted"] * len(predicted_temperatures)
    })
    combined_data = pd.concat([data, predicted_data], ignore_index=True)
    combined_data["Date"] = pd.to_datetime(combined_data["Date"])
    combined_data = combined_data.sort_values(by="Date")

    plt.figure(figsize=(12, 6))
    plt.plot(combined_data["Date"], combined_data["Temperature (C)"], color="black", linestyle="-", label="Temperature Line")
    plt.scatter(combined_data[combined_data["Color"] == "blue"]["Date"],
                combined_data[combined_data["Color"] == "blue"]["Temperature (C)"],
                color="blue", label="Normal Data", zorder=5)
    plt.scatter(combined_data[combined_data["Color"] == "red"]["Date"],
                combined_data[combined_data["Color"] == "red"]["Temperature (C)"],
                color="red", label="Anomalies", zorder=5)
    plt.scatter(combined_data[combined_data["Color"] == "yellow"]["Date"],
                combined_data[combined_data["Color"] == "yellow"]["Temperature (C)"],
                color="yellow", label="Predicted Data", zorder=5)
    plt.title(f"Weather Data, Anomalies, and Predictions for {city_name}")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.xticks(combined_data["Date"], combined_data["Date"].dt.strftime('%Y-%m-%d'), rotation=45)
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf8")
    plt.close()
    return image_base64

def group_most_similar_cities_return(heatmap_data):
    """Compute and return a string identifying the most similar city pair based on temperature data."""
    # Drop columns with all NaN values to avoid errors.
    heatmap_data = heatmap_data.dropna(axis=1, how="all")
    city_pairs = list(combinations(heatmap_data.index, 2))
    distances = {
        pair: euclidean(heatmap_data.loc[pair[0]].fillna(0), heatmap_data.loc[pair[1]].fillna(0))
        for pair in city_pairs
    }
    if not distances:
        return "Not enough data to compare cities."
    most_similar_pair = min(distances, key=distances.get)
    return f"The most similar cities are: {most_similar_pair[0]} and {most_similar_pair[1]}"

def generate_heatmap_image(cities, start_date, end_date):
    """Generate a heatmap of temperature data for multiple cities and return a Base64 image string
       along with a text message for the most similar cities."""
    climate_data = []
    for city in cities:
        sanitized_city = sanitize_filename(city)
        csv_folder = "csv"
        anomalies_csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_with_anomalies.csv")
        if not os.path.exists(anomalies_csv_file_path):
            print(f"No data found for {city}.")
            continue
        data = pd.read_csv(anomalies_csv_file_path)
        data["City"] = city
        data["Date"] = pd.to_datetime(data["Date"]).dt.date  # keep only the date
        climate_data.append(data)

    if not climate_data:
        return None, "No data available for visualization."

    combined_data = pd.concat(climate_data, ignore_index=True)
    heatmap_data = combined_data.pivot(index="City", columns="Date", values="Temperature (C)")
    heatmap_data_normalized = (heatmap_data - heatmap_data.min().min()) / (heatmap_data.max().max() - heatmap_data.min().min())

    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data_normalized, cmap="coolwarm", cbar=True, annot=False, fmt=".1f", linewidths=0.5)
    plt.title("Temperature Heatmap for Selected Cities and Dates")
    plt.xlabel("Date")
    plt.ylabel("City")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    heatmap_base64 = base64.b64encode(buf.getvalue()).decode("utf8")
    plt.close()

    similar_text = group_most_similar_cities_return(heatmap_data)
    return heatmap_base64, similar_text

# ------------------------------
# Flask Routes
# ------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        city = request.form.get("city")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        if not city or not start_date or not end_date:
            return render_template("index.html", error="All fields are required.")
        # Fetch data and predictions for a single city.
        get_weather_with_anomalies(city, start_date, end_date)
        predicted_temperatures, prediction_start_date, _ = predict_temperature(city, start_date, end_date)
        plot_image = generate_weather_plot(city, predicted_temperatures, prediction_start_date)
        return render_template("result.html", city=city, start_date=start_date, end_date=end_date, plot_image=plot_image)
    return render_template("index.html")

@app.route("/compare", methods=["GET", "POST"])
def compare():
    if request.method == "POST":
        cities_input = request.form.get("cities")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        if not cities_input or not start_date or not end_date:
            return render_template("compare.html", error="All fields are required.")
        cities = [c.strip() for c in cities_input.split(",") if c.strip()]
        # Ensure that data exists for each city; fetch if necessary.
        for city in cities:
            sanitized_city = sanitize_filename(city)
            csv_folder = "csv"
            anomalies_csv_file_path = os.path.join(csv_folder, f"{sanitized_city}_weather_with_anomalies.csv")
            if not os.path.exists(anomalies_csv_file_path):
                get_weather_with_anomalies(city, start_date, end_date)
        heatmap_image, similar_text = generate_heatmap_image(cities, start_date, end_date)
        return render_template("compare_result.html",
                               cities=cities,
                               start_date=start_date,
                               end_date=end_date,
                               heatmap_image=heatmap_image,
                               similar_text=similar_text)
    return render_template("compare.html")

# ------------------------------
# WSGI Entry Point
# ------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
