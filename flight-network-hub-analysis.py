# Flight Network Analysis - Hub Analysis

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

# Ignore warnings for centrality calculations that might not converge
warnings.filterwarnings('ignore')

# Load the network
try:
    flight_network = nx.read_gexf("data/flight_network.gexf")
    print("Loaded flight network from file")
except:
    print("Error loading network file. Please run the network creation script first.")
    exit()

# Load airport data for reference
try:
    airports_df = pd.read_csv('data/airports_cleaned.csv')
    # Create a dictionary for airport information lookup
    if 'IATA' in airports_df.columns:
        # Determine the column names for airport info
        name_col = 'Name' if 'Name' in airports_df.columns else 'name' if 'name' in airports_df.columns else 'airport_name'
        city_col = 'City' if 'City' in airports_df.columns else 'city'
        country_col = 'Country' if 'Country' in airports_df.columns else 'country'
        
        # Create a dictionary for easy lookup
        airport_info = {}
        for _, row in airports_df.iterrows():
            iata = row['IATA']
            airport_info[iata] = {
                'name': row[name_col] if name_col in airports_df.columns else 'Unknown',
                'city': row[city_col] if city_col in airports_df.columns else 'Unknown',
                'country': row[country_col] if country_col in airports_df.columns else 'Unknown'
            }
    else:
        # Create a fallback dictionary if IATA column isn't found
        airport_info = {}
        print("Warning: Could not find IATA column in airports data")
except Exception as e:
    print(f"Error loading airport data: {e}")
    airport_info = {}  # Empty dictionary as fallback

def identify_important_hubs():
    """
    Identifies important airports (hubs) using different centrality measures
    """
    print("Calculating centrality measures...")
    
    # Calculate various centrality measures
    # Degree centrality - simple count of connections
    in_degree_centrality = nx.in_degree_centrality(flight_network)
    out_degree_centrality = nx.out_degree_centrality(flight_network)
    
    # Betweenness centrality - measures how often a node is on the shortest path between other nodes
    # This can be computationally expensive for large networks
    print("Calculating betweenness centrality (this may take a while)...")
    betweenness_centrality = nx.betweenness_centrality(flight_network, k=100)  # Using approximation with k=100 samples
    
    # PageRank - measures the importance of a node based on its connections
    pagerank = nx.pagerank(flight_network, alpha=0.85)
    
    # Create a DataFrame with the results
    centrality_df = pd.DataFrame({
        'Airport': list(flight_network.nodes()),
        'In-Degree Centrality': [in_degree_centrality.get(node, 0) for node in flight_network.nodes()],
        'Out-Degree Centrality': [out_degree_centrality.get(node, 0) for node in flight_network.nodes()],
        'Betweenness Centrality': [betweenness_centrality.get(node, 0) for node in flight_network.nodes()],
        'PageRank': [pagerank.get(node, 0) for node in flight_network.nodes()]
    })
    
    # Add airport information
    centrality_df['Airport Name'] = centrality_df['Airport'].apply(
        lambda x: airport_info.get(x, {}).get('name', 'Unknown')
    )
    centrality_df['City'] = centrality_df['Airport'].apply(
        lambda x: airport_info.get(x, {}).get('city', 'Unknown')
    )
    centrality_df['Country'] = centrality_df['Airport'].apply(
        lambda x: airport_info.get(x, {}).get('country', 'Unknown')
    )
    
    # Save the results
    os.makedirs('results', exist_ok=True)
    centrality_df.to_csv('results/airport_centrality_measures.csv', index=False)
    
    return centrality_df

# Identify important hubs
centrality_df = identify_important_hubs()

# Display top 20 airports by different centrality measures
print("\nTop 20 airports by In-Degree Centrality (most arriving flights):")
top_in_degree = centrality_df.sort_values('In-Degree Centrality', ascending=False).head(20)
print(top_in_degree[['Airport', 'Airport Name', 'City', 'Country', 'In-Degree Centrality']])

print("\nTop 20 airports by Out-Degree Centrality (most departing flights):")
top_out_degree = centrality_df.sort_values('Out-Degree Centrality', ascending=False).head(20)
print(top_out_degree[['Airport', 'Airport Name', 'City', 'Country', 'Out-Degree Centrality']])

print("\nTop 20 airports by Betweenness Centrality (most important for connections):")
top_betweenness = centrality_df.sort_values('Betweenness Centrality', ascending=False).head(20)
print(top_betweenness[['Airport', 'Airport Name', 'City', 'Country', 'Betweenness Centrality']])

print("\nTop 20 airports by PageRank (overall importance in the network):")
top_pagerank = centrality_df.sort_values('PageRank', ascending=False).head(20)
print(top_pagerank[['Airport', 'Airport Name', 'City', 'Country', 'PageRank']])

# Create visualization of the top 10 hubs by PageRank
try:
    plt.figure(figsize=(12, 8))
    top10_pagerank = centrality_df.sort_values('PageRank', ascending=False).head(10)

    # Create a bar plot
    sns.barplot(
        x='Airport', 
        y='PageRank', 
        data=top10_pagerank,
        palette='viridis'
    )

    plt.title('Top 10 Global Airports by PageRank Centrality', fontsize=16)
    plt.xlabel('Airport Code', fontsize=14)
    plt.ylabel('PageRank Centrality Score', fontsize=14)
    plt.xticks(rotation=45)

    # Add airport names as annotations
    for i, row in enumerate(top10_pagerank.itertuples()):
        # Use safe attribute access with getattr
        airport_name = getattr(row, 'Airport Name', 'Unknown')
        city = getattr(row, 'City', 'Unknown')
        country = getattr(row, 'Country', 'Unknown')
        
        # Safe concatenation with empty string fallbacks
        annotation_text = f"{airport_name or ''}\n{city or ''}, {country or ''}"
        
        plt.text(
            i, 
            row.PageRank + 0.001, 
            annotation_text, 
            ha='center', 
            va='bottom', 
            fontsize=9
        )

    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/top10_airports_pagerank.png')
    plt.close()

    print("Top 10 airports visualization saved to results/top10_airports_pagerank.png")
except Exception as e:
    print(f"Error creating visualization: {e}")

# Correlation between centrality measures
try:
    print("\nCalculating correlation between centrality measures...")
    correlation_matrix = centrality_df[['In-Degree Centrality', 'Out-Degree Centrality', 
                                      'Betweenness Centrality', 'PageRank']].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Between Centrality Measures', fontsize=16)
    plt.tight_layout()
    plt.savefig('results/centrality_correlation.png')
    plt.close()

    print("Centrality correlation heatmap saved to results/centrality_correlation.png")
except Exception as e:
    print(f"Error creating correlation matrix: {e}")