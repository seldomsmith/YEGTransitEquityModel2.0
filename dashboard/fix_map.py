"""Patch app.py to add real map with centroid coordinates."""
import re
code = open('dashboard/app.py').read()
# 1. Add geopandas import
code = code.replace(
    "import os\nimport json",
    "import os\nimport json\nimport geopandas as gpd"
)
# 2. Add centroid loading after compute_accessibility function and data loading
old_load = """# Load data
demo = load_demographics()
tt = load_travel_times()
df = compute_accessibility(demo, tt)"""
new_load = """# Load data
demo = load_demographics()
tt = load_travel_times()
df = compute_accessibility(demo, tt)
# Load centroids for map coordinates
centroids_path = os.path.join(DATA_DIR, 'region', 'centroids.gpkg')
if os.path.exists(centroids_path):
    centroids_gdf = gpd.read_file(centroids_path)
    centroids_gdf['lat'] = centroids_gdf.geometry.y
    centroids_gdf['lon'] = centroids_gdf.geometry.x
    coords = centroids_gdf[['DAUID', 'lat', 'lon']]
    df = df.merge(coords, on='DAUID', how='left')
    print(f"  Loaded {len(coords)} centroid coordinates for map")
else:
    # Random coords for development
    df['lat'] = np.random.uniform(53.4, 53.7, len(df))
    df['lon'] = np.random.uniform(-113.7, -113.3, len(df))
    print("  Using sample coordinates (no centroids.gpkg found)")"""
code = code.replace(old_load, new_load)
# 3. Replace the map callback with a real scatter_mapbox
old_map = """    # Create a scatter map (since we don't have GeoJSON in browser)
    # Using centroids as proxy for DA locations
    # In production, this would use a choropleth with GeoJSON boundaries
    
    fig = px.scatter_mapbox(
        df,
        lat=None,  # Will be replaced with actual coordinates
        lon=None,
        color=metric,
        size='total_pop',
        color_continuous_scale=CHOROPLETH_SCALE if metric != 'avg_travel_time' else CHOROPLETH_SCALE[::-1],
        hover_name='DAUID',
        hover_data={
            'total_pop': True,
            'accessibility': ':.1f',
            'low_income_pct': ':.1f',
        },
        title=labels.get(metric, metric),
        mapbox_style='open-street-map',
        zoom=10,
        center={'lat': 53.55, 'lon': -113.49},
    ) if False else go.Figure()  # Placeholder - needs lat/lon data
    
    # For now, create a meaningful chart instead
    fig = px.histogram(
        df, x=metric, nbins=30,
        color_discrete_sequence=[COLORS['green_400']],
        title=f'Distribution: {labels.get(metric, metric)}',
    )
    fig.update_layout(
        height=550,
        xaxis_title=labels.get(metric, metric),
        yaxis_title='Number of Neighbourhoods',
        **CHART_TEMPLATE['layout'],
    )"""
new_map = """    # Real scatter mapbox with centroid coordinates
    map_df = df.dropna(subset=['lat', 'lon']).copy()
    
    # Clamp size to avoid tiny/huge dots
    map_df['marker_size'] = np.clip(map_df['total_pop'], 50, 2000)
    
    reverse = metric in ['avg_travel_time', 'desert_score']
    scale = CHOROPLETH_SCALE[::-1] if reverse else CHOROPLETH_SCALE
    
    fig = px.scatter_mapbox(
        map_df,
        lat='lat',
        lon='lon',
        color=metric,
        size='marker_size',
        size_max=15,
        color_continuous_scale=scale,
        hover_name='DAUID',
        hover_data={
            'total_pop': ':,',
            'accessibility': ':.1f',
            'avg_travel_time': ':.1f',
            'low_income_pct': ':.1f',
            'marker_size': False,
        },
        mapbox_style='open-street-map',
        zoom=10,
        center={'lat': 53.55, 'lon': -113.49},
        opacity=0.7,
    )
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title=labels.get(metric, metric),
            thickness=15,
            len=0.6,
        ),
        mapbox=dict(
            bearing=0,
            pitch=0,
        ),
    )"""
code = code.replace(old_map, new_map)
open('dashboard/app.py', 'w').write(code)
print("✅ Map patched! Restart the dashboard to see the real map.")
