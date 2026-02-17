import csv
import os
import random

# Paths
raw_dir = r"data\EDM\raw"
boundary_csv = os.path.join(raw_dir, "Statistics_Canada_Dissemination_Areas_20260216.csv")
demo_csv = os.path.join(raw_dir, "demographics.csv")
supply_csv = os.path.join(raw_dir, "supply.csv")

# 1. Read DA IDs from the user's boundary CSV
# The file format seems to be: "fid","da_int","name","Geometry"
# And values like: "1","48,111,966","Name",...
da_ids = []

try:
    with open(boundary_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        # Find da_int index
        try:
            id_idx = header.index("da_int")
        except ValueError:
            # Fallback if header is different, assuming 2nd column based on preview
            id_idx = 1
            
        for row in reader:
            if len(row) > id_idx:
                # Remove commas from ID (e.g., "48,111,966" -> "48111966")
                clean_id = row[id_idx].replace(",", "").strip()
                if clean_id.isdigit():
                    da_ids.append(clean_id)

    print(f"Found {len(da_ids)} DAs.")

    # 2. Create Placeholder Demographics
    # Columns: DB table usually expects: id, total_pop, etc.
    # Based on other regions, usually mapping is defined in config.
    # Let's create columns: DAUID, Total_Pop, Low_Income, Limit_Mobility
    
    with open(demo_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["DAUID", "total_pop", "low_income", "minority", "single_parent", "zero_car", "seniors"])
        
        for da in da_ids:
            # Random dummy data for testing
            pop = random.randint(300, 1000)
            writer.writerow([
                da, 
                pop, 
                int(pop * 0.15), # 15% low income
                int(pop * 0.30), # 30% minority
                int(pop * 0.10), 
                int(pop * 0.05),
                int(pop * 0.12)
            ])
            
    print(f"Created {demo_csv}")

    # 3. Create Placeholder Supply (Jobs/Destinations)
    with open(supply_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["DAUID", "total_jobs", "essential_services"])
        
        for da in da_ids:
            writer.writerow([
                da,
                random.randint(0, 500), # Jobs vary a lot
                random.randint(0, 5)    # Few services per DA
            ])
            
    print(f"Created {supply_csv}")

except Exception as e:
    print(f"Error: {e}")
