import pandas as pd
import numpy as np

class DataProcessor:
def __init__(self, file_path: str):
....


def load_data(self) -> pd.DataFrame:
"""Load climate data from CSV file."""
.....

def clean_data(self) -> pd.DataFrame:
"""Remove rows with missing values and normalize temperature
data."""
.....

def get_features_and_target(self) -> Tuple[np.ndarray,
np.ndarray]:
"""Split data into features (year, month) and target
(temperature)."""
.....
