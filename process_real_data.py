import zipfile
import pandas as pd
import geopandas as gpd
import os
import io

print("=== Edmonton Real Data Integration ===")

# 1. Process Boundaries (DA shapes)
print("Processing Boundaries (lda_000b21a_e.zip)...")
with zipfile.ZipFile('lda_000b21a_e.zip', 'r') as z:
    z.extractall('data/EDM/region/temp_shapes')

# Load the shapes (Alberta PRUID is 48, Edmonton CMAUID is 835)
gdf = gpd.read_file('data/EDM/region/temp_shapes')
# Filter for Edmonton Census Metropolitan Area (CMAUID = 835)
edmonton_boundaries = gdf[gdf['CMAUID'] == '835'].copy()

# Save real boundaries and centroids
os.makedirs('data/EDM/region', exist_ok=True)
edmonton_boundaries.to_crs("EPSG:4326").to_file('data/EDM/region/region.gpkg', driver='GPKG')
centroids = edmonton_boundaries.to_crs("EPSG:3400").centroid.to_crs("EPSG:4326")
centroids_gdf = gpd.GeoDataFrame({"DAUID": edmonton_boundaries["DAUID"]}, geometry=centroids, crs="EPSG:4326")
centroids_gdf.to_file('data/EDM/region/centroids.gpkg', driver='GPKG')
print(f"✅ Extracted {len(edmonton_boundaries)} real Edmonton neighbourhoods!")

# 2. Process Demographics (Prairies CSV)
print("\nProcessing Demographics (98-401-X2021006_Prairies_eng_CSV.zip)...")
# We only need specific target IDs (Edmonton DAs)
target_das = edmonton_boundaries['DAUID'].tolist()

with zipfile.ZipFile('98-401-X2021006_Prairies_eng_CSV.zip', 'r') as z:
    # Find the data file inside
    csv_name = [f for f in z.namelist() if 'data' in f.lower() and f.endswith('.csv')][0]
    
    # We read in chunks to save memory
    relevant_data = []
    for chunk in pd.read_csv(z.open(csv_name), chunksize=50000, encoding='latin1', dtype={'ALT_GEO_CODE': str}):
        # Filter for DAs in our Edmonton list
        # Note: StatsCan column is usually 'ALT_GEO_CODE' for the 8-digit ID
        matches = chunk[chunk['ALT_GEO_CODE'].isin(target_das)]
        if not matches.empty:
            relevant_data.append(matches)

full_demo = pd.concat(relevant_data)

# Simplify the data into the format our dashboard needs
# (This is a simplified mapping - we'll refine it, but it gets the totals)
pivot = full_demo.pivot_table(index='ALT_GEO_CODE', columns='CHARACTERISTIC_NAME', values='C1_COUNT_TOTAL', aggfunc='first')
pivot.index.name = 'DAUID'
pivot.to_csv('data/EDM/raw/demographics.csv')
print("✅ Real Demographics saved to data/EDM/raw/demographics.csv")
