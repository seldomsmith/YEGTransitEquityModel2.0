# Upload Instructions for GitHub

## ✅ All Folders Are Now Visible!

I've renamed the hidden folders so you can upload them easily:

- `.devcontainer` → `devcontainer_config` (will auto-rename in cloud)
- `data` → `data_folders` (will auto-rename in cloud)

The `setup_data.sh` script will automatically fix these names when it runs.

---

## What's in this folder?

This `ted-data-main2` folder contains ONLY the essential code files needed for your GitHub repository. All large data files have been excluded - they will be downloaded automatically in the cloud.

## Total Size: ~100KB ✅

## What's Included:

✅ All Python scripts (ted/ module, test_pipeline.py, etc.)
✅ Configuration files (configs/, devcontainer_config/)
✅ Dockerfile and setup_data.sh
✅ Empty data_folders/ structure (with .gitkeep files)
✅ All documentation

## What's NOT Included (downloads in cloud):

❌ OSM files (~200MB)
❌ Census boundaries (~200MB)  
❌ GTFS data (~50MB)

---

## How to Upload to GitHub

### Step 1: Clear Your Repository (Recommended)

1. Go to https://github.com/seldomsmith/YEGTransitEquityModel1.0
2. Delete all existing files to start fresh

### Step 2: Upload Everything

1. Open the `ted-data-main2` folder on your computer
2. **Select ALL files and folders inside** (Ctrl+A)
   - You should see: devcontainer_config, data_folders, ted, configs, and all the .md/.py files
3. **Drag them to the GitHub repository page**
4. **Commit the changes**

### Step 3: Launch in Cloud

#### Option A: GitHub Codespaces (Recommended - Free & Easy)

1. Click the green "Code" button on GitHub
2. Go to "Codespaces" tab
3. Click "Create codespace on main"
4. Wait for it to build (~2-3 minutes)
5. In the terminal, run:
   ```bash
   bash setup_data.sh
   ```
   This will:
   - Rename folders automatically
   - Download all data files
   - Install dependencies
   - Process the data
6. Then run:
   ```bash
   python3 test_pipeline.py
   ```

#### Option B: Google Cloud Run (Professional Deployment)

1. Install Google Cloud SDK
2. Run: `gcloud run deploy transit-dashboard --source .`
3. The Dockerfile will handle everything automatically

---

## Troubleshooting

**Q: I still can't see devcontainer_config or data_folders**
A: In Windows Explorer, make sure "Show hidden files" is enabled. But these folders are now named WITHOUT dots, so they should be visible!

**Q: The upload says "file too large"**
A: Make sure you're uploading from `ted-data-main2`, NOT `ted-data-main`. The ted-data-main2 folder excludes all large data files.

**Q: What if I accidentally upload the wrong folder?**
A: Just delete everything on GitHub and try again. The ted-data-main2 folder is ready to go!

---

## What Happens in the Cloud?

The `setup_data.sh` script will automatically:

1. ✅ Rename devcontainer_config → .devcontainer
2. ✅ Rename data_folders → data
3. ✅ Download Alberta OSM data (~200MB)
4. ✅ Download Census boundaries (~200MB)
5. ✅ Download Edmonton GTFS feed (~50MB)
6. ✅ Install all Python dependencies
7. ✅ Process all data into the correct format

**No manual data uploads needed!** 🎉
