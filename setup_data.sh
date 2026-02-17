#!/bin/bash
set -e
echo "=== Transit Equity Dashboard - Automated Data Setup ==="

# Fix devcontainer folder name if needed
if [ -d "devcontainer_config" ] && [ ! -d ".devcontainer" ]; then
    mv devcontainer_config .devcontainer
    echo "[OK] Fixed .devcontainer structure."
fi

# Install/Update critical build dependencies
echo "[1/4] Updating Python environment..."
python3 -m pip install --upgrade pip setuptools

# Create data structures
mkdir -p data/EDM/raw data/EDM/region/statscan_boundaries data/EDM/osm data/EDM/gtfs

# Download OSM (~200MB)
echo "[2/4] Downloading Alberta OSM..."
if [ ! -f "data/EDM/osm/edmonton.osm.pbf" ]; then
    wget -q --show-progress -O data/EDM/osm/edmonton.osm.pbf https://download.geofabrik.de/north-america/canada/alberta-latest.osm.pbf
fi

# Download Boundaries (~200MB)
echo "[3/4] Downloading Census Boundaries..."
if [ ! -f "data/EDM/region/lda_000b21a_e.zip" ]; then
    wget -q --show-progress -O data/EDM/region/lda_000b21a_e.zip https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-le/boundary-limites/files-fichiers/lda_000b21a_e.zip
    unzip -o data/EDM/region/lda_000b21a_e.zip -d data/EDM/region/statscan_boundaries
fi

# Download GTFS (~50MB)
echo "[4/4] Downloading Edmonton GTFS..."
if [ ! -f "data/EDM/gtfs/ETS.zip" ]; then
    wget -q --show-progress -O data/EDM/gtfs/ETS.zip https://gtfs.edmonton.ca/TMGTFSRealTimeWebService/GTFS/gtfs.zip
fi

# Process data
echo "[DONE] Running initial processing scripts..."
python3 generate_placeholders.py
python3 process_region.py
echo "=== Data Setup Complete ==="
