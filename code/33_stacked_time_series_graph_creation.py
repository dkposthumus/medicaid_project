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

election_years = {
    2012: [2012, 2013, 2014, 2015],
    2016: [2016, 2017, 2018, 2019], 
    2020: [2020, 2021, 2022, 2023],
    2024: [2024]
}

for df, label, geovar in zip([state_level, county_level], 
                             ['States', 'Counties'],
                              ['state_name', 'county-state', 'cd-state']):
    # Create a mapping of state-year to 'r' classification based on presidential vote
    df['r_state_check'] = (df['republican_pres_votes'] > df['democratic_pres_votes']).astype(int)
    df = df[df['year'].between(2012, 2024)]
    df['r_state'] = np.nan  # Initialize a new column
    for election_year, affected_years in election_years.items():
        trump_states = df[(df['year'] == election_year) &
                               (df['republican_pres_votes'] > df['democratic_pres_votes'])][geovar].unique()
        df.loc[df['year'].isin(affected_years) & df[geovar].isin(trump_states), 'r_state'] = 'r'
    df['r_state'].fillna('d', inplace=True)
    # we want a stacked time-series graph
    num_cols = ['num_male_19_medicaid_acs', 'num_male_19_64_medicaid_acs',
       'num_male_65_medicaid_acs', 'num_female_19_medicaid_acs',
       'num_female_19_64_medicaid_acs', 'num_female_65_medicaid_acs']
    labels = ['Male Children', 'Male Adults', 'Male 65+',
          'Female Children', 'Female Adults', 'Female 65+']
    for value, party_label in zip(['r', 'd'], ['Republican', 'Democratic']):
        filtered = df[df['year'].between(2012, 2023)]
        filtered = filtered[filtered['r_state'] == value]
        collapsed = filtered.groupby('year')[num_cols].sum().reset_index()

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.stackplot(collapsed['year'], collapsed[num_cols].T, labels=labels, alpha=0.7)
        # Formatting the plot
        ax.set_title(f"Stacked Area Graph of Medicaid Enrollment by Age and Gender for {party_label} {label}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of Enrollees")
        ax.legend(title="Categories", loc='upper left')
        ax.grid(True, linestyle='--', alpha=0.6)
        # Show the plot
        plt.close()

        collapsed_norm = collapsed.copy()
        collapsed_norm[num_cols] = collapsed_norm[num_cols].div(collapsed_norm[num_cols].sum(axis=1), axis=0)
        # Plot stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        bottom = np.zeros(len(collapsed_norm['year']))
        ax.stackplot(collapsed['year'], collapsed_norm[num_cols].T, labels=labels, alpha=0.7)
        # Formatting the plot
        ax.set_title(f"Share of Medicaid Enrollment by Age and Gender for {party_label} {label}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Share of Total Enrollees")
        ax.legend(title="Categories", loc='upper left')
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        # Show the plot
        plt.show()

