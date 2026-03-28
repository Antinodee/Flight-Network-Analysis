# Flight Network Analysis - Community Detection

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import Counter
import community as community_louvain
import folium
from folium.plugins import MarkerCluster

# Load the network
try:
    flight_network = nx.read_gexf("data/flight_network.gexf")
    print("Loaded flight network from file")
except:
    print("Error loading network file. Please run the network creation script first.")
    exit()

# Load airport data for geographic visualization
airports_df = pd.read_csv('data/airports_cleaned.csv')
airports_dict = airports_df.set_index('IATA').to_dict('index')

def detect_communities():
    """
    Detect communities in the flight network
    """
    print("Detecting communities in the flight network...")
    
    # Convert directed graph to undirected for community detection
    undirected_network = flight_network.to_undirected()
    
    # Apply Louvain community detection
    print("Applying Louvain community detection algorithm...")
    communities = community_louvain.best_partition(undirected_network)
    
    # Count airports in each community
    community_counts = Counter(communities.values())
    print(f"Detected {len(community_counts)} communities")
    
    # Sort communities by size (number of airports)
    sorted_communities = sorted(community_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop 10 largest communities:")
    for i, (community_id, count) in enumerate(sorted_communities[:10]):
        print(f"Community {i+1}: {count} airports ({count/len(communities):.2%} of total)")
    
    # Add community assignment to each airport
    community_df = pd.DataFrame({
        'Airport': list(communities.keys()),
        'Community': list(communities.values())
    })
    
    # Add airport information
    community_df['Airport Name'] = community_df['Airport'].map(lambda x: airports_dict.get(x, {}).get('Name', 'Unknown'))
    community_df['City'] = community_df['Airport'].map(lambda x: airports_dict.get(x, {}).get('City', 'Unknown'))
    community_df['Country'] = community_df['Airport'].map(lambda x: airports_dict.get(x, {}).get('Country', 'Unknown'))
    community_df['Latitude'] = community_df['Airport'].map(lambda x: airports_dict.get(x, {}).get('Latitude', np.nan))
    community_df['Longitude'] = community_df['Airport'].map(lambda x: airports_dict.get(x, {}).get('Longitude', np.nan))
    
    # Save community assignments
    community_df.to_csv('results/airport_communities.csv', index=False)
    
    return community_df, communities

# Run community detection
community_df, communities = detect_communities()

# Analyze the geographical distribution of communities
def analyze_community_geography():
    """
    Analyze the geographical distribution of communities
    """
    print("\nAnalyzing geographical distribution of communities...")
    
    # For each community, calculate the geographic center and radius
    community_geography = {}
    
    for community_id in community_df['Community'].unique():
        # Get airports in this community
        community_airports = community_df[community_df['Community'] == community_id]
        
        # Calculate geographic center (mean lat/lon)
        center_lat = community_airports['Latitude'].mean()
        center_lon = community_airports['Longitude'].mean()
        
        # Calculate geographic radius (standard deviation of distances)
        if len(community_airports) > 1:
            distances = np.sqrt((community_airports['Latitude'] - center_lat)**2 + 
                               (community_airports['Longitude'] - center_lon)**2)
            radius = distances.std()
        else:
            radius = 0
        
        # Count countries in this community
        country_counts = community_airports['Country'].value_counts()
        main_countries = country_counts.head(3).index.tolist()
        
        # Store results
        community_geography[community_id] = {
            'center_lat': center_lat,
            'center_lon': center_lon,
            'radius': radius,
            'num_airports': len(community_airports),
            'main_countries': main_countries
        }
    
    # Convert to DataFrame
    geo_df = pd.DataFrame.from_dict(community_geography, orient='index')
    geo_df['community_id'] = geo_df.index
    geo_df = geo_df.sort_values('num_airports', ascending=False)
    
    # Save results
    geo_df.to_csv('results/community_geography.csv', index=False)
    
    return geo_df

# Analyze community geography
community_geo_df = analyze_community_geography()

# Print summary of top communities
print("\nGeographic analysis of top 5 communities:")
for i, row in community_geo_df.head(5).iterrows():
    print(f"Community {i} ({row['num_airports']} airports):")
    print(f"  Center: {row['center_lat']:.2f}, {row['center_lon']:.2f}")
    print(f"  Geographic spread (radius): {row['radius']:.2f}")
    print(f"  Main countries: {', '.join(row['main_countries'])}")

# Create a world map visualization of communities
def create_community_map():
    """
    Create an interactive map of flight network communities
    """
    print("\nCreating interactive community map...")
    
    # Create a base map centered at (0, 0)
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='cartodbpositron')
    
    # Create a marker cluster for better performance
    marker_cluster = MarkerCluster().add_to(m)
    
    # Generate a color palette for communities
    num_communities = len(community_df['Community'].unique())
    colors = plt.cm.rainbow(np.linspace(0, 1, num_communities))
    color_map = {comm_id: f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}' 
                for comm_id, (r, g, b, _) in zip(sorted(community_df['Community'].unique()), colors)}
    
    # Add markers for each airport
    for idx, airport in community_df.iterrows():
        if pd.notna(airport['Latitude']) and pd.notna(airport['Longitude']):
            # Create a circle marker
            folium.CircleMarker(
                location=[airport['Latitude'], airport['Longitude']],
                radius=5,
                color=color_map[airport['Community']],
                fill=True,
                fill_color=color_map[airport['Community']],
                fill_opacity=0.7,
                popup=f"{airport['Airport']} - {airport['Airport Name']}<br>{airport['City']}, {airport['Country']}<br>Community: {airport['Community']}"
            ).add_to(marker_cluster)
    
    # Add community centers as larger markers
    for idx, community in community_geo_df.iterrows():
        if pd.notna(community['center_lat']) and pd.notna(community['center_lon']):
            folium.CircleMarker(
                location=[community['center_lat'], community['center_lon']],
                radius=10,
                color='black',
                fill=True,
                fill_color=color_map[idx],
                fill_opacity=0.7,
                popup=f"Community {idx}<br>{community['num_airports']} airports<br>Main countries: {', '.join(community['main_countries'])}"
            ).add_to(m)
    
    # Save the map
    m.save('results/community_map.html')
    print("Interactive community map saved to results/community_map.html")

# Create community map
create_community_map()

# Analyze inter-community connections
def analyze_inter_community_connections():
    """
    Analyze connections between different communities
    """
    print("\nAnalyzing inter-community connections...")
    
    # Create a community-to-community adjacency matrix
    communities_list = sorted(communities.values())
    community_ids = sorted(list(set(communities_list)))
    num_communities = len(community_ids)
    
    # Initialize adjacency matrix
    community_matrix = np.zeros((num_communities, num_communities))
    
    # Fill the matrix with edge counts
    for source, target in flight_network.edges():
        if source in communities and target in communities:
            source_community = communities[source]
            target_community = communities[target]
            community_matrix[source_community, target_community] += 1
    
    # Create a DataFrame for easier analysis
    community_df = pd.DataFrame(
        community_matrix, 
        index=community_ids, 
        columns=community_ids
    )
    
    # Save the matrix
    community_df.to_csv('results/inter_community_connections.csv')
    
    # Create a heatmap visualization
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        community_df.iloc[:10, :10],  # Show only top 10 communities
        annot=True, 
        fmt='.0f', 
        cmap='viridis'
    )
    plt.title('Flight Connections Between Top 10 Communities', fontsize=16)
    plt.xlabel('Destination Community', fontsize=14)
    plt.ylabel('Source Community', fontsize=14)
    plt.tight_layout()
    plt.savefig('results/inter_community_heatmap.png')
    plt.close()
    
    print("Inter-community connection analysis saved to results/inter_community_connections.csv")
    print("Heatmap visualization saved to results/inter_community_heatmap.png")
    
    return community_df

# Analyze inter-community connections
community_connections = analyze_inter_community_connections()