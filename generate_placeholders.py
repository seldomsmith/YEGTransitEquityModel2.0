import csv
import os
import random

# Paths
raw_dir = "data/EDM/raw"
demo_csv = os.path.join(raw_dir, "demographics.csv")
supply_csv = os.path.join(raw_dir, "supply.csv")

# Generate placeholder DAs for Edmonton (typical range: 48110001 - 48110999)
da_ids = [f"481100{str(i).zfill(2)}" for i in range(1, 200)]

print(f"Generating {len(da_ids)} placeholder DAs...")

os.makedirs(raw_dir, exist_ok=True)

# Create Demographics
with open(demo_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["DAUID", "total_pop", "low_income", "minority", "single_parent", "zero_car", "seniors"])
    
    for da in da_ids:
        pop = random.randint(300, 1000)
        writer.writerow([
            da, pop, int(pop * 0.15), int(pop * 0.30), 
            int(pop * 0.10), int(pop * 0.05), int(pop * 0.12)
        ])

print(f"Created {demo_csv}")

# Create Supply
with open(supply_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["DAUID", "total_jobs", "essential_services"])
    
    for da in da_ids:
        writer.writerow([da, random.randint(0, 500), random.randint(0, 5)])

print(f"Created {supply_csv}")
