#!/bin/bash
set -e
echo "=== Transit Equity Dashboard - Automated Data Setup ==="

# Fix folder names (Windows hides dot-folders)
if [ -d "devcontainer_config" ] && [ ! -d ".devcontainer" ]; then
    mv devcontainer_config .devcontainer
    echo "[OK] Renamed devcontainer_config to .devcontainer"
fi

# Install/Update critical build dependencies
echo "[1/5] Updating Python environment..."
python3 -m pip install --upgrade pip setuptools

# Install Python dependencies FIRST (before data downloads)
echo "[2/5] Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Create data structures
mkdir -p data/EDM/raw data/EDM/region/statscan_boundaries data/EDM/osm data/EDM/gtfs

# Download OSM (~200MB)
echo "[3/5] Downloading Alberta OSM..."
if [ ! -f "data/EDM/osm/edmonton.osm.pbf" ]; then
    wget -q --show-progress -O data/EDM/osm/edmonton.osm.pbf https://download.geofabrik.de/north-america/canada/alberta-latest.osm.pbf
else
    echo "  Already exists, skipping."
fi

# Download GTFS (~50MB)
echo "[4/5] Downloading Edmonton GTFS..."
if [ ! -f "data/EDM/gtfs/ETS.zip" ]; then
    wget -q --show-progress -O data/EDM/gtfs/ETS.zip https://gtfs.edmonton.ca/TMGTFSRealTimeWebService/GTFS/gtfs.zip
else
    echo "  Already exists, skipping."
fi

# Process data
echo "[5/5] Running data processing scripts..."
python3 generate_placeholders.py
python3 process_region.py || echo "WARNING: Region processing failed (boundary data may be missing)"

echo ""
echo "=== Data Setup Complete ==="
echo "Note: Census boundary download was skipped (StatsCan requires manual download)"
echo "The pipeline will use placeholder demographic data for now."
echo ""
echo "Next: Run 'python3 test_pipeline.py' to test the pipeline."
