# Upload Instructions for GitHub

## What's in this folder?

This `ted-data-main2` folder contains ONLY the essential code files needed for your GitHub repository. All large data files have been excluded - they will be downloaded automatically in the cloud.

## Total Size

~100KB (small enough for easy GitHub upload)

## What's Included:

✅ All Python scripts (ted/ module, test_pipeline.py, etc.)
✅ Configuration files (configs/, .devcontainer/)
✅ Dockerfile and setup_data.sh
✅ Empty data/ folder structure (with .gitkeep files)

## What's NOT Included (will download in cloud):

❌ OSM files (~200MB)
❌ Census boundaries (~200MB)  
❌ GTFS data (~50MB)

---

## How to Upload to GitHub

### Step 1: Clear Your Repository (Optional but Recommended)

1. Go to https://github.com/seldomsmith/YEGTransitEquityModel1.0
2. Delete all existing files to start fresh

### Step 2: Upload Everything

1. Open the `ted-data-main2` folder on your computer
2. Select ALL files and folders inside (Ctrl+A)
3. Drag them to the GitHub repository page
4. Commit the changes

### Step 3: Launch in Cloud

Choose ONE of these options:

#### Option A: GitHub Codespaces (Free, Easy)

1. Click the green "Code" button on GitHub
2. Go to "Codespaces" tab
3. Click "Create codespace on main"
4. Wait for it to build (~2 minutes)
5. In the terminal, run:
   ```bash
   bash setup_data.sh
   python3 test_pipeline.py
   ```

#### Option B: Google Cloud Run (Professional)

1. Install Google Cloud SDK
2. Run: `gcloud run deploy transit-dashboard --source .`
3. The Dockerfile will handle everything automatically

---

## What Happens in the Cloud?

The `setup_data.sh` script will automatically:

1. Download Alberta OSM data
2. Download Census boundaries
3. Download Edmonton GTFS feed
4. Process all data into the correct format
5. Run the test pipeline

No manual data uploads needed! 🎉
