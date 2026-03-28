# ✈️ Flight Network Analysis

A graph-based analysis of the global flight network using real-world airport and route data. This project models airports as nodes and flight routes as edges, then applies network science techniques to uncover the structure, key hubs, resilience, and seasonal patterns of the global aviation system.

---

## 📌 Overview

This project builds a directed graph of the global flight network and performs multiple layers of analysis:

- **Hub Identification** — Finds the world's most important airports using centrality measures (degree, betweenness, PageRank)
- **Community Detection** — Discovers clusters of airports that are more densely connected to each other than to the rest of the network
- **Resilience Analysis** — Tests how the network holds up when airports or routes are removed
- **Seasonal Patterns** — Compares network structure across summer, fall, winter, and spring flight schedules

---

## 📁 Project Structure

```
789proj/
├── data/
│   ├── airports.csv                  # Raw airport data
│   ├── airports_cleaned.csv          # Cleaned airport data
│   ├── routes.csv                    # Raw routes data
│   ├── routes_cleaned.csv            # Cleaned routes data
│   ├── flight_network.gexf           # Full flight network graph
│   ├── flight_network_summer.gexf    # Seasonal network variants
│   ├── flight_network_fall.gexf
│   ├── flight_network_winter.gexf
│   └── flight_network_spring.gexf
├── results/
│   ├── airport_centrality_measures.csv
│   ├── airport_communities.csv
│   ├── airport_seasonal_metrics.csv
│   ├── degree_distribution.png
│   ├── top10_airports_pagerank.png
│   ├── community_map.html
│   ├── inter_community_heatmap.png
│   ├── network_resilience_visualization.png
│   └── seasonal_network_metrics_plot.png
├── report/
│   └── flight_network_analysis_report.html
├── flight-network-setup.py           # Environment setup
├── flight-network-data-acquisition.py
├── flight-network-creation.py        # Builds the graph
├── flight-network-hub-analysis.py    # Centrality & hub detection
├── flight-network-resilience.py      # Resilience testing
├── flight-network-community.py       # Community detection
├── flight-network-seasonal.py        # Seasonal analysis
├── flight-network-report.py          # Report generation
└── flight-network-main.py            # Master runner script
```

---

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install networkx pandas matplotlib seaborn numpy
```

### 2. Run all analyses in sequence

```bash
python flight-network-main.py
```

You will be prompted to either run all steps or select specific ones.

### 3. View the report

Open `report/flight_network_analysis_report.html` in your browser for the full interactive report.

---

## 🔍 Analysis Modules

| Script | Description |
|--------|-------------|
| `flight-network-data-acquisition.py` | Downloads and prepares raw airport and route data |
| `flight-network-creation.py` | Builds the directed NetworkX graph from cleaned data |
| `flight-network-hub-analysis.py` | Computes degree, betweenness, and PageRank centrality |
| `flight-network-resilience.py` | Simulates node/edge removal and measures network breakdown |
| `flight-network-community.py` | Detects geographic and topological airport communities |
| `flight-network-seasonal.py` | Analyzes how network metrics shift across seasons |
| `flight-network-report.py` | Generates the final HTML report with all visualizations |

---

## 🛠️ Technologies Used

- **Python 3.8+**
- **NetworkX** — Graph construction and analysis
- **Pandas** — Data loading and cleaning
- **Matplotlib / Seaborn** — Visualizations
- **NumPy** — Numerical computations

---

## 📊 Sample Results

- Identified top global hubs by PageRank (e.g. major international airports)
- Detected distinct geographic communities in the flight network
- Measured network resilience under targeted and random airport removal
- Compared seasonal shifts in connectivity and hub importance

---

## 👤 Author

Feel free to reach out or connect on LinkedIn or Gmail if you have questions about this project.
