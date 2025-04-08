import requests
import csv
import re
import os
from datetime import datetime, timedelta

#Link to see what you can do with the API
#https://www.weatherapi.com/my/fields.aspx

def sanitize_filename(filename):
    """Sanitize the string to be used as a valid filename."""
    return re.sub(r'[^\w\s-]', '', filename.replace(' ', '_'))

def get_weather_by_city_and_save(city_name):
    api_key = "0fa4dde2d3b54e9baa8233753250704"  # API key is hard coded here
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
    api_key = "0fa4dde2d3b54e9baa8233753250704"  # API key is hard coded here
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
                
                #print(f"Fetched data for {date_str}")
                current_date += timedelta(days=1)
        
        print("Weather data for the past year fetched and saved to CSV.")
    except requests.RequestException as error:
        print(f"Error occurred: {error}")

def get_past_week_weather_by_city_and_save(city_name):
    api_key = "0fa4dde2d3b54e9baa8233753250704"  # API key is hard coded here
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
                
                print(f"Fetched data for {date_str}")
                current_date += timedelta(days=1)
        
        print(f"Weather data for the past week fetched and saved to {csv_file_path}.")
    except requests.RequestException as error:
        print(f"Error occurred: {error}")

# Example usage
city = input("Enter the city name: ")
get_past_week_weather_by_city_and_save(city)
