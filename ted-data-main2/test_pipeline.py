"""
Edmonton Transit Equity Dashboard - Pipeline Test Script
Tests that core data loading and routing components work correctly.
"""
import os
import sys
import datetime

print("=" * 60)
print("Edmonton TED Pipeline Test")
print("=" * 60)

# ------------------------------------------------------------------
# Test 1: Import Core Libraries
# ------------------------------------------------------------------
print("\n[1/6] Importing core libraries...")
try:
    import geopandas as gpd
    import pandas as pd
    import yaml
    print("  OK - geopandas, pandas, yaml imported")
except ImportError as e:
    print(f"  FAIL - Missing library: {e}")
    sys.exit(1)

# ------------------------------------------------------------------
# Test 2: Load Config
# ------------------------------------------------------------------
print("\n[2/6] Loading Edmonton config...")
config_path = os.path.join("configs", "EDM", "config.yaml")
try:
    with open(config_path) as f:
        config = yaml.safe_load(f)
    print(f"  OK - Region: {config['name']} ({config['code']})")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

# ------------------------------------------------------------------
# Test 3: Load Region Boundaries
# ------------------------------------------------------------------
print("\n[3/6] Loading region boundaries...")
try:
    region = gpd.read_file(config["gpkg"])
    print(f"  OK - {len(region)} dissemination areas loaded")
    print(f"  CRS: {region.crs}")
    print(f"  Bounds: {region.total_bounds}")
except Exception as e:
    print(f"  FAIL - {e}")

# ------------------------------------------------------------------
# Test 4: Load Centroids
# ------------------------------------------------------------------
print("\n[4/6] Loading centroids...")
try:
    centroids = gpd.read_file(config["centroids_gpkg"])
    print(f"  OK - {len(centroids)} centroid points loaded")
    print(f"  Sample DAUIDs: {centroids['DAUID'].head(5).tolist()}")
except Exception as e:
    print(f"  FAIL - {e}")

# ------------------------------------------------------------------
# Test 5: Load Demographics (Placeholder)
# ------------------------------------------------------------------
print("\n[5/6] Loading demographics...")
try:
    demo = pd.read_csv(config["demographics"])
    print(f"  OK - {len(demo)} rows, columns: {list(demo.columns)}")
    print(f"  NOTE: This is PLACEHOLDER data")
except Exception as e:
    print(f"  FAIL - {e}")

# ------------------------------------------------------------------
# Test 6: GTFS and Transport Network
# ------------------------------------------------------------------
print("\n[6/6] Testing transport network build...")
try:
    from r5py import TransportNetwork
    
    gtfs_folder = config["gtfs"]
    osm_file = config["osm"]
    
    # Find GTFS zip files
    gtfs_files = []
    for fname in os.listdir(gtfs_folder):
        if fname.endswith(".zip") and not fname.startswith("."):
            gtfs_files.append(os.path.join(gtfs_folder, fname))
    print(f"  Found {len(gtfs_files)} GTFS file(s): {[os.path.basename(f) for f in gtfs_files]}")
    print(f"  OSM file: {osm_file} (exists: {os.path.exists(osm_file)})")
    
    # Build transport network - this is the critical test
    print("  Building transport network (this may take a few minutes)...")
    network = TransportNetwork(osm_pbf=osm_file, gtfs=gtfs_files)
    print("  OK - Transport network built successfully!")
    
    # Quick travel time test with a small subset
    from r5py import TravelTimeMatrixComputer
    
    sample = centroids.head(5).copy()
    sample = sample.rename(columns={"DAUID": "id"})
    
    departure_time = datetime.datetime(2026, 3, 4, 8, 0, 0)
    
    print(f"  Computing sample travel times (5 origins -> 5 destinations)...")
    ttmc = TravelTimeMatrixComputer(
        network,
        origins=sample,
        destinations=sample,
        departure=departure_time,
        departure_time_window=datetime.timedelta(minutes=10),
        max_time=datetime.timedelta(minutes=60),
    )
    tt_matrix = ttmc.compute_travel_times()
    print(f"  OK - Got {len(tt_matrix)} travel time pairs")
    print(f"  Sample results:")
    print(tt_matrix.head(10).to_string(index=False))
    
except ImportError as e:
    print(f"  WARN - r5py import issue: {e}")
    print("  (r5py requires Java - checking...)")
    os.system("java -version 2>&1")
except Exception as e:
    print(f"  ISSUE - {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Pipeline Test Complete")
print("=" * 60)
