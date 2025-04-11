import unittest
from unittest.mock import patch, mock_open, MagicMock
from  APISEARCH.climate import *

class TestSanitizeFileName(unittest.TestCase):
    def test_sanitize_simple(self):
        self.assertEqual(sanitize_filename("New York"), "New_York")

    def test_sanitize_with_special_chars(self):
        self.assertEqual(sanitize_filename("Los Angeles!@#$"), "Los_Angeles")

    def test_sanitize_numbers(self):
        self.assertEqual(sanitize_filename("Miami 2025!"), "Miami_2025")

    def test_sanitize_empty(self):
        self.assertEqual(sanitize_filename(""), "")

    def test_sanitize_dashes(self):
        self.assertEqual(sanitize_filename("San-Francisco"), "San-Francisco")


class TestGetWeatherWithAnomalies(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")  # To prevent actual directory creation
    @patch("requests.get")
    def test_get_weather_with_anomalies(self, mock_get, mock_makedirs, mock_file):
        # Mock API response for historical data and current data
        fake_day_data = {
            "forecast": {
                "forecastday": [
                    {
                        "day": {
                            "avgtemp_c": 25.0,
                            "condition": {"text": "Sunny"},
                            "air_quality": {"us-epa-index": 2}
                        },
                        "astro": {
                            "sunrise": "6:30 AM",
                            "sunset": "7:45 PM"
                        }
                    }
                ]
            },
            "alerts": {
                "alert": [{"headline": "Heat Advisory"}]
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = fake_day_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Use a fixed short range to avoid long loops
        get_weather_with_anomalies("Test City", "2023-04-01", "2023-04-01")

        # Assert file write was attempted
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called()  # CSV writer wrote something

        # Assert that requests.get was called at least once
        self.assertTrue(mock_get.called)
        self.assertGreaterEqual(mock_get.call_count, 11)


class TestPredictTemperature(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("requests.get")
    def test_predict_temperature(self, mock_get, mock_makedirs, mock_file):
        fake_day_data = {
            "forecast": {
                "forecastday": [
                    {
                        "day": {
                            "avgtemp_c": 20.0
                        }
                    }
                ]
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = fake_day_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        temps, start, end = predict_temperature("Test City", "2023-04-01", "2023-04-01")

        self.assertIsNotNone(temps)
        self.assertEqual(len(temps), 7)
        self.assertTrue(all(t == 20.0 for t in temps))
        mock_file.assert_called()
        self.assertGreaterEqual(mock_get.call_count, 70)


class TestPlotWeatherWithAnomaliesAndPrediction(unittest.TestCase):
    @patch("pandas.read_csv")
    @patch("os.path.exists", return_value=True)
    @patch("matplotlib.pyplot.show")
    def test_plot_weather_with_anomalies_and_predictions(self, mock_show, mock_exists, mock_read_csv):
        mock_df = pd.DataFrame({
            "Date": ["2023-04-01"],
            "Temperature (C)": [22],
            "Anomaly": ["No"]
        })
        mock_read_csv.return_value = mock_df

        predicted = [23, 24, 25, 26, 27, 28, 29]
        prediction_start_date = datetime.strptime("2023-04-02", "%Y-%m-%d")

        # Just test that the function runs
        plot_weather_with_anomalies_and_predictions("Test City", predicted, prediction_start_date)
        mock_show.assert_called()


class TestPlotClimateHeatMap(unittest.TestCase):
    @patch("APISEARCH.climate.os.path.exists", return_value=True)
    @patch("APISEARCH.climate.pd.read_csv")
    @patch("APISEARCH.climate.plt.show")
    @patch("APISEARCH.climate.group_most_similar_cities")
    def test_plot_climate_heatmap(self, mock_group, mock_show, mock_read_csv, mock_exists):
        # Simulate data for two cities
        mock_read_csv.side_effect = [
            pd.DataFrame({
                "Date": ["2023-04-01", "2023-04-02"],
                "Temperature (C)": [20.0, 21.0],
                "Anomaly": ["No", "Yes"]
            }),
            pd.DataFrame({
                "Date": ["2023-04-01", "2023-04-02"],
                "Temperature (C)": [19.0, 20.5],
                "Anomaly": ["No", "No"]
            })
        ]

        plot_climate_heatmap(["CityA", "CityB"], "2023-04-01", "2023-04-02")

        # Check that plot was shown and grouping was triggered
        mock_show.assert_called_once()
        mock_group.assert_called_once()


class TestGroupMostSimilarCities(unittest.TestCase):
    def test_group_most_similar_cities(self):
        df = pd.DataFrame({
            "2023-04-01": [20.0, 20.1, 35.0],
            "2023-04-02": [21.0, 21.1, 36.0]
        }, index=["CityA", "CityB", "CityC"])

        # Should identify CityA and CityB as most similar
        with patch("builtins.print") as mock_print:
            group_most_similar_cities(df)
            mock_print.assert_called_with("The most similar cities are: CityA and CityB")


if __name__ == '__main__':
    unittest.main()