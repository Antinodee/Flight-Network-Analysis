# Flight Network Analysis - Network Creation

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load cleaned data
airports_df = pd.read_csv('data/airports_cleaned.csv')
routes_df = pd.read_csv('data/routes_cleaned.csv')

def create_flight_network():
    """
    Creates a NetworkX graph from flight routes data
    """
    # Create directed graph
    G = nx.DiGraph()
    
    # Create dictionary for fast airport lookup
    airport_dict = airports_df.set_index('IATA').to_dict('index')
    
    # Add airports as nodes with attributes
    for iata, data in airport_dict.items():
        if pd.notna(iata) and iata != '\\N':
            G.add_node(
                iata,
                name=data['Name'],
                city=data['City'],
                country=data['Country'],
                latitude=data['Latitude'],
                longitude=data['Longitude']
            )
    
    print(f"Added {G.number_of_nodes()} airports as nodes")
    
    # Add routes as edges
    edge_count = 0
    for _, route in routes_df.iterrows():
        source = route['Source airport']
        dest = route['Destination airport']
        
        if source in G and dest in G:
            # Add edge if it doesn't exist, otherwise increment weight
            if G.has_edge(source, dest):
                G[source][dest]['weight'] += 1
            else:
                G.add_edge(source, dest, weight=1)
                edge_count += 1
    
    print(f"Added {edge_count} routes as edges")
    
    # Remove isolated nodes (airports with no connections)
    isolated_nodes = list(nx.isolates(G))
    G.remove_nodes_from(isolated_nodes)
    print(f"Removed {len(isolated_nodes)} isolated airports")
    
    print(f"Final network: {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    return G

# Create the flight network
flight_network = create_flight_network()

# Save the network to disk for later use
nx.write_gexf(flight_network, "data/flight_network.gexf")
print("Network saved to disk")

# Basic network statistics
print("\nBasic Network Statistics:")
print(f"Number of airports (nodes): {flight_network.number_of_nodes()}")
print(f"Number of routes (edges): {flight_network.number_of_edges()}")
print(f"Network density: {nx.density(flight_network):.6f}")

# Check if the network is connected
if nx.is_strongly_connected(flight_network):
    print("The network is strongly connected (can reach any airport from any other)")
else:
    # For directed graphs, we typically look at the largest strongly connected component
    largest_scc = max(nx.strongly_connected_components(flight_network), key=len)
    print(f"The network is not strongly connected")
    print(f"Largest strongly connected component has {len(largest_scc)} airports ({len(largest_scc)/flight_network.number_of_nodes():.2%} of total)")

# Analyze the weakly connected components (ignoring direction)
weakly_connected_components = list(nx.weakly_connected_components(flight_network))
print(f"Number of weakly connected components: {len(weakly_connected_components)}")
largest_wcc = max(weakly_connected_components, key=len)
print(f"Largest weakly connected component has {len(largest_wcc)} airports ({len(largest_wcc)/flight_network.number_of_nodes():.2%} of total)")

# Check network diameter (longest shortest path)
# This can be computationally expensive for large networks
try:
    diameter = nx.diameter(max(nx.strongly_connected_components(flight_network), key=len))
    print(f"Network diameter (in largest SCC): {diameter}")
except:
    print("Network diameter calculation skipped (computationally expensive)")

# Create a histogram of node degrees
in_degrees = [d for n, d in flight_network.in_degree()]
out_degrees = [d for n, d in flight_network.out_degree()]

plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.hist(in_degrees, bins=30, alpha=0.7)
plt.title('Incoming Flights Distribution')
plt.xlabel('Number of Incoming Flights')
plt.ylabel('Number of Airports')

plt.subplot(1, 2, 2)
plt.hist(out_degrees, bins=30, alpha=0.7)
plt.title('Outgoing Flights Distribution')
plt.xlabel('Number of Outgoing Flights')
plt.ylabel('Number of Airports')

plt.tight_layout()
plt.savefig('results/degree_distribution.png')
plt.close()

print("Degree distribution plot saved to results/degree_distribution.png")