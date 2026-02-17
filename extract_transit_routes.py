import zipfile, pandas as pd, json, os, numpy as np
print("=== Extracting Transit Routes ===")
with zipfile.ZipFile('data/EDM/gtfs/ETS.zip') as z:
    routes = pd.read_csv(z.open('routes.txt'), dtype=str)
    trips = pd.read_csv(z.open('trips.txt'), dtype=str)
    shapes = pd.read_csv(z.open('shapes.txt'))
tc = trips.groupby('route_id').size().reset_index(name='trip_count')
routes = routes.merge(tc, on='route_id', how='left')
routes['trip_count'] = routes['trip_count'].fillna(0).astype(int)
rs = trips[['route_id','shape_id']].drop_duplicates('route_id')
routes = routes.merge(rs, on='route_id', how='left')
routes['route_type'] = routes['route_type'].astype(int)
routes['category'] = 'bus_regular'
routes.loc[routes['route_type'].isin([0,1,2]), 'category'] = 'lrt'
bus = routes[routes['category']!='lrt']
if len(bus)>0:
    hf = bus['trip_count'].quantile(0.85)
    routes.loc[(routes['category']=='bus_regular')&(routes['trip_count']>=hf),'category']='bus_high_freq'
sg = shapes.sort_values('shape_pt_sequence').groupby('shape_id')
result = {'lrt':[], 'bus_high_freq':[], 'bus_regular':[]}
for _,r in routes.iterrows():
    if pd.isna(r.get('shape_id')): continue
    if r['shape_id'] not in sg.groups: continue
    pts = sg.get_group(r['shape_id'])
    step = 1 if r['category']=='lrt' else (2 if r['category']=='bus_high_freq' else 3)
    coords = pts[['shape_pt_lat','shape_pt_lon']].iloc[::step].values.tolist()
    name = (r.get('route_short_name','') or '')
    ln = (r.get('route_long_name','') or '')
    dn = f"{name} - {ln}".strip(' -') if ln else name
    result[r['category']].append({'route_id':r['route_id'],'name':dn,'short_name':name,'trip_count':int(r['trip_count']),'coords':coords})
for c in result: result[c].sort(key=lambda x:x['trip_count'],reverse=True)
os.makedirs('data/EDM/processed', exist_ok=True)
with open('data/EDM/processed/transit_routes.json','w') as f: json.dump(result,f)
sz = os.path.getsize('data/EDM/processed/transit_routes.json')/1024/1024
for c,rl in result.items():
    print(f"  {c}: {len(rl)} routes")
    if rl: print(f"    Top: {', '.join(r['name'] for r in rl[:3])}")
print(f"Saved {sz:.1f}MB")
