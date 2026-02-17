# Edmonton Transit Equity Dashboard - Setup Summary

**Date**: 2026-02-16  
**Status**: Environment configured, ready for initial pipeline test

## ✅ Completed Tasks

### 1. Project Structure

- Created directory structure for Edmonton region (`data/EDM/`)
- Set up configuration in `configs/EDM/config.yaml`

### 2. Data Acquisition

- **Transit Data**: ETS GTFS feed (Feb-Apr 2026) → `data/EDM/gtfs/ETS.zip`
- **Network Data**: Alberta OSM extract → `data/EDM/osm/edmonton.osm.pbf`
- **Boundary Data**: Statistics Canada 2021 DAs → Processed to GeoPackages

### 3. Environment Setup

- Installed Python 3.11 with required packages:
  - geopandas 1.1.2
  - pandas 2.0.3
  - r5py 1.1.0
  - pyproj, shapely, rasterio, etc.

### 4. Data Processing

- Extracted 1,113 Edmonton DAs from Canada-wide shapefile
- Generated region boundaries: `data/EDM/region/region.gpkg`
- Generated routing centroids: `data/EDM/region/centroids.gpkg`

### 5. Placeholder Data

- Created `demographics.csv` with 1,219 DAs (dummy values for testing)
- Created `supply.csv` with placeholder job/service counts
- **⚠️ NOTE**: These are temporary files for pipeline testing only

## ⏳ Pending Tasks

### Critical: Real Demographic Data

- [ ] Download 2021 Census Profile from Statistics Canada (site currently down for maintenance)
- [ ] Extract required variables: population, low-income, minority, single-parent, zero-car, seniors
- [ ] Replace `data/EDM/raw/demographics.csv` with real data

### Optional: Supply/Destination Data

- [ ] Acquire real jobs data by DA
- [ ] Locate essential services (grocery, hospitals, schools)
- [ ] Replace `data/EDM/raw/supply.csv` with real data

### Code Optimization

- [ ] Refactor `ted/fare.py` (1043 lines) into smaller modules
- [ ] Refactor `ted/gtfs.py` (790 lines) into smaller modules
- [ ] Refactor `ted/run.py` (754 lines) into smaller modules

## 🚀 Next Steps

1. **Run Initial Test**: Execute the pipeline with placeholder data to verify:
   - GTFS parsing works correctly
   - OSM network loading succeeds
   - Travel time matrix calculation runs
   - Output files are generated

2. **Acquire Real Data**: Once Statistics Canada site is back online:
   - Download Census Profile for Alberta DAs
   - Process and integrate real demographic data

3. **Validate Results**: Compare outputs with known transit patterns

## 📁 File Locations

```
data/EDM/
├── gtfs/
│   └── ETS.zip                    # Transit schedules
├── osm/
│   └── edmonton.osm.pbf           # Street network
├── region/
│   ├── region.gpkg                # DA boundaries (1113 features)
│   └── centroids.gpkg             # Routing points
└── raw/
    ├── demographics.csv           # ⚠️ PLACEHOLDER
    └── supply.csv                 # ⚠️ PLACEHOLDER
```

## 📝 Configuration

See `configs/EDM/config.yaml` for all path settings and parameters.
