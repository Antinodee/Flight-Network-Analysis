# Flight Network Analysis - Data Acquisition

import pandas as pd
import requests
import io
import os

def download_openflights_data():
    """
    Downloads airport and route data from OpenFlights dataset
    """
    # URLs for the datasets
    airports_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    routes_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
    
    # Column names for the datasets
    airports_columns = [
        'Airport ID', 'Name', 'City', 'Country', 'IATA', 'ICAO',
        'Latitude', 'Longitude', 'Altitude', 'Timezone', 'DST',
        'Tz database time zone', 'Type', 'Source'
    ]
    
    routes_columns = [
        'Airline', 'Airline ID', 'Source airport', 'Source airport ID',
        'Destination airport', 'Destination airport ID',
        'Codeshare', 'Stops', 'Equipment'
    ]
    
    # Download and save airports data
    print("Downloading airports data...")
    airports_response = requests.get(airports_url)
    airports_df = pd.read_csv(io.StringIO(airports_response.text), names=airports_columns)
    airports_df.to_csv('data/airports.csv', index=False)
    print(f"Airports data saved. Total airports: {len(airports_df)}")
    
    # Download and save routes data
    print("Downloading routes data...")
    routes_response = requests.get(routes_url)
    routes_df = pd.read_csv(io.StringIO(routes_response.text), names=routes_columns)
    routes_df.to_csv('data/routes.csv', index=False)
    print(f"Routes data saved. Total routes: {len(routes_df)}")
    
    return airports_df, routes_df

# Download data if it doesn't exist locally
if not os.path.exists('data/airports.csv') or not os.path.exists('data/routes.csv'):
    airports_df, routes_df = download_openflights_data()
else:
    print("Loading existing data...")
    airports_df = pd.read_csv('data/airports.csv')
    routes_df = pd.read_csv('data/routes.csv')
    print(f"Data loaded. {len(airports_df)} airports and {len(routes_df)} routes.")

# Display sample data
print("\nSample airports data:")
print(airports_df.head())

print("\nSample routes data:")
print(routes_df.head())

# Basic data cleaning
print("\nCleaning data...")

# Clean airports data - remove airports without IATA codes
airports_df = airports_df[airports_df['IATA'] != '\\N']
print(f"Airports after removing those without IATA codes: {len(airports_df)}")

# Clean routes data - ensure source and destination airports have valid codes
routes_df = routes_df[routes_df['Source airport'] != '\\N']
routes_df = routes_df[routes_df['Destination airport'] != '\\N']
print(f"Routes after cleaning: {len(routes_df)}")

# Save cleaned data
airports_df.to_csv('data/airports_cleaned.csv', index=False)
routes_df.to_csv('data/routes_cleaned.csv', index=False)

print("Data acquisition and cleaning complete!")