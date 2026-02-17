# Transit Equity Dashboard - Edmonton Implementation Plan

## Overview

This document details the modifications required to adapt the US-centric Transit Equity Dashboard for Edmonton (EDM). The original system uses US Census Block Groups (`BG20`), ACS demographic variables, and `pygris` to fetch US boundaries. We will replace these with Canadian equivalents while maintaining the existing data pipeline structure where possible.

## 1. Directory Structure

We will create a new region directory `data/EDM` to mirror the existing structure:

```
data/
  └── EDM/
      ├── config.yaml          # Main configuration file
      ├── runs.yaml            # Run definitions (dates/times)
      ├── region/
      │   └── boundaries.gpkg  # GeoPackage containing DAs and supply points
      ├── gtfs/                # Raw GTFS .zip files
      ├── osm/                 # OpenStreetMap .pbf file
      └── demographics.csv     # Census attributes (Population, Low Income, etc.)
```

## 2. Code Modifications

### A. Abstracting Census Data Loading (`ted/census.py`)

The current implementation is hardcoded for the US Census Bureau API via `pygris`. We need to introduce a `CensusLoader` abstraction.

- **Current State**: `download_demographic_data()` calls `get_census()` directly.
- **New State**:
  - Create a base class `CensusProvider`.
  - Implement `USCensusProvider` (existing logic).
  - Implement `LocalFileProvider` (for Edmonton/Canada).
  - The `LocalFileProvider` will simply load a prepared CSV and join it to a Shapefile/GeoJSON.
- **ID Mapping**:
  - Map Edmonton's `DAUID` (Dissemination Area Unique ID) to the code's expected `BG20` field to minimize refactoring across the entire codebase.

### B. Fare Logic Implementation (`ted/fare.py`)

Edmonton's fare structure (Base Fare + 90-min Transfer) is simpler than zonal systems but has unique rules (Arc card capping is complex, but for initial implementation we can model a simple transfer window).

- **Base Fare**: $3.50 (Cash) / $2.75 (Arc Stored Value). We can model the $2.75 base fare.
- **Transfer Window**: 90 minutes.
- **Implementation**:
  - Create a `EdmontonFare` class inheriting from `BaseFare`.
  - Logic: `cost = base_fare` for first boarding. Subsequent boardings within 90 mins are free ($0 transfer cost).

### C. GTFS Handling (`ted/gtfs.py`)

- No major code changes expected here. The existing `GTFS` loading library is standard.
- **Action**: Validate that ETS GTFS `stop_times.txt` and `calendar.txt` cover the analysis dates correctly.

### D. Run Configuration (`ted/run.py`)

- Update `create_regions()` to include `EDM`.
- The `Run` class takes a `regions` dictionary. We need to ensure the `EDM` entry points to our local files instead of trying to fetch US data.

## 3. Data Schema Specifications

### Demographic Data (`demographics.csv`)

The system expects specific columns. We will create a mapping or pre-process the Canadian Census CSV to match:
| System Field | Source Field (StatCan 2021) | Notes |
| :--- | :--- | :--- |
| `BG20` | `DAUID` | Primary Key |
| `total_pop` | `Population, 2021` | |
| `low_income` | `LIM-AT` or `LICO-AT` count | Proxy for poverty metrics |
| `minority` | `Visible Minority Total` | Proxy for racial equity metrics |
| `single_parent` | `Total - Lone-parent census families in private households` | |
| `zero_car` | `No certificate of registration` (check availability) | Or estimate from specialized tables |

### Supply Data (`supply.csv`)

Aggregated counts per DA (or points that can be aggregated):
| System Field | Description |
| :--- | :--- |
| `jobs_total` | Total jobs in DA |
| `grocery` | Count of supermarkets |
| `education` | Count of schools/universities |
| `parks` | Park area (hectares) or access point count |

## 4. Execution Workflow

1.  **Prepare Data**: User places all files in `data/EDM/raw`.
2.  **ETL Script**: Run a new script `scripts/prepare_edm_data.py` (to be written) which:
    - Standardizes IDs.
    - Converts boundaries to a compatible GeoPackage.
    - Generates the required `demographics.csv` and `supply.csv`.
3.  **Run Analysis**:
    - `python ted/run.py --config data/EDM/config.yaml`
4.  **Validate**:
    - Check `results/EDM/access.csv` for reasonable travel times.

## 5. Next Steps for User

1. [ ] Confirm access to Edmonton Data Portal (GTFS, Boundaries).
2. [ ] Locate the 2021 Census Profile for Edmonton CSD (Census Subdivision) broken down by Dissemination Area.
3. [ ] Provide the list of available files so we can write the specific ETL scripts.
