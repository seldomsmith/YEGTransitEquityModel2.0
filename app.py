"""
Edmonton Transit Equity Dashboard
River Valley Light Theme — Built with Dash (Plotly)

Run:  python app.py
Open:  http://localhost:8050
"""

import dash
from dash import html, dcc, callback, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import json
import geopandas as gpd
import geopandas as gpd

# ============================================================
# DATA LOADING
# ============================================================

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'EDM')

def load_demographics():
    """Load real demographics or generate sample data."""
    demo_path = os.path.join(DATA_DIR, 'raw', 'demographics.csv')
    if os.path.exists(demo_path):
        df = pd.read_csv(demo_path, dtype={'DAUID': str})
        return df
    else:
        # Generate sample for development
        np.random.seed(42)
        n = 200
        return pd.DataFrame({
            'DAUID': [f'4811{str(i).zfill(4)}' for i in range(n)],
            'total_pop': np.random.randint(100, 2000, n),
            'low_income': np.random.randint(10, 500, n),
            'minority': np.random.randint(20, 600, n),
            'seniors': np.random.randint(10, 400, n),
        })

def load_travel_times():
    """Load travel time matrix or generate sample."""
    tt_path = os.path.join(DATA_DIR, 'processed', 'travel_times.csv')
    if os.path.exists(tt_path):
        return pd.read_csv(tt_path, dtype={'from_id': str, 'to_id': str})
    return None

def compute_accessibility(demo_df, tt_df=None, threshold=45):
    """Compute accessibility scores for each DA."""
    n = len(demo_df)
    
    if tt_df is not None and len(tt_df) > 0:
        # Real computation from travel time matrix
        reachable = tt_df[tt_df['travel_time'] <= threshold].groupby('from_id').size()
        scores = (reachable / n * 100).clip(0, 100)
        demo_df = demo_df.copy()
        demo_df['accessibility'] = demo_df['DAUID'].map(scores).fillna(0).round(1)
        
        avg_times = tt_df.groupby('from_id')['travel_time'].mean()
        demo_df['avg_travel_time'] = demo_df['DAUID'].map(avg_times).fillna(60).round(1)
    else:
        # Sample data for development
        np.random.seed(42)
        demo_df = demo_df.copy()
        demo_df['accessibility'] = np.random.uniform(5, 85, n).round(1)
        demo_df['avg_travel_time'] = np.random.uniform(15, 55, n).round(1)
    
    # Derived metrics
    demo_df['low_income_pct'] = (demo_df['low_income'] / demo_df['total_pop'].replace(0, 1) * 100).round(1)
    demo_df['minority_pct'] = (demo_df['minority'] / demo_df['total_pop'].replace(0, 1) * 100).round(1)
    demo_df['senior_pct'] = (demo_df['seniors'] / demo_df['total_pop'].replace(0, 1) * 100).round(1)
    
    # Vulnerability weight (normalized)
    vuln = demo_df[['low_income_pct', 'minority_pct', 'senior_pct']].mean(axis=1)
    demo_df['vulnerability'] = (vuln / vuln.max() * 100).round(1) if vuln.max() > 0 else 0
    
    # Transit Desert Score = low access + high vulnerability
    demo_df['desert_score'] = ((100 - demo_df['accessibility']) * demo_df['vulnerability'] / 100).round(1)
    
    # Equity Index = access × vulnerability (high = vulnerable BUT well-served)
    demo_df['equity_index'] = (demo_df['accessibility'] * demo_df['vulnerability'] / 100).round(1)
    
    # Rank
    demo_df['access_rank'] = demo_df['accessibility'].rank(ascending=False).astype(int)
    
    # Rating
    def rate(score):
        if score >= 60: return 'Excellent'
        if score >= 40: return 'Good'
        if score >= 20: return 'Moderate'
        return 'Poor'
    demo_df['rating'] = demo_df['accessibility'].apply(rate)
    
    return demo_df


# Load data
demo = load_demographics()
tt = load_travel_times()
df = compute_accessibility(demo, tt)

# Load centroids for map coordinates
centroids_path = os.path.join(DATA_DIR, 'region', 'centroids.gpkg')
try:
    if os.path.exists(centroids_path):
        centroids_gdf = gpd.read_file(centroids_path)
        centroids_gdf = centroids_gdf.copy()
        centroids_gdf['DAUID'] = centroids_gdf['DAUID'].astype(str)
        centroids_gdf['lat'] = centroids_gdf.geometry.y
        centroids_gdf['lon'] = centroids_gdf.geometry.x
        coords = centroids_gdf[['DAUID', 'lat', 'lon']].copy()
        
        # Ensure DAUID is string in df as well
        df['DAUID'] = df['DAUID'].astype(str)
        
        # Merge
        df = df.merge(coords, on='DAUID', how='left')
        
        # Check if merge worked
        if 'lat' in df.columns and df['lat'].notna().sum() > 0:
            print(f"✅ Loaded {df['lat'].notna().sum()} centroid coordinates for map")
        else:
            raise ValueError("Centroid merge failed - no valid coordinates")
    else:
        raise FileNotFoundError(f"Centroids file not found: {centroids_path}")
except Exception as e:
    print(f"⚠️  Centroid loading failed: {e}")
    print("   Using sample coordinates instead")
    df['lat'] = np.random.uniform(53.4, 53.7, len(df))
    df['lon'] = np.random.uniform(-113.7, -113.3, len(df))

# Load neighbourhood names
neighbourhood_path = os.path.join(DATA_DIR, 'processed', 'da_neighbourhood_map.csv')
try:
    if os.path.exists(neighbourhood_path):
        hoods = pd.read_csv(neighbourhood_path, dtype={'DAUID': str})
        df = df.merge(hoods, on='DAUID', how='left')
        print(f"✅ Loaded neighbourhood names for {df['neighbourhood'].notna().sum()} DAs")
    else:
        df['neighbourhood'] = 'Unknown'
except Exception as e:
    print(f"⚠️  Neighbourhood loading failed: {e}")
    df['neighbourhood'] = df['DAUID']

# Load transit routes for overlay
routes_path = os.path.join(DATA_DIR, 'processed', 'transit_routes.json')
try:
    if os.path.exists(routes_path):
        with open(routes_path) as f:
            transit_routes = json.load(f)
        print(f"✅ Loaded {sum(len(v) for v in transit_routes.values())} transit routes")
    else:
        transit_routes = {'lrt': [], 'bus_high_freq': [], 'bus_regular': []}
except Exception as e:
    print(f"⚠️  Transit routes loading failed: {e}")
    transit_routes = {'lrt': [], 'bus_high_freq': [], 'bus_regular': []}

# ============================================================
# THEME COLORS (River Valley)
# ============================================================

COLORS = {
    'green_900': '#0d3b22',
    'green_800': '#1a5c3a',
    'green_600': '#2d8f6f',
    'green_400': '#43b692',
    'green_200': '#b2dfcc',
    'green_100': '#e6f5ec',
    'green_50': '#f0f9f4',
    'sun_gold': '#f5c542',
    'sun_cream': '#fef9e7',
    'amber': '#e8a735',
    'coral': '#e05c5c',
    'sky_blue': '#5bb5d5',
    'text_primary': '#1a3a2a',
    'text_secondary': '#5a7a6a',
    'white': '#ffffff',
    'bg': '#f0f9f4',
}

CHOROPLETH_SCALE = ['#e05c5c', '#e8a735', '#f5c542', '#43b692', '#1a5c3a']

# Chart template
CHART_TEMPLATE = dict(
    layout=dict(
        font=dict(family='Inter, sans-serif', color=COLORS['text_primary']),
        paper_bgcolor=COLORS['white'],
        plot_bgcolor=COLORS['green_50'],
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(gridcolor=COLORS['green_100'], zerolinecolor=COLORS['green_200']),
        yaxis=dict(gridcolor=COLORS['green_100'], zerolinecolor=COLORS['green_200']),
    )
)

# ============================================================
# APP INITIALIZATION
# ============================================================

app = dash.Dash(
    __name__,
    title='Edmonton Transit Equity Dashboard',
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'},
        {'name': 'description', 'content': 'Transit equity analysis for Edmonton, Alberta — visualizing accessibility across 1,952 neighbourhoods.'},
    ],
    suppress_callback_exceptions=True,
)

# ============================================================
# COMPONENT BUILDERS
# ============================================================

def build_kpi_card(label, value, icon, variant='', change_text=''):
    """Build a single KPI card."""
    children = [
        html.Div(icon, className='kpi-icon'),
        html.Div(label, className='kpi-label'),
        html.Div(str(value), className=f'kpi-value {variant}'),
    ]
    if change_text:
        children.append(html.Div(change_text, className='kpi-change positive'))
    return html.Div(children, className=f'kpi-card {variant}')


def build_sidebar():
    """Build the navigation sidebar."""
    return html.Div([
        # Logo
        html.Div([
            html.Div([
                html.Div('🚌', className='sidebar-logo-icon'),
                html.Span('Transit Equity'),
            ], className='sidebar-logo'),
            html.Div('Edmonton, Alberta', className='sidebar-subtitle'),
        ], className='sidebar-header'),
        
        # Navigation
        html.Nav([
            html.Div('Dashboard', className='nav-section-label'),
            html.Div([
                html.Span('📊', className='nav-item-icon'),
                html.Span('Overview'),
            ], className='nav-item active', id='nav-overview'),
            html.Div([
                html.Span('🗺️', className='nav-item-icon'),
                html.Span('Interactive Map'),
            ], className='nav-item', id='nav-map'),

            html.Div('Analysis', className='nav-section-label'),
            html.Div([
                html.Span('⚖️', className='nav-item-icon'),
                html.Span('Equity Analysis'),
            ], className='nav-item', id='nav-equity'),
            html.Div([
                html.Span('🏘️', className='nav-item-icon'),
                html.Span('Neighbourhoods'),
            ], className='nav-item', id='nav-neighbourhoods'),

            html.Div('Reference', className='nav-section-label'),
            html.Div([
                html.Span('📋', className='nav-item-icon'),
                html.Span('Methodology'),
            ], className='nav-item', id='nav-methodology'),
        ], className='sidebar-nav'),
        
        # Footer
        html.Div([
            html.Div('Data: StatsCan 2021 Census'),
            html.Div('Transit: ETS GTFS Feed'),
            html.Div('Map: OpenStreetMap'),
        ], className='sidebar-footer'),
    ], className='sidebar')


def build_header(title, subtitle=''):
    """Build the header bar."""
    return html.Div([
        html.Div([
            html.Div(title, className='header-title'),
            html.Div(subtitle, className='header-subtitle') if subtitle else None,
        ]),
        html.Div([
            html.Span(f'{len(df):,} Neighbourhoods', className='header-badge'),
            html.Span(f'{df["total_pop"].sum():,} Population', className='header-badge'),
        ], className='header-right'),
    ], className='header')

# ============================================================
# TAB 1: EXECUTIVE OVERVIEW
# ============================================================

def build_overview_tab():
    """Executive Overview - KPIs, charts, key insights."""
    
    # KPI calculations
    equity_score = round(df['accessibility'].mean(), 1)
    total_pop = f"{df['total_pop'].sum():,}"
    transit_deserts = len(df[df['accessibility'] < 20])
    avg_time = round(df['avg_travel_time'].mean(), 1)
    
    # Demographic equity chart
    demo_groups = {
        'All Populations': df['accessibility'].mean(),
        'Low Income Areas': df[df['low_income_pct'] > df['low_income_pct'].median()]['accessibility'].mean(),
        'Minority Areas': df[df['minority_pct'] > df['minority_pct'].median()]['accessibility'].mean(),
        'Senior Areas': df[df['senior_pct'] > df['senior_pct'].median()]['accessibility'].mean(),
    }
    
    bar_colors = [COLORS['green_400'] if v >= equity_score else COLORS['coral'] for v in demo_groups.values()]
    
    equity_bar = go.Figure(go.Bar(
        x=list(demo_groups.keys()),
        y=list(demo_groups.values()),
        marker_color=bar_colors,
        text=[f'{v:.1f}' for v in demo_groups.values()],
        textposition='outside',
        textfont=dict(size=13, family='Inter, sans-serif', color=COLORS['text_primary']),
    ))
    equity_bar.update_layout(
        title=dict(text='Transit Accessibility by Demographic Group', font=dict(size=14)),
        yaxis_title='Avg Accessibility Score',
        showlegend=False,
        height=340,
        **CHART_TEMPLATE['layout'],
    )
    equity_bar.add_hline(y=equity_score, line_dash='dash', line_color=COLORS['green_600'],
                         annotation_text=f'City Average: {equity_score}',
                         annotation_position='top left')
    
    # Accessibility distribution histogram
    hist = go.Figure(go.Histogram(
        x=df['accessibility'],
        nbinsx=25,
        marker_color=COLORS['green_400'],
        marker_line_color=COLORS['green_600'],
        marker_line_width=1,
    ))
    hist.update_layout(
        title=dict(text='Accessibility Score Distribution', font=dict(size=14)),
        xaxis_title='Accessibility Score',
        yaxis_title='Number of Neighbourhoods',
        height=340,
        **CHART_TEMPLATE['layout'],
    )
    
    # Top 10 transit deserts table
    deserts = df.nlargest(10, 'desert_score')[['DAUID', 'total_pop', 'accessibility', 'desert_score', 'low_income_pct']]
    deserts_table = dash_table.DataTable(
        data=deserts.to_dict('records'),
        columns=[
            {'name': 'DAUID', 'id': 'DAUID'},
            {'name': 'Population', 'id': 'total_pop', 'type': 'numeric', 'format': dash_table.Format.Format().group(True)},
            {'name': 'Access Score', 'id': 'accessibility', 'type': 'numeric'},
            {'name': 'Desert Score', 'id': 'desert_score', 'type': 'numeric'},
            {'name': 'Low Income %', 'id': 'low_income_pct', 'type': 'numeric'},
        ],
        style_header={
            'backgroundColor': COLORS['green_100'],
            'color': COLORS['green_900'],
            'fontWeight': '600',
            'fontSize': '0.8rem',
            'textTransform': 'uppercase',
            'letterSpacing': '0.03em',
            'border': 'none',
            'borderBottom': f'2px solid {COLORS["green_200"]}',
        },
        style_cell={
            'fontFamily': 'Inter, sans-serif',
            'fontSize': '0.85rem',
            'padding': '10px 14px',
            'border': 'none',
            'borderBottom': f'1px solid {COLORS["green_100"]}',
            'textAlign': 'left',
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'desert_score', 'filter_query': '{desert_score} > 50'},
                'color': COLORS['coral'],
                'fontWeight': '600',
            },
            {
                'if': {'column_id': 'accessibility', 'filter_query': '{accessibility} < 20'},
                'color': COLORS['coral'],
                'fontWeight': '600',
            },
        ],
        style_as_list_view=True,
    )
    
    return html.Div([
        html.H2('Executive Overview', className='page-title'),
        html.P('City-wide transit equity snapshot for Edmonton, Alberta.', className='page-description'),
        
        # KPI Row
        html.Div([
            build_kpi_card('Transit Equity Score', f'{equity_score}/100', '📊', 'green'),
            build_kpi_card('Population Served', total_pop, '👥', 'blue'),
            build_kpi_card('Transit Deserts', transit_deserts, '🏜️', 'alert'),
            build_kpi_card('Avg Travel Time', f'{avg_time} min', '⏱️', 'gold'),
        ], className='kpi-row'),
        
        # Row 2: Equity Bar + Histogram 
        html.Div([
            html.Div([
                html.Div([
                    html.Div('Equity by Demographics', className='card-title'),
                ], className='card-header'),
                html.Div([
                    dcc.Graph(figure=equity_bar, config={'displayModeBar': False}),
                ], className='card-body'),
            ], className='card'),
            html.Div([
                html.Div([
                    html.Div('Score Distribution', className='card-title'),
                ], className='card-header'),
                html.Div([
                    dcc.Graph(figure=hist, config={'displayModeBar': False}),
                ], className='card-body'),
            ], className='card'),
        ], className='grid-2col-equal'),
        
        # Row 3: Transit Deserts Table
        html.Div([
            html.Div([
                html.Div('🏜️ Top 10 Transit Deserts', className='card-title'),
            ], className='card-header'),
            html.Div([
                deserts_table,
            ], className='card-body'),
        ], className='card'),
    ], className='page-content tab-content')


# ============================================================
# TAB 2: INTERACTIVE MAP
# ============================================================

def build_map_tab():
    """Interactive choropleth map of Edmonton."""
    return html.Div([
        html.H2('Interactive Map', className='page-title'),
        html.P('Explore transit accessibility across 1,952 Edmonton neighbourhoods.', className='page-description'),
        
        # Map Controls
        html.Div([
            html.Div([
                html.Label('Color By:'),
                dcc.Dropdown(
                    id='map-metric',
                    options=[
                        {'label': 'Accessibility Score', 'value': 'accessibility'},
                        {'label': 'Average Travel Time', 'value': 'avg_travel_time'},
                        {'label': 'Low Income %', 'value': 'low_income_pct'},
                        {'label': 'Minority %', 'value': 'minority_pct'},
                        {'label': 'Senior %', 'value': 'senior_pct'},
                        {'label': 'Transit Desert Score', 'value': 'desert_score'},
                        {'label': 'Equity Index', 'value': 'equity_index'},
                        {'label': 'Population', 'value': 'total_pop'},
                    ],
                    value='accessibility',
                    clearable=False,
                    style={'width': '220px'},
                ),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
        ], className='map-controls'),
        
        # Map
        html.Div([
            dcc.Graph(id='main-map', style={'height': '600px'}),
        ]),
        
        # Detail Panel
        html.Div(id='map-detail-panel'),
        
    ], className='page-content tab-content')


# ============================================================
# TAB 3: EQUITY ANALYSIS
# ============================================================

def build_equity_tab():
    """Equity analysis with scatter plots and disparity metrics."""
    
    # Scatter: Low Income % vs Accessibility
    scatter = px.scatter(
        df,
        x='low_income_pct',
        y='accessibility',
        size='total_pop',
        color='accessibility',
        color_continuous_scale=CHOROPLETH_SCALE,
        hover_data=['DAUID', 'total_pop', 'low_income_pct'],
        labels={
            'low_income_pct': 'Low Income Population (%)',
            'accessibility': 'Transit Accessibility Score',
            'total_pop': 'Population',
        },
        title='Poverty vs. Transit Access',
    )
    scatter.update_layout(
        height=450,
        coloraxis_colorbar_title='Access Score',
        **CHART_TEMPLATE['layout'],
    )
    # Add trendline manually
    if len(df) > 2:
        z = np.polyfit(df['low_income_pct'].fillna(0), df['accessibility'].fillna(0), 1)
        p = np.poly1d(z)
        x_range = np.linspace(df['low_income_pct'].min(), df['low_income_pct'].max(), 100)
        scatter.add_trace(go.Scatter(
            x=x_range, y=p(x_range),
            mode='lines',
            line=dict(color=COLORS['coral'], width=2, dash='dash'),
            name='Trend',
            showlegend=True,
        ))
    
    # Disparity metrics
    top_20 = df.nlargest(int(len(df) * 0.2), 'accessibility')['accessibility'].mean()
    bottom_20 = df.nsmallest(int(len(df) * 0.2), 'accessibility')['accessibility'].mean()
    gap_ratio = round(top_20 / max(bottom_20, 1), 1)
    
    coverage = len(df[df['avg_travel_time'] <= 30]) / len(df) * 100
    
    # Gini coefficient
    access_sorted = np.sort(df['accessibility'].values)
    n = len(access_sorted)
    gini = (2 * np.sum((np.arange(1, n + 1)) * access_sorted) - (n + 1) * np.sum(access_sorted)) / (n * np.sum(access_sorted)) if np.sum(access_sorted) > 0 else 0
    gini = round(abs(gini), 3)
    
    return html.Div([
        html.H2('Equity Analysis', className='page-title'),
        html.P('How fairly is transit access distributed across Edmonton?', className='page-description'),
        
        # Disparity KPIs
        html.Div([
            build_kpi_card('Gini Coefficient', gini, '📐', 'amber' if gini > 0.3 else 'green'),
            build_kpi_card('Access Gap', f'{gap_ratio}x', '📊', 'alert' if gap_ratio > 2 else 'gold'),
            build_kpi_card('30-min Coverage', f'{coverage:.0f}%', '🎯', 'green' if coverage > 60 else 'alert'),
        ], className='grid-3col'),
        
        # Scatter plot
        html.Div([
            html.Div([
                html.Div('Poverty vs Transit Access Correlation', className='card-title'),
            ], className='card-header'),
            html.Div([
                dcc.Graph(figure=scatter, config={'displayModeBar': False}),
            ], className='card-body'),
        ], className='card', style={'marginBottom': '24px'}),
    ], className='page-content tab-content')


# ============================================================
# TAB 4: NEIGHBOURHOOD EXPLORER
# ============================================================

def build_neighbourhoods_tab():
    """Sortable data table with all neighbourhoods."""
    
    table_data = df[['DAUID', 'total_pop', 'low_income_pct', 'minority_pct', 'senior_pct',
                      'accessibility', 'avg_travel_time', 'desert_score', 'rating', 'access_rank']].copy()
    
    neighbourhood_table = dash_table.DataTable(
        id='neighbourhood-table',
        data=table_data.to_dict('records'),
        columns=[
            {'name': 'DAUID', 'id': 'DAUID'},
            {'name': 'Population', 'id': 'total_pop', 'type': 'numeric'},
            {'name': 'Low Income %', 'id': 'low_income_pct', 'type': 'numeric'},
            {'name': 'Minority %', 'id': 'minority_pct', 'type': 'numeric'},
            {'name': 'Senior %', 'id': 'senior_pct', 'type': 'numeric'},
            {'name': 'Access Score', 'id': 'accessibility', 'type': 'numeric'},
            {'name': 'Avg Travel (min)', 'id': 'avg_travel_time', 'type': 'numeric'},
            {'name': 'Desert Score', 'id': 'desert_score', 'type': 'numeric'},
            {'name': 'Rating', 'id': 'rating'},
            {'name': 'Rank', 'id': 'access_rank', 'type': 'numeric'},
        ],
        sort_action='native',
        filter_action='native',
        page_size=20,
        page_action='native',
        style_header={
            'backgroundColor': COLORS['green_100'],
            'color': COLORS['green_900'],
            'fontWeight': '600',
            'fontSize': '0.75rem',
            'textTransform': 'uppercase',
            'letterSpacing': '0.03em',
            'border': 'none',
            'borderBottom': f'2px solid {COLORS["green_200"]}',
        },
        style_cell={
            'fontFamily': 'Inter, sans-serif',
            'fontSize': '0.82rem',
            'padding': '10px 12px',
            'border': 'none',
            'borderBottom': f'1px solid {COLORS["green_100"]}',
            'textAlign': 'left',
            'maxWidth': '120px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'rating', 'filter_query': '{rating} = "Excellent"'},
                'color': COLORS['green_600'],
                'fontWeight': '600',
            },
            {
                'if': {'column_id': 'rating', 'filter_query': '{rating} = "Good"'},
                'color': COLORS['green_400'],
                'fontWeight': '500',
            },
            {
                'if': {'column_id': 'rating', 'filter_query': '{rating} = "Poor"'},
                'color': COLORS['coral'],
                'fontWeight': '600',
            },
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': COLORS['green_50'],
            },
        ],
        style_as_list_view=True,
    )
    
    return html.Div([
        html.H2('Neighbourhood Explorer', className='page-title'),
        html.P('Search, sort, and compare all 1,952 Edmonton neighbourhoods.', className='page-description'),
        
        html.Div([
            html.Div([
                html.Div('All Neighbourhoods', className='card-title'),
            ], className='card-header'),
            html.Div([
                neighbourhood_table,
            ], className='card-body'),
        ], className='card'),
    ], className='page-content tab-content')


# ============================================================
# TAB 5: METHODOLOGY
# ============================================================

def build_methodology_tab():
    """Methodology and data sources page."""
    return html.Div([
        html.H2('Methodology & Data Sources', className='page-title'),
        html.P('Transparency in how transit equity scores are calculated.', className='page-description'),
        
        html.Div([
            html.H3('📦 Data Sources'),
            html.P('This dashboard combines three primary datasets:'),
            html.Ul([
                html.Li([html.Strong('Statistics Canada 2021 Census: '), 
                         'Population, low income, visible minorities, and seniors data at the Dissemination Area (DA) level for the Edmonton Census Metropolitan Area.']),
                html.Li([html.Strong('Edmonton Transit Service (ETS) GTFS: '), 
                         'General Transit Feed Specification data containing all bus and LRT routes, stops, and schedules.']),
                html.Li([html.Strong('OpenStreetMap (OSM): '), 
                         'Street network data for Edmonton, used for pedestrian walking segments in multi-modal routing.']),
            ]),
        ], className='methodology-section'),
        
        html.Div([
            html.H3('🧮 Accessibility Score'),
            html.P('Measures what percentage of the city each neighbourhood can reach within a given time threshold using public transit.'),
            html.Div('accessibility_i = COUNT(DAs reachable within T minutes from DA_i) / TOTAL_DAs × 100', className='formula-block'),
            html.P('Default threshold T = 45 minutes. Higher scores indicate better transit connectivity.'),
        ], className='methodology-section'),
        
        html.Div([
            html.H3('⚖️ Transit Equity Index'),
            html.P('Combines accessibility with demographic vulnerability to identify areas where vulnerable populations have good or poor transit access.'),
            html.Div('equity_i = accessibility_i × vulnerability_weight_i', className='formula-block'),
            html.Div('vulnerability_weight = normalized(low_income% + minority% + senior%)', className='formula-block'),
        ], className='methodology-section'),
        
        html.Div([
            html.H3('🏜️ Transit Desert Score'),
            html.P('Identifies neighbourhoods that are BOTH underserved by transit AND home to vulnerable populations.'),
            html.Div('desert_score_i = (1 - accessibility_i / 100) × vulnerability_weight_i', className='formula-block'),
            html.P('Higher desert scores indicate the most critical areas for transit investment.'),
        ], className='methodology-section'),
        
        html.Div([
            html.H3('📐 Gini Coefficient'),
            html.P('A statistical measure of inequality in transit access distribution across the city. Ranges from 0 (perfectly equal) to 1 (maximally unequal).'),
        ], className='methodology-section'),
        
        html.Div([
            html.H3('🔧 Technical Stack'),
            html.Ul([
                html.Li('Routing Engine: R5py (Conveyal R5) with Java 21'),
                html.Li('Travel Time Computation: Origin-Destination matrix for all 1,952 DA centroids'),
                html.Li('Dashboard: Plotly Dash with custom "River Valley" CSS theme'),
                html.Li('Maps: Plotly Mapbox choropleth'),
            ]),
        ], className='methodology-section'),
        
    ], className='page-content tab-content')


# ============================================================
# MAIN LAYOUT
# ============================================================

app.layout = html.Div([
    # Hidden store for current tab
    dcc.Store(id='current-tab', data='overview'),
    
    # Sidebar
    build_sidebar(),
    
    # Main content
    html.Div([
        build_header('Edmonton Transit Equity Dashboard', 'Powered by StatsCan 2021 Census + ETS GTFS'),
        html.Div(id='tab-content'),
    ], className='main-content'),
], className='app-container')


# ============================================================
# CALLBACKS
# ============================================================

# Tab navigation
@callback(
    Output('current-tab', 'data'),
    [Input('nav-overview', 'n_clicks'),
     Input('nav-map', 'n_clicks'),
     Input('nav-equity', 'n_clicks'),
     Input('nav-neighbourhoods', 'n_clicks'),
     Input('nav-methodology', 'n_clicks')],
    prevent_initial_call=False,
)
def switch_tab(c1, c2, c3, c4, c5):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]['prop_id'] == '.':
        return 'overview'
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    mapping = {
        'nav-overview': 'overview',
        'nav-map': 'map',
        'nav-equity': 'equity',
        'nav-neighbourhoods': 'neighbourhoods',
        'nav-methodology': 'methodology',
    }
    return mapping.get(trigger, 'overview')


# Render tab content
@callback(
    Output('tab-content', 'children'),
    Input('current-tab', 'data'),
)
def render_tab(tab):
    if tab == 'overview':
        return build_overview_tab()
    elif tab == 'map':
        return build_map_tab()
    elif tab == 'equity':
        return build_equity_tab()
    elif tab == 'neighbourhoods':
        return build_neighbourhoods_tab()
    elif tab == 'methodology':
        return build_methodology_tab()
    return build_overview_tab()


# Map callback
@callback(
    Output('main-map', 'figure'),
    Input('map-metric', 'value'),
)
def update_map(metric):
    """Update the map based on selected metric."""
    labels = {
        'accessibility': 'Accessibility Score',
        'avg_travel_time': 'Avg Travel Time (min)',
        'low_income_pct': 'Low Income %',
        'minority_pct': 'Minority %',
        'senior_pct': 'Senior %',
        'desert_score': 'Transit Desert Score',
        'equity_index': 'Equity Index',
        'total_pop': 'Population',
    }
    
    # Real scatter mapbox with centroid coordinates
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
        hover_name='neighbourhood',  # Show neighbourhood name instead of DAUID
        hover_data={
            'DAUID': True,
            'total_pop': ':,',
            'accessibility': ':.1f',
            'avg_travel_time': ':.1f',
            'low_income_pct': ':.1f',
            'marker_size': False,
            'lat': False,
            'lon': False,
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
    )
    
    return fig


# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    print("\n🌲 Edmonton Transit Equity Dashboard")
    print("   River Valley Theme | Dash + Plotly")
    print(f"   Loaded {len(df):,} neighbourhoods | {df['total_pop'].sum():,} population")
    print(f"\n   Open: http://localhost:8050\n")
    app.run(debug=True, host='0.0.0.0', port=8050)
