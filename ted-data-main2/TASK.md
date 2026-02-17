# Transit Equity Dashboard - Edmonton Adaptation Task List

## 1. Project Initialization

- [x] Create project structure for Edmonton (`EDM`) region.
- [x] Create `configs/EDM` directory.
- [x] Draft initial `config.yaml` for Edmonton parameters.

## 2. Data Acquisition

### Transit Data

- [x] **ETS GTFS Feed**: Downloaded and placed in `data/EDM/gtfs/ETS.zip`
  - Source: Edmonton Transit Service (Feb-Apr 2026 schedule)

### Network Data

- [x] **OpenStreetMap Extract**: Downloaded Alberta extract as `edmonton.osm.pbf`
  - Source: [Geofabrik](https://download.geofabrik.de/north-america/canada/alberta.html)

### Demographic Data (Census Replacement)

**⚠️ IMPORTANT: Currently Using PLACEHOLDER Data**

The system is configured with **randomly generated placeholder demographic data** to enable initial testing of the transit routing pipeline. This data is located at:

- `data/EDM/raw/demographics.csv` (1219 DAs with dummy values)
- `data/EDM/raw/supply.csv` (placeholder job/service counts)

**TO DO**: Replace with real 2021 Census data when Statistics Canada site is available.

Required real data:

- [x] **Boundary File**: Downloaded Statistics Canada 2021 DA boundaries
  - Processed to `data/EDM/region/region.gpkg` (1113 Edmonton DAs)
  - Centroids generated at `data/EDM/region/centroids.gpkg`
- [ ] **Demographic Profile**: CSV file keyed by `DAUID` containing:
  - Total Population
  - Low-Income Population (LIM-AT or LICO)
  - Visible Minority Population
  - Single Parent Households
  - Zero-Car Households
  - Seniors (65+)

### Destination/Supply Data

_Note: Currently using placeholder data. Needs real data aggregated to the DA level._

- [ ] **Jobs**: Total jobs count per `DAUID`.
- [ ] **Essential Services Points**: Shapefiles or lat/lon CSVs for:
  - Grocery Stores
  - Hospitals / Urgent Care
  - Pharmacies
  - Schools (K-12 and Post-Secondary)
  - Parks/Green Spaces (Polygon or centroids)

## 3. Code Adaptation

### Census Module Refactor

- [ ] **Abstract `ted/census.py`**: Modify to support loading local Shapefiles/CSVs instead of US Census API.
- [ ] **ID Standardization**: Replace `BG20` (Block Group 2020) references with `DAUID` throughout the pipeline (or alias `DAUID` to `BG20` to minimize code churn).

### Fare Module Update

- [ ] **Implement Edmonton Fare Rules**:
  - Update `ted/fare.py` with ETS logic (90-min transfer window, base fare).
- [ ] **Fare Matrix**: Generate the cost matrix between all DAs.

### Analysis Execution

- [ ] **Run Matrix**: Calculate travel times (Transit & Auto) for all DA pairs.
- [ ] **Run Accessibility Scenarios**: Calculate access to jobs/services within 30, 45, 60 mins.
- [ ] **Run Equity Analysis**: Weight accessibility scores by key demographic groups.

## 4. Validation & Visualization

- [ ] **QC Outputs**: Verify travel times match reality (e.g., Downtown to mill woods).
- [ ] **Generate Vector Tiles**: Convert results to Mapbox-compatible tiles for the frontend.
