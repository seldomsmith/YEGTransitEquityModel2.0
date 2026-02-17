
import os
import geopandas as gpd
import pandas as pd
import shutil

# Configuration
RAW_DIR = "data/EDM/raw"
REGION_DIR = "data/EDM/region"
BOUNDARIES_SHP = os.path.join(REGION_DIR, "statscan_boundaries", "lda_000b21a_e.shp")
DEMOGRAPHICS_CSV = os.path.join(RAW_DIR, "demographics.csv")
OUTPUT_REGION_GPKG = os.path.join(REGION_DIR, "region.gpkg")
OUTPUT_CENTROIDS_GPKG = os.path.join(REGION_DIR, "centroids.gpkg")

def process_region():
    print("Loading Demographics to get list of Edmonton DAs...")
    try:
        demo_df = pd.read_csv(DEMOGRAPHICS_CSV)
        # Ensure DAUID is string to match shapefile
        target_das = demo_df['DAUID'].astype(str).tolist()
        print(f"Found {len(target_das)} target DAs in demographics file.")
    except Exception as e:
        print(f"Error reading demographics: {e}")
        return

    print("Loading Statistics Canada Boundary File (this may take a moment)...")
    try:
        # Read the shapefile
        # Note: DAUID in StatCan file is often named 'DAUID'
        gdf = gpd.read_file(BOUNDARIES_SHP)
        print(f"Loaded {len(gdf)} total boundaries.")
        
        # Filter
        print("Filtering for Edmonton DAs...")
        # StatCan DAUIDs might be in a column named 'DAUID' or similar
        edmonton_gdf = gdf[gdf['DAUID'].isin(target_das)].copy()
        
        if len(edmonton_gdf) == 0:
            print("WARNING: No matching DAs found! Check ID formats.")
            print(f"Sample CSV IDs: {target_das[:5]}")
            print(f"Sample Shapefile IDs: {gdf['DAUID'].head().tolist()}")
            return

        print(f"Filtered to {len(edmonton_gdf)} features.")

        # Reproject to standard lat/lon (EPSG:4326) if needed
        if edmonton_gdf.crs.to_string() != "EPSG:4326":
            print("Reprojecting to EPSG:4326...")
            edmonton_gdf = edmonton_gdf.to_crs("EPSG:4326")

        # Save Region Boundaries
        print(f"Saving region boundaries to {OUTPUT_REGION_GPKG}...")
        edmonton_gdf.to_file(OUTPUT_REGION_GPKG, driver="GPKG")

        # Calculate and Save Centroids
        print("Calculating centroids...")
        # Project to a meter-based Query CRS for accurate centroids, then back to 4326
        # Using EPSG:3400 (Alberta 10-TM Forest) as a decent local metric projection
        centroids = edmonton_gdf.to_crs("EPSG:3400").centroid.to_crs("EPSG:4326")
        
        # Create a GDF for centroids with the same ID
        centroids_gdf = gpd.GeoDataFrame(
            {"DAUID": edmonton_gdf["DAUID"]}, 
            geometry=centroids,
            crs="EPSG:4326"
        )
        
        print(f"Saving centroids to {OUTPUT_CENTROIDS_GPKG}...")
        centroids_gdf.to_file(OUTPUT_CENTROIDS_GPKG, driver="GPKG")
        
        print("✅ Processing Complete!")

    except Exception as e:
        print(f"❌ Error processing spatial data: {e}")

if __name__ == "__main__":
    process_region()
