#!/bin/bash
set -e
echo "=== Transit Equity Dashboard - Automated Data Setup ==="

# Fix folder names (Windows hides dot-folders)
if [ -d "devcontainer_config" ] && [ ! -d ".devcontainer" ]; then
    mv devcontainer_config .devcontainer
    echo "[OK] Renamed devcontainer_config to .devcontainer"
fi

# Install/Update critical build dependencies
echo "[1/4] Updating Python environment..."
python3 -m pip install --upgrade pip setuptools

# Create data structures (in case they don't exist)
mkdir -p data/EDM/raw data/EDM/region/statscan_boundaries data/EDM/osm data/EDM/gtfs

# Download OSM (~200MB)
echo "[2/4] Downloading Alberta OSM..."
if [ ! -f "data/EDM/osm/edmonton.osm.pbf" ]; then
    wget -q --show-progress -O data/EDM/osm/edmonton.osm.pbf https://download.geofabrik.de/north-america/canada/alberta-latest.osm.pbf
else
    echo "  Already exists, skipping."
fi

# Download Boundaries (~200MB)
echo "[3/4] Downloading Census Boundaries..."
if [ ! -f "data/EDM/region/lda_000b21a_e.zip" ]; then
    wget -q --show-progress -O data/EDM/region/lda_000b21a_e.zip https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-le/boundary-limites/files-fichiers/lda_000b21a_e.zip
    unzip -o data/EDM/region/lda_000b21a_e.zip -d data/EDM/region/statscan_boundaries
else
    echo "  Already exists, skipping."
fi

# Download GTFS (~50MB)
echo "[4/4] Downloading Edmonton GTFS..."
if [ ! -f "data/EDM/gtfs/ETS.zip" ]; then
    wget -q --show-progress -O data/EDM/gtfs/ETS.zip https://gtfs.edmonton.ca/TMGTFSRealTimeWebService/GTFS/gtfs.zip
else
    echo "  Already exists, skipping."
fi

# Install Python dependencies
echo "[5/5] Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Process data
echo "[PROCESSING] Running data processing scripts..."
python3 generate_placeholders.py
python3 process_region.py

echo ""
echo "=== Data Setup Complete ==="
echo "Next: Run 'python3 test_pipeline.py' to test the pipeline."
