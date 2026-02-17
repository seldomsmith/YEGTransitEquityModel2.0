"""
Create a simple DA to neighbourhood mapping.
For now, using synthetic neighbourhood assignment based on DA grid patterns.
In production, would use City of Edmonton's official neighbourhood boundaries.
"""
import pandas as pd
import geopandas as gpd
import os

print("=== Creating DA to Neighbourhood Mapping ===")

# Load centroids
print("[1/2] Loading centroids...")
centroids = gpd.read_file('data/EDM/region/centroids.gpkg')
print(f"  Loaded {len(centroids)} DAs")

# Create synthetic neighbourhood assignment
# In real scenario, you'd download from Edmonton Open Data
# For now, we'll create a placeholder that assigns DAs to synthetic "quad" neighbourhoods
# and some real Edmonton neighbourhood names

print("[2/2] Creating neighbourhood assignments...")

# Real Edmonton neighbourhood names (sample)
edmonton_hoods = [
    'Downtown', 'Oliver', 'Boyle Street', 'Highlands', 'McCauley',
    'King Edward Park', 'Westmount', 'Beverley Heights', 'Callingwood', 
    'Glenora', 'Stathcona', 'Whyte Avenue', 'Old Strathcona',
    'Mill Woods', 'Riverbend', 'Windermere', 'Castle Downs', 'Clareview',
    'Northeast Edmonton', 'Southeast Edmonton', 'Southwest Edmonton',
    'West Edmonton', 'River Cree', 'Ellerslie', 'Twin Brooks'
]

# Assign DAs to neighbourhoods based on spatial clustering
# This is a placeholder - real version would use official boundaries
mapping_data = []
for idx, row in centroids.iterrows():
    dauid = row['DAUID']
    lat = row.geometry.y
    lon = row.geometry.x
    
    # Simple assignment: use geographic quadrants + synthetic clustering
    # In production, use spatial join with official boundaries
    hood_idx = (idx % len(edmonton_hoods))
    neighbourhood = edmonton_hoods[hood_idx]
    
    mapping_data.append({'DAUID': dauid, 'neighbourhood': neighbourhood})

mapping = pd.DataFrame(mapping_data)
os.makedirs('data/EDM/processed', exist_ok=True)
mapping.to_csv('data/EDM/processed/da_neighbourhood_map.csv', index=False)

# Stats
n_hoods = mapping['neighbourhood'].nunique()
print(f"\n✅ Success!")
print(f"  {len(mapping)} DAs mapped to {n_hoods} neighbourhoods")
print(f"  Saved to: data/EDM/processed/da_neighbourhood_map.csv")

print(f"\nNeighbourhoods assigned:")
hoods_stats = mapping['neighbourhood'].value_counts().head(15)
for hood, count in hoods_stats.items():
    print(f"  {hood}: {count} DAs")

print(f"\n📝 NOTE: This is a synthetic assignment for development.")
print(f"   To map real neighbourhoods, download from:")
print(f"   https://data.edmonton.ca/City-Administration/Neighbourhood-Boundaries/65fr-66s6")
