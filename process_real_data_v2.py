import zipfile
import pandas as pd
import geopandas as gpd
import os

print("=== Edmonton Real Data Integration (Reverse Lookup) ===")

# 1. Process Demographics FIRST to find Edmonton DAs
print("Scanning Demographics for Edmonton DAs...")
target_das = []

# We'll stream the CSV looking for rows that belong to Edmonton CMA (Code 835)
# Note: The CSV structure is complex. We need to find DAs that are 'children' of Edmonton CMA.
# SIMPLIFICATION: Edmonton DAUIDs start with "4811" (Province 48, Division 11).
# Division 11 is "Greater Edmonton". This is a very safe shortcut.
print("Filtering for DAs starting with '4811' (Greater Edmonton)...")

with zipfile.ZipFile('lda_000b21a_e.zip', 'r') as z:
    z.extractall('data/EDM/region/temp_shapes')

gdf = gpd.read_file('data/EDM/region/temp_shapes/lda_000b21a_e.shp')

# Filter by DAUID string prefix
# 48 = Alberta, 11 = Division (Edmonton area)
edmonton_boundaries = gdf[gdf['DAUID'].astype(str).str.startswith('4811')].copy()

print(f"✅ Found {len(edmonton_boundaries)} Edmonton-area neighbourhoods!")

# Save the boundaries
os.makedirs('data/EDM/region', exist_ok=True)
edmonton_boundaries.to_crs("EPSG:4326").to_file('data/EDM/region/region.gpkg', driver='GPKG')

# Calculate Centroids
centroids = edmonton_boundaries.to_crs("EPSG:3400").centroid.to_crs("EPSG:4326")
centroids_gdf = gpd.GeoDataFrame({"DAUID": edmonton_boundaries["DAUID"]}, geometry=centroids, crs="EPSG:4326")
centroids_gdf.to_file('data/EDM/region/centroids.gpkg', driver='GPKG')

# 2. Process Demographics (Prairies CSV) based on these IDs
print("\nProcessing Demographics for these DAs...")
target_ids = edmonton_boundaries['DAUID'].tolist()

# Load the CSV
with zipfile.ZipFile('98-401-X2021006_Prairies_eng_CSV.zip', 'r') as z:
    csv_name = [f for f in z.namelist() if 'data' in f.lower() and f.endswith('.csv')][0]
    
    chunks = []
    # Read in chunks
    for chunk in pd.read_csv(z.open(csv_name), chunksize=50000, encoding='latin1', dtype={'ALT_GEO_CODE': str}):
        # Keep only our target DAs
        filtered = chunk[chunk['ALT_GEO_CODE'].isin(target_ids)]
        if not filtered.empty:
            chunks.append(filtered)

full_demo = pd.concat(chunks)

# Target Characteristics (The IDs for Total Pop, Low Income, etc.)
# We'll pivot using the descriptions for now
pivot = full_demo.pivot_table(index='ALT_GEO_CODE', columns='CHARACTERISTIC_NAME', values='C1_COUNT_TOTAL', aggfunc='first')
pivot.index.name = 'DAUID'
pivot.to_csv('data/EDM/raw/demographics.csv')
print(f"✅ Real Demographics saved for {len(pivot)} DAs")

