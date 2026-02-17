import geopandas as gpd
import pandas as pd
import yaml
import os
import datetime
print("============================================================")
print("Edmonton TED Pipeline Test")
print("============================================================")
print("\n[1/6] Importing core libraries...")
print("  OK - geopandas, pandas, yaml imported")
print("\n[2/6] Loading Edmonton config...")
config_path = 'configs/edmonton.yaml'
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    print(f"  OK - Region: {config.get('region_name', 'Unknown')}")
else:
    print(f"  WARN - Config not found, using defaults")
print("\n[3/6] Loading region boundaries...")
region = gpd.read_file('data/EDM/region/region.gpkg')
print(f"  OK - {len(region)} dissemination areas loaded")
print(f"  CRS: {region.crs}")
print("\n[4/6] Loading centroids...")
centroids = gpd.read_file('data/EDM/region/centroids.gpkg')
centroids['id'] = centroids['DAUID']
print(f"  OK - {len(centroids)} centroid points loaded")
print(f"  Sample DAUIDs: {centroids['DAUID'].head().tolist()}")
print("\n[5/6] Loading demographics...")
demo = pd.read_csv('data/EDM/raw/demographics.csv')
print(f"  OK - {len(demo)} rows, columns: {demo.columns.tolist()}")
if 'total_pop' in demo.columns:
    print(f"  Total Population: {demo['total_pop'].sum():,}")
print("\n[6/6] Testing transport network build...")
try:
    from r5py import TransportNetwork, TravelTimeMatrix
    gtfs_path = 'data/EDM/gtfs'
    gtfs_files = [os.path.join(gtfs_path, f) for f in os.listdir(gtfs_path) if f.endswith('.zip')]
    osm_file = 'data/EDM/osm/edmonton.osm.pbf'
    print(f"  Found {len(gtfs_files)} GTFS file(s)")
    print(f"  OSM file: {osm_file}")
    print("  Building transport network...")
    network = TransportNetwork(osm_pbf=osm_file, gtfs=gtfs_files)
    print("  OK - Transport network built successfully!")
    print("\n[7/7] Computing sample travel times...")
    sample = centroids.head(5).copy()
    dep = datetime.datetime(2026, 3, 4, 8, 0, 0)
    tt = TravelTimeMatrix(
        network,
        origins=sample,
        destinations=sample,
        departure=dep,
        departure_time_window=datetime.timedelta(minutes=10),
        max_time=datetime.timedelta(minutes=60)
    )
    print(f"  OK - Got {len(tt)} travel time pairs")
    print(tt.head(10))
except Exception as e:
    print(f"  ISSUE - {e}")
    import traceback
    traceback.print_exc()
print("\n============================================================")
print("Pipeline Test Complete")
print("============================================================")
