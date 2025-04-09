"""

"""

import csv

with open('Tallahassee.csv', 'r') as file:
    csv_reader = csv.DictReader(file)

    for row in csv_reader:
        print(row["name"], row["datetime"], row["tempmax"], row["tempmin"] )