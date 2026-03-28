# Flight Network Analysis - Environment Setup
# Install required packages
# pip install networkx pandas matplotlib plotly folium geopandas

# Import libraries
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import folium
from datetime import datetime
import seaborn as sns
import os

# Set plot aesthetics
plt.style.use('ggplot')
sns.set_palette("Set2")

# Create directories for data and results
os.makedirs('data', exist_ok=True)
os.makedirs('results', exist_ok=True)

print("Environment setup complete!")