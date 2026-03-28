# Flight Network Analysis - Seasonal Patterns

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import random
from collections import defaultdict

# Since we don't have actual seasonal data, let's create a synthetic dataset
# to demonstrate how seasonal analysis could be performed
def generate_seasonal_data():
    """
    Generate synthetic seasonal flight data for demonstration
    """
    print("Generating synthetic seasonal flight data...")
    
    # Load the base network
    try:
        flight_network = nx.read_gexf("data/flight_network.gexf")
        print(f"Loaded flight network with {flight_network.number_of_nodes()} airports and {flight_network.number_of_edges()} routes")
    except:
        print("Error loading network file. Please run the network creation script first.")
        exit()
    
    # Load airports for reference
    airports_df = pd.read_csv('data/airports_cleaned.csv')
    
    # Define seasons
    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    
    # Create a dictionary to store seasonal networks
    seasonal_networks = {}
    
    # Define geographical regions based on latitude and longitude
    def get_region(lat, lon):
        if lat > 30:  # Northern hemisphere
            return 'North'
        elif lat < -30:  # Southern hemisphere
            return 'South'
        else:  # Tropical
            return 'Tropical'
    
    # Add region to airports
    airports_df['Region'] = airports_df.apply(
        lambda row: get_region(row['Latitude'], row['Longitude']), 
        axis=1
    )
    
    # Define seasonal coefficients for each region
    # These represent how likely flights are to operate in each season
    seasonal_coefficients = {
        'North': {
            'Winter': 0.8,  # Fewer flights in winter
            'Spring': 1.0,
            'Summer': 1.2,  # More flights in summer
            'Fall': 1.0
        },
        'South': {
            'Winter': 1.2,  # Winter in north is summer in south
            'Spring': 1.0,
            'Summer': 0.8,  # Summer in north is winter in south
            'Fall': 1.0
        },
        'Tropical': {
            'Winter': 1.1,  # Slight increase in winter (holiday travel)
            'Spring': 0.9,
            'Summer': 1.0,
            'Fall': 0.9
        }
    }
    
    # Additional tourism coefficients for specific destinations
    tourism_destinations = {
        # Beach destinations - more popular in summer
        'MIA': {'Winter': 1.2, 'Spring': 1.1, 'Summer': 1.5, 'Fall': 1.0},  # Miami
        'CUN': {'Winter': 1.3, 'Spring': 1.2, 'Summer': 1.4, 'Fall': 1.0},  # Cancun
        'HNL': {'Winter': 1.3, 'Spring': 1.1, 'Summer': 1.4, 'Fall': 1.0},  # Honolulu
        
        # Ski destinations - more popular in winter
        'DEN': {'Winter': 1.4, 'Spring': 1.0, 'Summer': 1.0, 'Fall': 1.0},  # Denver
        'ZRH': {'Winter': 1.5, 'Spring': 1.0, 'Summer': 1.1, 'Fall': 1.0},  # Zurich
        'YVR': {'Winter': 1.3, 'Spring': 1.0, 'Summer': 1.2, 'Fall': 1.0},  # Vancouver
        
        # Holiday destinations - peaks in winter and summer
        'MCO': {'Winter': 1.3, 'Spring': 1.0, 'Summer': 1.3, 'Fall': 0.9},  # Orlando
        'LAS': {'Winter': 1.1, 'Spring': 1.0, 'Summer': 1.2, 'Fall': 1.0},  # Las Vegas
        'CDG': {'Winter': 1.0, 'Spring': 1.1, 'Summer': 1.4, 'Fall': 1.0},  # Paris
        'FCO': {'Winter': 0.9, 'Spring': 1.1, 'Summer': 1.5, 'Fall': 1.0},  # Rome
    }
    
    # Create a mapping of airports to regions for fast lookup
    airport_regions = airports_df.set_index('IATA')['Region'].to_dict()
    
    # Generate seasonal networks
    for season in seasons:
        print(f"Generating {season} network...")
        
        # Create a new graph for this season
        G = nx.DiGraph()
        
        # Add all nodes (airports) with their attributes
        for node in flight_network.nodes():
            G.add_node(node, **flight_network.nodes[node])
        
        # Process each edge (flight route)
        for source, target, data in flight_network.edges(data=True):
            # Default weight
            weight = data.get('weight', 1)
            
            # Get regions for source and destination airports
            source_region = airport_regions.get(source, 'Tropical')
            target_region = airport_regions.get(target, 'Tropical')
            
            # Apply seasonal coefficients
            source_coef = seasonal_coefficients[source_region][season]
            target_coef = seasonal_coefficients[target_region][season]
            
            # Apply tourism coefficients if applicable
            source_tourism = tourism_destinations.get(source, {'Winter': 1, 'Spring': 1, 'Summer': 1, 'Fall': 1})
            target_tourism = tourism_destinations.get(target, {'Winter': 1, 'Spring': 1, 'Summer': 1, 'Fall': 1})
            
            # Calculate the combined coefficient
            combined_coef = (source_coef + target_coef) / 2 * (source_tourism[season] + target_tourism[season]) / 2
            
            # Add some randomness
            random_factor = random.uniform(0.9, 1.1)
            final_coef = combined_coef * random_factor
            
            # Calculate new weight
            new_weight = max(1, int(weight * final_coef))
            
            # Add edge with new weight
            G.add_edge(source, target, weight=new_weight)
        
        # Store the seasonal network
        seasonal_networks[season] = G
        print(f"  {season} network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Save the seasonal networks
    for season, G in seasonal_networks.items():
        nx.write_gexf(G, f"data/flight_network_{season.lower()}.gexf")
    
    print("Synthetic seasonal networks generated and saved")
    
    return seasonal_networks, airports_df

# Generate seasonal data
seasonal_networks, airports_df = generate_seasonal_data()

def analyze_seasonal_patterns():
    """
    Analyze seasonal patterns in the flight networks
    """
    print("\nAnalyzing seasonal patterns...")
    
    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    
    # Calculate network metrics for each season
    metrics = {
        'Season': [],
        'Number of Flights (Edges)': [],
        'Average Flights per Airport': [],
        'Network Density': [],
        'Average Degree Centrality': []
    }
    
    # Airport-specific seasonal metrics
    airport_metrics = defaultdict(lambda: {'Airport': None, 'IATA': None, 'Winter': 0, 'Spring': 0, 'Summer': 0, 'Fall': 0})
    
    for season in seasons:
        G = seasonal_networks[season]
        
        # Calculate network-level metrics
        metrics['Season'].append(season)
        metrics['Number of Flights (Edges)'].append(G.number_of_edges())
        metrics['Average Flights per Airport'].append(G.number_of_edges() / G.number_of_nodes())
        metrics['Network Density'].append(nx.density(G))
        
        # Calculate average degree centrality
        degree_centrality = nx.degree_centrality(G)
        metrics['Average Degree Centrality'].append(np.mean(list(degree_centrality.values())))
        
        # Calculate airport-specific metrics
        for airport, degree in G.degree():
            airport_metrics[airport]['Airport'] = G.nodes[airport].get('name', 'Unknown')
            airport_metrics[airport]['IATA'] = airport
            airport_metrics[airport][season] = degree
    
    # Convert metrics to DataFrame
    metrics_df = pd.DataFrame(metrics)
    metrics_df.to_csv('results/seasonal_network_metrics.csv', index=False)
    
    # Convert airport metrics to DataFrame
    airport_metrics_df = pd.DataFrame.from_dict(airport_metrics, orient='index')
    
    # Calculate seasonal variation for each airport
    airport_metrics_df['Seasonal Variation'] = airport_metrics_df.apply(
        lambda row: np.std([row['Winter'], row['Spring'], row['Summer'], row['Fall']]), 
        axis=1
    )
    
    # Calculate summer/winter ratio
    airport_metrics_df['Summer/Winter Ratio'] = airport_metrics_df.apply(
        lambda row: row['Summer'] / max(1, row['Winter']), 
        axis=1
    )
    
    # Sort by seasonal variation
    airport_metrics_df = airport_metrics_df.sort_values('Seasonal Variation', ascending=False)
    
    # Save airport seasonal metrics
    airport_metrics_df.to_csv('results/airport_seasonal_metrics.csv', index=False)
    
    # Find airports with highest seasonal variation
    top_seasonal_airports = airport_metrics_df.head(20)
    
    print("\nTop 10 airports with highest seasonal variation:")
    for i, (_, row) in enumerate(top_seasonal_airports.head(10).iterrows()):
        print(f"{i+1}. {row['IATA']} - {row['Airport']}")
        print(f"   Winter: {row['Winter']}, Spring: {row['Spring']}, Summer: {row['Summer']}, Fall: {row['Fall']}")
        print(f"   Seasonal Variation: {row['Seasonal Variation']:.2f}, Summer/Winter Ratio: {row['Summer/Winter Ratio']:.2f}")
    
    return metrics_df, airport_metrics_df

# Analyze seasonal patterns
network_metrics, airport_metrics = analyze_seasonal_patterns()

# Create visualizations
def visualize_seasonal_patterns():
    """
    Create visualizations of seasonal patterns
    """
    print("\nCreating seasonal pattern visualizations...")
    
    # Plot network metrics by season
    plt.figure(figsize=(15, 10))
    
    metrics_to_plot = [
        'Number of Flights (Edges)', 
        'Average Flights per Airport',
        'Network Density', 
        'Average Degree Centrality'
    ]
    
    for i, metric in enumerate(metrics_to_plot):
        plt.subplot(2, 2, i+1)
        sns.barplot(
            x='Season', 
            y=metric, 
            data=network_metrics,
            palette='viridis'
        )
        plt.title(f'Seasonal Variation in {metric}', fontsize=14)
        plt.xticks(rotation=0)
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/seasonal_network_metrics_plot.png')
    plt.close()
    
    # Plot top 10 airports with highest seasonal variation
    top_airports = airport_metrics.head(10)
    
    # Reshape data for plotting
    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    plot_data = []
    
    for _, row in top_airports.iterrows():
        for season in seasons:
            plot_data.append({
                'Airport': f"{row['IATA']} ({row['Airport'][:10]}...)",
                'Season': season,
                'Connections': row[season]
            })
    
    plot_df = pd.DataFrame(plot_data)
    
    # Create plot
    plt.figure(figsize=(14, 8))
    sns.barplot(
        x='Airport', 
        y='Connections', 
        hue='Season',
        data=plot_df,
        palette='viridis'
    )
    plt.title('Seasonal Variation in Airport Connections', fontsize=16)
    plt.xlabel('Airport', fontsize=14)
    plt.ylabel('Number of Connections', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Season')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('results/top_seasonal_airports.png')
    plt.close()
    
    print("Seasonal pattern visualizations saved to results folder")

# Create visualizations
visualize_seasonal_patterns()