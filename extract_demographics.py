import zipfile
import pandas as pd
import geopandas as gpd
import os

print("=== Extracting Real Demographics for Edmonton ===")
print("Loading DA list...")

# 1. Load the REAL Edmonton IDs from the region file we made
try:
    gdf = gpd.read_file('data/EDM/region/region.gpkg')
    target_das = set(gdf['DAUID'].astype(str))
    print(f"Targeting {len(target_das)} neighbourhoods.")
except Exception as e:
    print(f"Error loading region file: {e}")
    exit(1)

# 2. Define the exact StatsCan variables we need
TARGET_VARS = {
    "Population, 2021": "total_pop",
    "In low income based on the Low-income measure, after tax (LIM-AT)": "low_income",
    "Total visible minority population": "minority",
    "Total - Lone-parent census families in private households": "single_parent",
    "65 years and over": "seniors"
}

# 3. Stream the massive CSV
print("Scanning 400MB Census file... (this takes ~30s)")
data_rows = []

zip_file = '98-401-X2021006_Prairies_eng_CSV.zip'
if not os.path.exists(zip_file):
    print("Error: Zip file not found!")
    exit(1)

with zipfile.ZipFile(zip_file, 'r') as z:
    # Find CSV inside
    csv_name = [f for f in z.namelist() if f.endswith('.csv') and '98-401' in f][0]
    
    # Read in chunks
    with z.open(csv_name) as f:
        # Use dtype to keep IDs as strings (crucial!)
        for chunk in pd.read_csv(f, chunksize=50000, encoding='latin1', dtype={'ALT_GEO_CODE': str}):
            
            # Filter 1: Is it an Edmonton DA?
            chunk = chunk[chunk['ALT_GEO_CODE'].isin(target_das)]
            
            if not chunk.empty:
                # Filter 2: Is it a variable we want?
                mask = chunk['CHARACTERISTIC_NAME'].apply(
                    lambda x: any(k in str(x) for k in TARGET_VARS.keys())
                )
                relevant = chunk[mask].copy()
                
                if not relevant.empty:
                    # Map the long StatsCan name to our short name
                    relevant['mapped_var'] = relevant['CHARACTERISTIC_NAME'].apply(
                        lambda x: next((v for k, v in TARGET_VARS.items() if k in str(x)), None)
                    )
                    
                    # Keep just ID, Variable, and Count
                    cols = relevant[['ALT_GEO_CODE', 'mapped_var', 'C1_COUNT_TOTAL']]
                    data_rows.append(cols)

# 4. Assemble
if not data_rows:
    print("❌ Error: No matching data found! Check DA IDs." )
    exit(1)

full_df = pd.concat(data_rows)

# Pivot (DAs as rows, variables as columns)
final_demo = full_df.pivot_table(
    index='ALT_GEO_CODE', 
    columns='mapped_var', 
    values='C1_COUNT_TOTAL', 
    aggfunc='first'
).fillna(0).astype(int)

# Rename index to match our pipeline
final_demo.index.name = 'DAUID'
final_demo.reset_index(inplace=True)

# 5. Save
output_path = 'data/EDM/raw/demographics.csv'
final_demo.to_csv(output_path, index=False)
print(f"✅ Success! Saved real data for {len(final_demo)} neighbourhoods.")
print(final_demo.head())
