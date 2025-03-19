import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
output = (work_dir / 'output')
code = Path.cwd() 

## pull in county-level and state-level master data 
state_level = pd.read_csv(f'{clean_data}/master_state_level.csv')
county_level = pd.read_csv(f'{clean_data}/master_county.csv')
# for county-level, create joint county-state identifier
county_level['county-state'] = (county_level['county_name'] + '-' + county_level['state_name'])
cd_level = pd.read_csv(f'{clean_data}/master_cd.csv')  

def compute_population_shifts(df, geovar):
    df['r_state_check'] = (df['republican_pres_votes'] > df['democratic_pres_votes']).astype(int)
    df = df[df['year'].between(2012, 2024)]
    df['r_state'] = np.nan  # Initialize a new column
    for election_year, affected_years in election_years.items():
        trump_states = df[(df['year'] == election_year) &
                               (df['republican_pres_votes'] > df['democratic_pres_votes'])][geovar].unique()
        df.loc[df['year'].isin(affected_years) & df[geovar].isin(trump_states), 'r_state'] = 'r'
    """
    Identifies population in counties/states that shift from 'r' to '' in r_state each year.
    """
    df = df.sort_values(by=['year', geovar])  # Ensure chronological order
    # Identify shifts: 'r' in year t but '' (NaN) in year t+1
    df['r_to_blank'] = (df.groupby(geovar)['r_state']
                          .shift(1)
                          .eq('r') & df['r_state'].isna())
    # Identify shifts: '' (NaN) in year t but 'r' in year t+1
    df['blank_to_r'] = (df.groupby(geovar)['r_state']
                          .shift(1)
                          .isna() & df['r_state'].eq('r'))
    # Aggregate total population affected by year
    population_r_to_blank = df[df['r_to_blank']].groupby('year')['population'].sum().reset_index()
    population_r_to_blank = population_r_to_blank[population_r_to_blank['year'] >= 2016]
    population_blank_to_r = df[df['blank_to_r']].groupby('year')['population'].sum().reset_index()
    population_blank_to_r = population_blank_to_r[population_blank_to_r['year'] >= 2016]

    return population_r_to_blank, population_blank_to_r

# Define election-year mappings
election_years = {
    2012: [2012, 2013, 2014, 2015],
    2016: [2016, 2017, 2018, 2019], 
    2020: [2020, 2021, 2022, 2023],
    2024: [2024]
}
state_population_r_to_blank, state_population_blank_to_r = compute_population_shifts(state_level, 'state_name')
county_population_r_to_blank, county_population_blank_to_r = compute_population_shifts(county_level, 'county-state')
# --------------------
# Plot the results
# --------------------
plt.figure(figsize=(10, 6))
# Plot 'r' to '' (losing Republican status)
plt.plot(state_population_r_to_blank['year'], state_population_r_to_blank['population'] / 1e6, 
         marker='o', linestyle='-', label="States (r → '')")
plt.plot(county_population_r_to_blank['year'], county_population_r_to_blank['population'] / 1e6, 
         marker='s', linestyle='--', label="Counties (r → '')")
# Plot '' to 'r' (gaining Republican status)
plt.plot(state_population_blank_to_r['year'], state_population_blank_to_r['population'] / 1e6, 
         marker='o', linestyle=':', label="States ('' → r)")
plt.plot(county_population_blank_to_r['year'], county_population_blank_to_r['population'] / 1e6, 
         marker='s', linestyle=':', label="Counties ('' → r)")
# Labels and title
plt.xlabel("Year")
plt.ylabel("Total Population (millions)")
plt.title("Population of Areas Shifting 'r' ↔ '' by Year")
plt.legend()
plt.grid(True)
# Show plot
plt.show()

# now plot differences
state_population_diff = state_population_r_to_blank.merge(state_population_blank_to_r, on='year', suffixes=('_r_to_blank', '_blank_to_r'), how='outer')
state_population_diff = state_population_diff.fillna(0)
state_population_diff['net republican gain population - state'] = state_population_diff['population_blank_to_r'] - state_population_diff['population_r_to_blank']

county_population_diff = county_population_r_to_blank.merge(county_population_blank_to_r, on='year', suffixes=('_r_to_blank', '_blank_to_r'), how='outer')
county_population_diff = county_population_diff.fillna(0)
county_population_diff['net republican gain population - county'] = county_population_diff['population_blank_to_r'] - county_population_diff['population_r_to_blank']

plt.figure(figsize=(10, 6))
# Plot 'r' to '' (losing Republican status)
plt.plot(state_population_diff['year'], state_population_diff['net republican gain population - state'] / 1e6, 
         marker='o', linestyle='-', label="Net Change in Republican States' Populations (R gains - R losses)")
plt.plot(county_population_diff['year'], county_population_diff['net republican gain population - county'] / 1e6, 
         marker='s', linestyle='--', label="Net Change in Republican Counties' Populations (R gains - R losses)")
# Labels and title
plt.xlabel("Year")
plt.ylabel("Total Population (millions)")
plt.title("Net Changes in Republican States'/Counties' Populations by Election Year")
plt.legend()
plt.grid(True)
plt.show()