# Flight Network Analysis - Final Report Generator

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from datetime import datetime

def generate_report():
    """
    Generate a comprehensive report of all flight network analyses
    """
    print("Generating comprehensive flight network analysis report...")
    
    # Check if all required files exist
    required_files = [
        'results/airport_centrality_measures.csv',
        'results/airport_communities.csv',
        'results/community_geography.csv',
        'results/network_resilience_analysis.csv',
        'results/seasonal_network_metrics.csv',
        'results/airport_seasonal_metrics.csv'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("WARNING: Some analysis files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        print("Run the corresponding analysis scripts first.")
    
    # Create report directory
    os.makedirs('report', exist_ok=True)
    
    # Generate HTML report
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flight Network Analysis Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #2980b9;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
                margin-top: 30px;
            }}
            h3 {{
                color: #3498db;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .image-container {{
                margin: 20px 0;
                text-align: center;
            }}
            img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 0 5px rgba(0,0,0,0.1);
            }}
            .footer {{
                margin-top: 50px;
                text-align: center;
                font-size: 12px;
                color: #777;
                border-top: 1px solid #ddd;
                padding-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Flight Network Analysis Report</h1>
            <p>Generated on: {report_date}</p>
            
            <h2>1. Executive Summary</h2>
            <p>This report presents a comprehensive analysis of the global flight network structure, identifying key hubs, community structures, resilience to disruptions, and seasonal patterns in air travel. The analysis leverages graph theory and network science methodologies to uncover insights about the complex interconnections between airports worldwide.</p>
            
            <h2>2. Network Overview</h2>
    """
    
    # Add basic network stats
    try:
        # If we can load the original network structure data, include it
        airports_df = pd.read_csv('data/airports_cleaned.csv')
        routes_df = pd.read_csv('data/routes_cleaned.csv')
        
        html_content += f"""
            <p>The analyzed flight network consists of {len(airports_df)} airports connected by {len(routes_df)} direct flight routes. This network represents the global air transportation infrastructure as captured in the OpenFlights dataset.</p>
            
            <h3>2.1 Network Characteristics</h3>
            <ul>
                <li>Number of airports (nodes): {len(airports_df)}</li>
                <li>Number of routes (edges): {len(routes_df)}</li>
                <li>Network type: Directed (flights have specific origins and destinations)</li>
            </ul>
        """
    except:
        html_content += "<p>Basic network statistics could not be loaded. Please ensure the data processing scripts have been run.</p>"
    
    # Add hub analysis section
    html_content += """
            <h2>3. Hub Analysis</h2>
            <p>Identifying the most important airports (hubs) in the network is crucial for understanding global air travel patterns. Various centrality measures were used to quantify the importance of each airport.</p>
    """
    
    try:
        centrality_df = pd.read_csv('results/airport_centrality_measures.csv')
        
        # Add top airports by PageRank
        top_pagerank = centrality_df.sort_values('PageRank', ascending=False).head(10)
        
        html_content += """
            <h3>3.1 Key Global Hubs (PageRank)</h3>
            <p>PageRank identifies the most influential airports in the network, considering both direct and indirect connections:</p>
            <table>
                <tr>
                    <th>Rank</th>
                    <th>Airport Code</th>
                    <th>Airport Name</th>
                    <th>City</th>
                    <th>Country</th>
                    <th>PageRank Score</th>
                </tr>
        """
        
        for i, row in enumerate(top_pagerank.itertuples()):
            html_content += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{row.Airport}</td>
                    <td>{row.Airport_Name}</td>
                    <td>{row.City}</td>
                    <td>{row.Country}</td>
                    <td>{row.PageRank:.6f}</td>
                </tr>
            """
        
        html_content += "</table>"
        
        # Add top airports by betweenness
        top_betweenness = centrality_df.sort_values('Betweenness Centrality', ascending=False).head(10)
        
        html_content += """
            <h3>3.2 Key Connection Hubs (Betweenness Centrality)</h3>
            <p>Betweenness centrality identifies airports that serve as important bridges or transfer points in the network:</p>
            <table>
                <tr>
                    <th>Rank</th>
                    <th>Airport Code</th>
                    <th>Airport Name</th>
                    <th>City</th>
                    <th>Country</th>
                    <th>Betweenness Score</th>
                </tr>
        """
        
        for i, row in enumerate(top_betweenness.itertuples()):
            html_content += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{row.Airport}</td>
                    <td>{row.Airport_Name}</td>
                    <td>{row.City}</td>
                    <td>{row.Country}</td>
                    <td>{row.Betweenness_Centrality:.6f}</td>
                </tr>
            """
        
        html_content += "</table>"
        
        # Add visualization
        if os.path.exists('results/top10_airports_pagerank.png'):
            html_content += """
                <div class="image-container">
                    <img src="../results/top10_airports_pagerank.png" alt="Top 10 Airports by PageRank">
                    <p>Figure 1: Top 10 global airports ranked by PageRank centrality</p>
                </div>
            """
    except:
        html_content += "<p>Hub analysis data could not be loaded. Please run the hub analysis script first.</p>"
    
    # Add community detection section
    html_content += """
            <h2>4. Community Structure</h2>
            <p>Network communities represent groups of airports that are more densely connected to each other than to the rest of the network. These communities often align with geographical regions, airline alliances, or hub-and-spoke systems.</p>
    """
    
    try:
        community_geo_df = pd.read_csv('results/community_geography.csv')
        
        html_content += f"""
            <h3>4.1 Identified Communities</h3>
            <p>The analysis identified {len(community_geo_df)} distinct communities in the flight network. The largest communities are:</p>
            <table>
                <tr>
                    <th>Community ID</th>
                    <th>Number of Airports</th>
                    <th>Main Countries</th>
                    <th>Geographic Center</th>
                </tr>
        """
        
        for i, row in enumerate(community_geo_df.sort_values('num_airports', ascending=False).head(10).itertuples()):
            countries = eval(row.main_countries) if isinstance(row.main_countries, str) else row.main_countries
            countries_str = ", ".join(countries[:3]) if countries else "N/A"
            
            html_content += f"""
                <tr>
                    <td>{row.community_id}</td>
                    <td>{row.num_airports}</td>
                    <td>{countries_str}</td>
                    <td>({row.center_lat:.2f}, {row.center_lon:.2f})</td>
                </tr>
            """
        
        html_content += "</table>"
        
        # Add community map if available
        if os.path.exists('results/community_map.html'):
            html_content += """
                <h3>4.2 Community Map</h3>
                <p>An interactive map of the communities is available in the results folder (community_map.html). The map shows the geographical distribution of each community with color coding.</p>
            """
        
        # Add inter-community connections if available
        if os.path.exists('results/inter_community_heatmap.png'):
            html_content += """
                <h3>4.3 Inter-Community Connections</h3>
                <div class="image-container">
                    <img src="../results/inter_community_heatmap.png" alt="Inter-Community Connections">
                    <p>Figure 2: Heat map showing flight connections between top communities</p>
                </div>
            """
    except:
        html_content += "<p>Community analysis data could not be loaded. Please run the community detection script first.</p>"
    
    # Add network resilience section
    html_content += """
            <h2>5. Network Resilience</h2>
            <p>This section analyzes how the flight network responds to disruptions, such as airport closures. Understanding network resilience is crucial for identifying vulnerabilities and improving the robustness of the air transportation system.</p>
    """
    
    try:
        if os.path.exists('results/network_resilience_visualization.png'):
            html_content += """
                <h3>5.1 Impact of Airport Removals</h3>
                <div class="image-container">
                    <img src="../results/network_resilience_visualization.png" alt="Network Resilience Analysis">
                    <p>Figure 3: Impact of airport removals on network connectivity</p>
                </div>
                <p>The graph shows how the network's connectivity deteriorates as airports are removed according to different strategies. Targeting airports with high centrality measures causes more rapid fragmentation of the network compared to random removals.</p>
            """
        
        if os.path.exists('results/critical_threshold_analysis.png'):
            html_content += """
                <h3>5.2 Critical Thresholds</h3>
                <div class="image-container">
                    <img src="../results/critical_threshold_analysis.png" alt="Critical Threshold Analysis">
                    <p>Figure 4: Critical thresholds for network fragmentation</p>
                </div>
                <p>The critical threshold represents the percentage of airports that need to be removed before the network's largest connected component drops below 50% of its original size. Lower values indicate greater vulnerability to that attack strategy.</p>
            """
    except:
        html_content += "<p>Resilience analysis data could not be loaded. Please run the resilience analysis script first.</p>"
    
    # Add seasonal analysis section
    html_content += """
            <h2>6. Seasonal Patterns</h2>
            <p>Flight networks exhibit seasonal variations due to tourism, weather, holidays, and other factors. This section examines how the network structure changes across seasons.</p>
    """
    
    try:
        seasonal_metrics = pd.read_csv('results/seasonal_network_metrics.csv')
        
        html_content += """
            <h3>6.1 Network-Level Seasonal Metrics</h3>
            <table>
                <tr>
                    <th>Season</th>
                    <th>Number of Flights</th>
                    <th>Average Flights per Airport</th>
                    <th>Network Density</th>
                </tr>
        """
        
        for _, row in seasonal_metrics.iterrows():
            html_content += f"""
                <tr>
                    <td>{row.Season}</td>
                    <td>{row['Number of Flights (Edges)']:.0f}</td>
                    <td>{row['Average Flights per Airport']:.2f}</td>
                    <td>{row['Network Density']:.6f}</td>
                </tr>
            """
        
        html_content += "</table>"
        
        if os.path.exists('results/seasonal_network_metrics_plot.png'):
            html_content += """
                <div class="image-container">
                    <img src="../results/seasonal_network_metrics_plot.png" alt="Seasonal Network Metrics">
                    <p>Figure 5: Seasonal variations in network metrics</p>
                </div>
            """
        
        if os.path.exists('results/top_seasonal_airports.png'):
            html_content += """
                <h3>6.2 Airports with Highest Seasonal Variation</h3>
                <div class="image-container">
                    <img src="../results/top_seasonal_airports.png" alt="Top Seasonal Airports">
                    <p>Figure 6: Airports with the highest seasonal variation in connections</p>
                </div>
                <p>These airports show significant changes in connectivity across seasons, likely due to tourism patterns, weather conditions, or other seasonal factors.</p>
            """
        
        # Add top seasonal airports if available
        try:
            airport_seasonal = pd.read_csv('results/airport_seasonal_metrics.csv')
            top_seasonal = airport_seasonal.sort_values('Seasonal Variation', ascending=False).head(10)
            
            html_content += """
                <h3>6.3 Top 10 Airports with Highest Seasonal Variation</h3>
                <table>
                    <tr>
                        <th>Airport</th>
                        <th>IATA Code</th>
                        <th>Winter</th>
                        <th>Spring</th>
                        <th>Summer</th>
                        <th>Fall</th>
                        <th>Seasonal Variation</th>
                        <th>Summer/Winter Ratio</th>
                    </tr>
            """
            
            for _, row in top_seasonal.iterrows():
                html_content += f"""
                    <tr>
                        <td>{row.Airport}</td>
                        <td>{row.IATA}</td>
                        <td>{row.Winter}</td>
                        <td>{row.Spring}</td>
                        <td>{row.Summer}</td>
                        <td>{row.Fall}</td>
                        <td>{row['Seasonal Variation']:.2f}</td>
                        <td>{row['Summer/Winter Ratio']:.2f}</td>
                    </tr>
                """
            
            html_content += "</table>"
        except:
            pass
            
    except:
        html_content += "<p>Seasonal analysis data could not be loaded. Please run the seasonal analysis script first.</p>"
    
    # Add conclusions
    html_content += """
            <h2>7. Conclusions and Recommendations</h2>
            
            <h3>7.1 Key Findings</h3>
            <ul>
                <li>The global flight network exhibits a scale-free structure, with a small number of major hubs handling a disproportionate amount of traffic.</li>
                <li>Network communities largely correspond to geographic regions, with some transcontinental communities formed around major airline alliances.</li>
                <li>The network shows vulnerability to targeted disruptions of central hubs, while being relatively resilient to random airport closures.</li>
                <li>Seasonal variations are significant for specific tourism-oriented airports and regions with extreme weather conditions.</li>
            </ul>
            
            <h3>7.2 Recommendations</h3>
            <ul>
                <li><strong>For Airlines:</strong> Optimize hub-and-spoke systems based on identified community structures. Consider seasonal adjustments to route offerings based on the observed patterns.</li>
                <li><strong>For Airports:</strong> Smaller airports could improve connectivity by establishing routes to regional hubs rather than trying to connect to distant major hubs.</li>
                <li><strong>For Regulators:</strong> Implement policies to reduce network vulnerability by encouraging more distributed connectivity rather than concentration around a few mega-hubs.</li>
                <li><strong>For Future Research:</strong> Incorporate passenger flow data to weight the network edges, providing a more accurate representation of the importance of each route.</li>
            </ul>
            
            <div class="footer">
                <p>Flight Network Analysis Project Report | Generated on {report_date}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML report
    with open('report/flight_network_analysis_report.html', 'w') as f:
        f.write(html_content)
    
    print("Comprehensive report generated: report/flight_network_analysis_report.html")

# Generate the report
generate_report()