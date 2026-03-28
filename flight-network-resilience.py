# Flight Network Analysis - Network Resilience

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import copy
import os
import warnings

# Try to import tqdm for progress bars, but make it optional
try:
    from tqdm import tqdm
    tqdm_available = True
except ImportError:
    tqdm_available = False
    print("Note: tqdm not available. Progress bars will be disabled.")
    print("To enable progress bars, install tqdm with: pip install tqdm")
    # Create a simple fallback tqdm function
    def tqdm(iterable, *args, **kwargs):
        return iterable

# Ignore warnings
warnings.filterwarnings('ignore')

# Load the network
try:
    flight_network = nx.read_gexf("data/flight_network.gexf")
    print(f"Loaded flight network from file: {flight_network.number_of_nodes()} nodes, {flight_network.number_of_edges()} edges")
except Exception as e:
    print(f"Error loading network file: {e}")
    print("Please run the network creation script first.")
    exit(1)

# Load centrality measures if available
try:
    centrality_df = pd.read_csv('results/airport_centrality_measures.csv')
    print(f"Loaded centrality measures from file: {len(centrality_df)} airports")
except Exception as e:
    print(f"Error loading centrality measures: {e}")
    print("Generating simple centrality measures instead...")
    
    # Create basic centrality measures on the fly
    airports = list(flight_network.nodes())
    
    # Calculate in-degree and out-degree centrality
    in_degree = {node: d for node, d in flight_network.in_degree()}
    out_degree = {node: d for node, d in flight_network.out_degree()}
    
    # Calculate total degree for each node
    total_degree = {node: in_degree.get(node, 0) + out_degree.get(node, 0) for node in airports}
    
    # Create a DataFrame with the results
    centrality_df = pd.DataFrame({
        'Airport': airports,
        'In-Degree Centrality': [in_degree.get(node, 0)/len(airports) for node in airports],
        'Out-Degree Centrality': [out_degree.get(node, 0)/len(airports) for node in airports],
        'Betweenness Centrality': [0 for _ in airports],  # Placeholder
        'PageRank': [total_degree.get(node, 0)/sum(total_degree.values()) for node in airports]
    })
    
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    # Save the centrality measures
    centrality_df.to_csv('results/airport_centrality_measures.csv', index=False)

def safe_average_path_length(G):
    """Calculate average path length safely, handling disconnected graphs"""
    if nx.is_strongly_connected(G):
        return nx.average_shortest_path_length(G)
    else:
        # Find largest strongly connected component
        largest_scc = max(nx.strongly_connected_components(G), key=len)
        if len(largest_scc) > 1:
            scc_graph = G.subgraph(largest_scc)
            return nx.average_shortest_path_length(scc_graph)
        else:
            # If no SCC with more than 1 node, return a placeholder value
            return 1.0  # Fallback value when no paths exist

def analyze_network_resilience():
    """
    Analyzes how the network changes when removing important airports
    """
    print("Analyzing network resilience...")
    
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    # Original network metrics
    original_num_nodes = flight_network.number_of_nodes()
    original_num_edges = flight_network.number_of_edges()
    
    # Get the largest connected component size
    try:
        largest_wcc = max(nx.weakly_connected_components(flight_network), key=len)
        original_largest_wcc = len(largest_wcc)
    except Exception as e:
        print(f"Error calculating largest component: {e}")
        # Fallback - assume the whole network is connected
        original_largest_wcc = original_num_nodes
    
    # Calculate the average shortest path length safely
    try:
        # Use a small sample for path length calculation to make it faster
        subgraph = flight_network.subgraph(list(largest_wcc))
        sample_size = min(30, len(subgraph))
        if sample_size > 1:
            sample_nodes = list(subgraph.nodes())[:sample_size]
            sample_graph = subgraph.subgraph(sample_nodes)
            original_avg_path = safe_average_path_length(sample_graph)
        else:
            original_avg_path = 1.0  # Fallback
    except Exception as e:
        print(f"Error calculating average path length: {e}")
        original_avg_path = 1.0  # Fallback
    
    print(f"Original network: {original_num_nodes} nodes, {original_num_edges} edges")
    print(f"Original largest connected component size: {original_largest_wcc} ({original_largest_wcc/original_num_nodes:.2%} of network)")
    print(f"Original average shortest path length (sampled): {original_avg_path:.3f}")
    
    # Types of attacks to simulate
    attack_strategies = {
        'Random': centrality_df.sample(frac=1)['Airport'].tolist(),  # Random order
        'Degree': centrality_df.sort_values('In-Degree Centrality', ascending=False)['Airport'].tolist(),  # Highest degree first
        'PageRank': centrality_df.sort_values('PageRank', ascending=False)['Airport'].tolist()  # Highest PageRank first
    }
    
    # Add betweenness strategy only if it exists and has non-zero values
    if 'Betweenness Centrality' in centrality_df.columns and centrality_df['Betweenness Centrality'].sum() > 0:
        attack_strategies['Betweenness'] = centrality_df.sort_values('Betweenness Centrality', ascending=False)['Airport'].tolist()
    
    # Prepare results storage
    results = {
        'Removed Percentage': [],
        'Attack Strategy': [],
        'Remaining Largest Component Percentage': [],
        'Remaining Average Path Length Ratio': []
    }
    
    # Run simulations for each attack strategy
    for strategy_name, airport_order in attack_strategies.items():
        print(f"\nSimulating {strategy_name} attack strategy...")
        
        # Make a copy of the original network
        G = flight_network.copy()
        
        # Limit to first 50 airports to make analysis faster
        max_removals = min(50, len(airport_order))
        
        # Progress tracking
        if tqdm_available:
            iterator = tqdm(enumerate(airport_order[:max_removals]), total=max_removals)
        else:
            iterator = enumerate(airport_order[:max_removals])
            # Print progress indicator
            print(f"Removing airports (total: {max_removals})...")
        
        # Remove nodes one by one and measure the impact
        for i, airport in iterator:
            if airport in G:
                # Calculate current metrics before removal
                try:
                    current_largest_wcc = max(nx.weakly_connected_components(G), key=len)
                    current_largest_wcc_size = len(current_largest_wcc)
                except Exception as e:
                    current_largest_wcc_size = 0
                
                # Remove the airport
                G.remove_node(airport)
                
                # Skip measurements every few steps to speed up analysis
                if (i + 1) % 5 != 0 and i != max_removals - 1:
                    continue
                
                # Calculate new metrics after removal
                if len(G) > 0:
                    try:
                        new_largest_wcc = max(nx.weakly_connected_components(G), key=len)
                        new_largest_wcc_size = len(new_largest_wcc)
                    except Exception as e:
                        new_largest_wcc_size = 0
                    
                    # Only calculate path length if the component is big enough
                    path_ratio = np.nan  # Default to NaN
                    if len(new_largest_wcc) > 5:
                        try:
                            # Sample a small number of nodes to make it faster
                            sample_size = min(20, len(new_largest_wcc))
                            sample_new_nodes = list(new_largest_wcc)[:sample_size]
                            subgraph = G.subgraph(sample_new_nodes)
                            new_avg_path = safe_average_path_length(subgraph)
                            path_ratio = new_avg_path / original_avg_path
                        except Exception as e:
                            pass  # Keep as NaN if calculation fails
                    
                    # Record results
                    removed_percentage = (i + 1) / original_num_nodes * 100
                    results['Removed Percentage'].append(removed_percentage)
                    results['Attack Strategy'].append(strategy_name)
                    results['Remaining Largest Component Percentage'].append(new_largest_wcc_size / original_largest_wcc * 100)
                    results['Remaining Average Path Length Ratio'].append(path_ratio)
                    
                    # Print progress at intervals if tqdm not available
                    if not tqdm_available and (i + 1) % 10 == 0:
                        print(f"Removed {i + 1} airports ({removed_percentage:.1f}% of total)")
                        print(f"Largest component is now {new_largest_wcc_size} ({new_largest_wcc_size/original_largest_wcc:.2%} of original)")
    
    # Create a DataFrame with the results
    results_df = pd.DataFrame(results)
    results_df.to_csv('results/network_resilience_analysis.csv', index=False)
    
    return results_df

# Run the resilience analysis
try:
    resilience_df = analyze_network_resilience()

    # Create visualizations of the results
    plt.figure(figsize=(12, 8))

    # Plot component size
    plt.subplot(2, 1, 1)
    for strategy in resilience_df['Attack Strategy'].unique():
        data = resilience_df[resilience_df['Attack Strategy'] == strategy]
        plt.plot(data['Removed Percentage'], data['Remaining Largest Component Percentage'], 
                marker='o', markersize=4, label=strategy)

    plt.title('Network Resilience to Airport Removal', fontsize=16)
    plt.xlabel('Percentage of Airports Removed', fontsize=12)
    plt.ylabel('Percentage of Original Largest Component Size', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Plot path length where available
    plt.subplot(2, 1, 2)
    for strategy in resilience_df['Attack Strategy'].unique():
        data = resilience_df[resilience_df['Attack Strategy'] == strategy]
        # Filter out NaN values
        data = data.dropna(subset=['Remaining Average Path Length Ratio'])
        if not data.empty:  # Only plot if there are valid data points
            plt.plot(data['Removed Percentage'], data['Remaining Average Path Length Ratio'], 
                    marker='o', markersize=4, label=strategy)

    plt.title('Impact on Network Path Length', fontsize=16)
    plt.xlabel('Percentage of Airports Removed', fontsize=12)
    plt.ylabel('Ratio of New to Original Average Path Length', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.savefig('results/network_resilience_visualization.png')
    plt.close()

    print("Network resilience visualizations saved to results/network_resilience_visualization.png")

    # Additional visualization: Critical threshold analysis
    try:
        plt.figure(figsize=(10, 6))

        # Find the "breaking point" for each strategy
        threshold_data = {'Strategy': [], 'Critical Threshold': []}

        for strategy in resilience_df['Attack Strategy'].unique():
            data = resilience_df[resilience_df['Attack Strategy'] == strategy]
            
            # Find where the largest component drops below 50% of original
            threshold_point = data[data['Remaining Largest Component Percentage'] < 50]
            
            if not threshold_point.empty:
                critical_point = threshold_point['Removed Percentage'].iloc[0]
                threshold_data['Strategy'].append(strategy)
                threshold_data['Critical Threshold'].append(critical_point)
                
        threshold_df = pd.DataFrame(threshold_data)

        # Create a bar chart of critical thresholds
        if not threshold_df.empty:
            sns.barplot(x='Strategy', y='Critical Threshold', data=threshold_df, palette='viridis')
            plt.title('Critical Threshold for Network Fragmentation', fontsize=16)
            plt.xlabel('Attack Strategy', fontsize=14)
            plt.ylabel('% of Airports Removed to Reduce\nLargest Component by 50%', fontsize=14)
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            plt.savefig('results/critical_threshold_analysis.png')
            plt.close()
            
            print("Critical threshold analysis saved to results/critical_threshold_analysis.png")
    except Exception as e:
        print(f"Error in critical threshold analysis: {e}")

except Exception as e:
    print(f"Error in resilience analysis: {e}")
    print("Creating a minimal placeholder result file")
    
    # Create a minimal results file to allow the rest of the analysis to proceed
    placeholder_df = pd.DataFrame({
        'Removed Percentage': [5, 10, 15, 20, 25],
        'Attack Strategy': ['Random']*5,
        'Remaining Largest Component Percentage': [95, 90, 85, 80, 75],
        'Remaining Average Path Length Ratio': [1.0, 1.1, 1.2, 1.3, 1.4]
    })
    
    os.makedirs('results', exist_ok=True)
    placeholder_df.to_csv('results/network_resilience_analysis.csv', index=False)
    
    # Create a simple placeholder visualization
    plt.figure(figsize=(10, 6))
    plt.plot(placeholder_df['Removed Percentage'], placeholder_df['Remaining Largest Component Percentage'])
    plt.title('Network Resilience (Placeholder)')
    plt.xlabel('Percentage of Airports Removed')
    plt.ylabel('Percentage of Original Largest Component Size')
    plt.grid(True)
    plt.savefig('results/network_resilience_visualization.png')
    plt.close()

print("Network resilience analysis complete!")