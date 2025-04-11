# ClimateChange

Structure:
```
climate_change_analyzer/
├── data/
│   └── climate_data.csv
│
├── src/
│   ├── __init__.py
│   ├── data_processor.py
│   ├── algorithms.py
│   ├── visualizer.py
│   ├── cli.py
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   ├── test_data_processor.py
│   ├── test_algorithms.py
│   └── test_visualizer.py
│
├── requirements.txt
└── README.md
```
**Flask Weather App**

- Fetches historical weather data from WeatherAPI (or another weather service).

- Flags anomalies in temperature data over a specified date range.

- Predicts future temperatures using historical data.

- Supports comparing multiple cities via a heatmap and similarity measure.


app.py – The main Flask application file. Defines routes for:

    Single‑city weather analysis (/).

    Multiple‑city comparison (/compare).

templates/ – Contains the HTML templates:

    index.html, result.html: For single‑city analysis.

    compare.html, compare_result.html: For comparing multiple cities.

**Installation**

1. Clone Repository
```
git clone https://github.com/Ryanauk/ClimateChange.git
cd ClimateChange
```
2. Create Virtual Enviroment
```
python3 -m venv myenv
source myenv/bin/activate
```
3. Install Dependencies:
```
pip install flask gunicorn requests pandas matplotlib seaborn scipy
```
**Running**

The file can be tested locally by running:
```
python app.py
```
The file is set up for my system at: http://127.0.0.1:5000 
so you might need to change to the ip or your system to test!

**Producing Server**
```
gunicorn -w 4 --timeout 120 -b 0.0.0.0:5000 app:app
# --timeout is used to give the API time for the information
# 0.0.0.0 is for request on this machines server
# 5000 is to listen to port 5000
```
Afterwards load up the url on your browser per the ip on the machine for example: http://127.0.0.1:5000 

# Work Load Share:
```bash
Reid:
1. data_processor.py
2.
3.

Ryan:
1. Data input information(Weather API)
2.
3.

Michael:
1.
2.
3.

Together:
- Main.py

