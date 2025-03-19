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
# create joint cd-state identifier
cd_level['cd119'] = cd_level['cd119'].astype(str)
cd_level['cd-state'] = (cd_level['cd119'] + '-' + cd_level['state_name'])

######################################################################################################################################
# Changes in medicaid enrollment over time for R states
######################################################################################################################################
# Define election-year mappings
election_years = {
    2012: [2012, 2013, 2014, 2015],
    2016: [2016, 2017, 2018, 2019], 
    2020: [2020, 2021, 2022, 2023],
    2024: [2024]
}

# fill missing observations of pct_enrollment with 0
for df, label, geovar, ct_var, ct_var_chip in zip([state_level, county_level], 
                             ['States', 'Counties'],
                              ['state_name', 'county-state', 'cd-state'],
                              ['num_medicaid_gov', 'num_county_medicaid_gov'],
                              ['num_medicaid_chip_gov', 'num_county_medicaid_chip_gov']):
    # Create a mapping of state-year to 'r' classification based on presidential vote
    df['r_state_check'] = (df['republican_pres_votes'] > df['democratic_pres_votes']).astype(int)
    df = df[df['year'].between(2012, 2024)]
    df['r_state'] = np.nan  # Initialize a new column
    for election_year, affected_years in election_years.items():
        trump_states = df[(df['year'] == election_year) &
                               (df['republican_pres_votes'] > df['democratic_pres_votes'])][geovar].unique()
        df.loc[df['year'].isin(affected_years) & df[geovar].isin(trump_states), 'r_state'] = 'r'

    for var, acs_var in zip([ct_var, 'pct_enrollment_medicaid_gov'],
                            ['total_medicaid_enrollees_acs', 'pct_enrollment_medicaid_acs']):
        df_filtered = df[~((df['year'].between(2017, 2020)) & 
                          (df[[var, acs_var]].isna().any(axis=1)))]
        df_filtered = df_filtered[~((df_filtered['year'].between(2017, 2020)) &
                            (df_filtered[[var, acs_var]].eq(0).any(axis=1)))]
        ratio_approx = (df_filtered[df_filtered['year'].between(2017, 2020)][var] /
            df_filtered[df_filtered['year'].between(2017, 2020)][acs_var]).mean()
        print(f'ratio for imputing 2012-2016 values of {var} data for {geovar}: {ratio_approx}')
        df.loc[df['year'].between(2012, 2016), var] = (
            df[acs_var] * ratio_approx)

    df.to_csv(f'{clean_data}/check.csv')

    for count_var, pct_var, title, data_min in zip([ct_var],
                              ['pct_enrollment_medicaid_gov'], ['Medicaid (Medicaid.gov)'], [2012]):
        min_year = data_min
        # now reproduce the same visual, with a different definition of 'r' (as defined by partisan control)
        df_r_states = df[df['r_state'] == 'r']
        df_r_states[pct_var] = df_r_states[pct_var].fillna(0)
        df_r_states = df_r_states[(df_r_states['year'] >= min_year) & (df_r_states['year'] <= 2024)]

        df_r_states_grouped = df_r_states.groupby('year').agg({
            count_var: 'sum',  # Total number of enrollments
            'population': 'sum'  # Total population
        }).reset_index()
        df_r_states_grouped[pct_var] = df_r_states_grouped[count_var] / df_r_states_grouped['population']

        fig, ax1 = plt.subplots(figsize=(10, 6))
        color1 = 'tab:blue'
        ax1.set_xlabel("Year")
        ax1.set_ylabel(f"Total {title} Enrollment (millions)", color=color1)
        ax1.plot(df_r_states_grouped['year'], df_r_states_grouped[count_var] / 1e6, 
            marker='o', linestyle='-', color=color1, label=f"{title} Enrollment (millions)")
        ax1.tick_params(axis='y', labelcolor=color1)
    
        ax2 = ax1.twinx()
        color2 = 'tab:red'
        ax2.set_ylabel(f"Percentage of {title} Enrollment (%)", color=color2)
        ax2.plot(df_r_states_grouped['year'], df_r_states_grouped[pct_var], 
             marker='o', linestyle='-', color=color2, label=f"{title} Enrollment (% of population)")
        ax2.tick_params(axis='y', labelcolor=color2)
    
        plt.title(f"{title} Enrollment Trends in Republican {label} ({min_year}-2024)")
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(handles1 + handles2, labels1 + labels2, loc='center left', bbox_to_anchor=(1.2, 0.5))
        plt.show()

        # now try to decompose these results
        baseline_states = df[(df['year'] == min_year) & (df['r_state'] == 'r')][geovar].unique()
        # Create the fixed composition (counterfactual) data by filtering all years to these states:
        df_fixed = df[df[geovar].isin(baseline_states)].copy()
        df_fixed[pct_var] = df_fixed[pct_var].fillna(0)
        df_fixed = df_fixed[(df_fixed['year'] >= min_year) & (df_fixed['year'] <= 2024)]
    
        # Group by year for the fixed composition data:
        df_fixed_grouped = df_fixed.groupby('year').agg({
            count_var: 'sum',  # Total number of enrollments
            'population': 'sum'  # Total population
        }).reset_index()
        df_fixed_grouped[pct_var] = df_fixed_grouped[count_var] / df_fixed_grouped['population']

        # Now compute the "actual" aggregated values using your current definition of r states.
        # (This is the same as before but using state_level where total_gov == 'r'.)
        df_actual = df[df['r_state'] == 'r'].copy()
        df_actual[pct_var] = df_actual[pct_var].fillna(0)
        df_actual = df_actual[(df_actual['year'] >= min_year) & (df_actual['year'] <= 2024)]
        df_actual_grouped = df_actual.groupby('year').agg({
            count_var: 'sum',
            'population': 'sum'
        }).reset_index()
        df_actual_grouped[pct_var] = df_actual_grouped[count_var] / df_actual_grouped['population']
    
        # Merge the two aggregated datasets on year:
        df_compare = df_actual_grouped.merge(df_fixed_grouped, on='year', suffixes=('_actual', '_fixed'))
    
        # Compute the difference: actual minus fixed composition
        df_compare['difference_count'] = df_compare[f'{count_var}_actual'] - df_compare[f'{count_var}_fixed']
        df_compare['difference_pct'] = df_compare[f'{pct_var}_actual'] - df_compare[f'{pct_var}_fixed']
    
        # ------------------------------
        # Now plot the fixed composition (counterfactual) and the difference over time
        # ------------------------------
        fig, ax1 = plt.subplots(figsize=(10, 6))
        # Left y-axis for enrollment numbers:
        color1 = 'tab:blue'
        ax1.set_xlabel("Year")
        ax1.set_ylabel(f"Total {title} Enrollment (millions)", color=color1)
        # Plot fixed composition enrollment (values from the 2017 state list) converted to millions:
        ax1.plot(df_compare['year'], df_compare[f'{count_var}_fixed'] / 1e6,
             marker='o', linestyle='-', color=color1, label=f"Fixed Enrollment (2017)")
        # Plot the difference (actual minus fixed)
        ax1.plot(df_compare['year'], df_compare['difference_count'] / 1e6,
             marker='s', linestyle='--', color=color1, label="(Dynamic - Fixed) Enrollment")
        ax1.tick_params(axis='y', labelcolor=color1)
    
        # Right y-axis for percentage measure:
        ax2 = ax1.twinx()
        color2 = 'tab:red'
        ax2.set_ylabel(f"Percentage of {title} Enrollment (%)", color=color2)
        ax2.plot(df_compare['year'], df_compare[f'{pct_var}_fixed'],
             marker='o', linestyle='-', color=color2, label="Fixed Enrollment (%) (2017)")
        ax2.plot(df_compare['year'], df_compare['difference_pct'],
             marker='s', linestyle='--', color=color2, label="(Dynamic - Fixed) Enrollment (%)")
        ax2.tick_params(axis='y', labelcolor=color2)
    
        plt.title(f"{title} Enrollment Trends in Republican {label} ({min_year}-2024)")
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
        ax1.axhline(y=0, color=color1, linestyle='--')
        ax2.axhline(y=0, color=color2, linestyle='--')

        # Combine legends from both axes and position them off the graph further to the right
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(handles1 + handles2, labels1 + labels2, loc='center left', 
               bbox_to_anchor=(1.2, 0.5))
        plt.show()

    fig, ax1 = plt.subplots(figsize=(10, 6))
    color1 = 'tab:blue'
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    for count_var, pct_var, title, min_year, max_year in zip([ct_var_chip, ct_var, 
                               'total_medicaid_enrollees_acs'],
                              ['pct_enrollment_medicaid_chip_gov', 'pct_enrollment_medicaid_gov', 
                               'pct_enrollment_medicaid_acs'],
                               ['Medicaid and Chip (Medicaid.gov)',
                                'Medicaid (Medicaid.gov)', 'Medicaid (ACS 5-Year)'],
                                [2017, 2012, 2012], [2024, 2024, 2023]):
        # now reproduce the same visual, with a different definition of 'r' (as defined by partisan control)
        df_r_states = df[df['r_state'] == 'r']
        # fill missing observations of pct_enrollment with 0
        df_r_states[pct_var] = df_r_states[pct_var].fillna(np.nan)
        df_r_states = df_r_states[(df_r_states['year'] >= min_year) & (df_r_states['year'] <= max_year)]
        for year in range(min_year, 2025):
            year_df = df_r_states[df_r_states['year'] == year]
        #print(year_df['state'].unique())
        df_r_states_grouped = df_r_states.groupby('year').agg({
            count_var: 'sum',  # Total number of enrollments
            pct_var: 'mean'  # Average percentage enrollment
        }).reset_index()
        ax1.plot(df_r_states_grouped['year'], df_r_states_grouped[count_var] / 1e6, 
            marker='o', linestyle='-', label=f"{title} (millions)")
        ax2.plot(df_r_states_grouped['year'], df_r_states_grouped[pct_var], 
            marker='s', linestyle='--', label=f'{title} (%)')
    
    ax1.set_xlabel("Year")
    ax1.set_ylabel(f"Total {title} Enrollment (millions)", color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax2.set_ylabel(f"Percentage of {title} Enrollment (%)", color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    plt.title(f"Enrollment Trends in Republican {label} (2012-2024), by Data Series - {label}")
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='center left', 
               bbox_to_anchor=(1.2, 0.5))
    plt.show()

######################################################################################################################################
# 
######################################################################################################################################
