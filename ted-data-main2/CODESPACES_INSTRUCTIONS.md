# Edmonton Transit Equity Dashboard - Codespaces Setup

## Quick Start (2 commands)

Once your Codespace is running, open the terminal and run:

```bash
bash setup_data.sh
python test_pipeline.py
```

That's it! The setup script downloads all the large data files automatically.

## What the setup script does

1. Installs Python dependencies
2. Downloads Alberta OSM data (~200MB)
3. Downloads Statistics Canada boundaries (~200MB)
4. Downloads Edmonton Transit GTFS feed (~50MB)
5. Processes boundaries into region files

## Troubleshooting

- If `devcontainer_config` exists, the script renames it to `.devcontainer` automatically
- If downloads fail, re-run `bash setup_data.sh` - it skips already-downloaded files
