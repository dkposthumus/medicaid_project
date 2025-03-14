import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import geopandas as gpd

home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
shapefiles = (data / 'shapefiles')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
output = (work_dir / 'output')
code = Path.cwd() 

## pull in county-level and state-level master data 
state_level = pd.read_csv(f'{clean_data}/master_state_level.csv')

# our state_level dataste includes territories; we don't want this. 
state_level = state_level[state_level['usa_state_dummy'] == 1]
state_level = state_level.dropna(subset=['republican_pres_votes'])

## pull in USA state-level shapefiles
path = f'{shapefiles}/tl_2024_us_state/tl_2024_us_state.shp'
states_gdf = gpd.read_file(path)
states_gdf["NAME"] = states_gdf["NAME"].str.lower()
states_gdf = states_gdf[~states_gdf['NAME'].isin([
    'united states virgin islands', 
    'commonwealth of the northern mariana islands',
    'guam', 
    'american samoa', 
    'puerto rico'
])]

######################################################################################################################################
# State-Level Map of Where Greatest Change in Medicaid Enrollment
######################################################################################################################################
# first reshape dataframe wide 
wide = state_level.pivot(
    index='state', 
    columns='year', 
    values='pct_enrollment_medicaid'
).reset_index()
# Rename the pivoted columns for clarity:
wide.rename(columns={2012: 'pct_2012', 2024: 'pct_2024'}, inplace=True)
# Compute difference (may produce NaN if data is missing for a given state/year)
wide['pct_diff'] = wide['pct_2024'] - wide['pct_2012']
# merge data with shapefile
merged_gdf = states_gdf.merge(wide, left_on='NAME', right_on='state', how='left')

fig, ax = plt.subplots(figsize=(12, 8))
merged_gdf.plot(
    column='pct_diff',    # difference column to color by
    cmap='OrRd',          # color map (choose any you like, e.g., 'YlGnBu', 'viridis')
    legend=True,          # show the color scale
    edgecolor='black',    # outline for states
    linewidth=0.4,
    ax=ax
)
# Add a title and remove axis clutter
ax.set_title('Change in Medicaid Enrollment (%) from 2012 to 2024')
ax.set_axis_off()
plt.show()