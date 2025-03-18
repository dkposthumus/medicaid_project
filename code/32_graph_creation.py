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
state_level = state_level[state_level['usa_state_dummy'] == 1]

######################################################################################################################################
# Changes in medicaid enrollment over time for R states
######################################################################################################################################
# fill missing observations of pct_enrollment with 0
for count_var, pct_var, title, data_min in zip(['num_medicaid_chip_gov', 'num_medicaid_gov', 
                               'total_medicaid_enrollees_acs'],
                              ['pct_enrollment_medicaid_chip_gov', 'pct_enrollment_medicaid_gov', 
                               'pct_enrollment_medicaid_acs'],
                               ['Medicaid and Chip (Medicaid.gov)',
                                'Medicaid (Medicaid.gov)', 'Medicaid (ACS 5-Year)'],
                                [2017, 2017, 2012]):
    min_year = data_min
    r_states = state_level[state_level['year'].isin([2016, 2020, 2024])].groupby('state').filter(
        lambda g: all(g['republican_pres_votes'] > g['democratic_pres_votes'])
    )['state'].unique()
    #print(r_states)
    df_r_states = state_level[state_level['state'].isin(r_states)]
    df_r_states[pct_var] = df_r_states[pct_var].fillna(0)
    df_r_states = df_r_states[(df_r_states['year'] >= min_year) & (df_r_states['year'] <= 2023)]

    df_r_states_grouped = df_r_states.groupby('year').agg({
        count_var: 'sum',  # Total number of enrollments
        pct_var: 'mean'  # Average percentage enrollment
    }).reset_index()

    fig, ax1 = plt.subplots(figsize=(10, 6))
    # Left y-axis (Medicaid enrollment numbers)
    color1 = 'tab:blue'
    ax1.set_xlabel("Year")
    ax1.set_ylabel(f"Total {title} Enrollment (millions)", color=color1)
    ax1.plot(df_r_states_grouped['year'], df_r_states_grouped[count_var] / 1e6, 
         marker='o', linestyle='-', color=color1, label=f"{title} Enrollment (millions)")
    ax1.tick_params(axis='y', labelcolor=color1)
    # Create second y-axis (percentage of Medicaid enrollment)
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel("Percentage of Medicaid Enrollment (%)", color=color2)
    ax2.plot(df_r_states_grouped['year'], df_r_states_grouped[pct_var], 
         marker='s', linestyle='--', color=color2, label="Medicaid and CHIP Enrollment (%/of population)")
    ax2.tick_params(axis='y', labelcolor=color2)
    # Title and grid
    plt.title(f"{title} Enrollment Trends in Republican States ({min_year}-2023)")
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    # Add legends
    leg1 = ax1.legend(loc='upper left', bbox_to_anchor=(0, 1)) 
    leg2 = ax2.legend(loc='upper left', bbox_to_anchor=(0, 0.88))  
    plt.close()

    # now reproduce the same visual, with a different definition of 'r' (as defined by partisan control)
    df_r_states = state_level[state_level['total_gov'] == 'r']
    # fill missing observations of pct_enrollment with 0
    df_r_states[pct_var] = df_r_states[pct_var].fillna(0)
    df_r_states = df_r_states[(df_r_states['year'] >= min_year) & (df_r_states['year'] <= 2023)]

    for year in range(min_year, 2024):
        year_df = df_r_states[df_r_states['year'] == year]
        #print(year_df['state'].unique())

    df_r_states_grouped = df_r_states.groupby('year').agg({
        count_var: 'sum',  # Total number of enrollments
        pct_var: 'mean'  # Average percentage enrollment
    }).reset_index()

    fig, ax1 = plt.subplots(figsize=(10, 6))
    # Left y-axis (Medicaid enrollment numbers)
    color1 = 'tab:blue'
    ax1.set_xlabel("Year")
    ax1.set_ylabel(f"Total {title} Enrollment (millions)", color=color1)
    ax1.plot(df_r_states_grouped['year'], df_r_states_grouped[count_var] / 1e6, 
         marker='o', linestyle='-', color=color1, label=f"{title} Enrollment (millions)")
    ax1.tick_params(axis='y', labelcolor=color1)
    # Create second y-axis (percentage of Medicaid enrollment)
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel(f"Percentage of {title} Enrollment (%)", color=color2)
    ax2.plot(df_r_states_grouped['year'], df_r_states_grouped[pct_var], 
         marker='o', linestyle='-', color=color2, label=f"{title} Enrollment (%/of population)")
    ax2.tick_params(axis='y', labelcolor=color2)
    # Title and grid
    plt.title(f"{title} Enrollment Trends in Republican States ({min_year}-2023)")
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='center left', 
               bbox_to_anchor=(1.2, 0.5))
    plt.show()

    # now try to decompose these results
    baseline_states = state_level[(state_level['year'] == min_year) & (state_level['total_gov'] == 'r')]['state'].unique()
    # Create the fixed composition (counterfactual) data by filtering all years to these states:
    df_fixed = state_level[state_level['state'].isin(baseline_states)].copy()
    df_fixed[pct_var] = df_fixed[pct_var].fillna(0)
    df_fixed = df_fixed[(df_fixed['year'] >= min_year) & (df_fixed['year'] <= 2023)]
    
    # Group by year for the fixed composition data:
    df_fixed_grouped = df_fixed.groupby('year').agg({
        count_var: 'sum',   # Sum enrollment for fixed states
        pct_var: 'mean'     # Mean percentage enrollment for fixed states
    }).reset_index()
    
    # Now compute the "actual" aggregated values using your current definition of r states.
    # (This is the same as before but using state_level where total_gov == 'r'.)
    df_actual = state_level[state_level['total_gov'] == 'r'].copy()
    df_actual[pct_var] = df_actual[pct_var].fillna(0)
    df_actual = df_actual[(df_actual['year'] >= min_year) & (df_actual['year'] <= 2023)]
    df_actual_grouped = df_actual.groupby('year').agg({
        count_var: 'sum',
        pct_var: 'mean'
    }).reset_index()
    
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
    
    plt.title(f"{title} Enrollment Trends in Republican States ({min_year}-2023)")
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
for count_var, pct_var, title, min_year in zip(['num_medicaid_chip_gov', 'num_medicaid_gov', 
                               'total_medicaid_enrollees_acs'],
                              ['pct_enrollment_medicaid_chip_gov', 'pct_enrollment_medicaid_gov', 
                               'pct_enrollment_medicaid_acs'],
                               ['Medicaid and Chip (Medicaid.gov)',
                                'Medicaid (Medicaid.gov)', 'Medicaid (ACS 5-Year)'],
                                [2017, 2017, 2012]):
    # now reproduce the same visual, with a different definition of 'r' (as defined by partisan control)
    df_r_states = state_level[state_level['total_gov'] == 'r']
    # fill missing observations of pct_enrollment with 0
    df_r_states[pct_var] = df_r_states[pct_var].fillna(np.nan)
    df_r_states = df_r_states[(df_r_states['year'] >= min_year) & (df_r_states['year'] <= 2023)]
    for year in range(min_year, 2024):
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
plt.title("Enrollment Trends in Republican States (2012-2023), by Data Series")
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2, labels1 + labels2, loc='center left', 
               bbox_to_anchor=(1.2, 0.5))
plt.show()

######################################################################################################################################
# 
######################################################################################################################################
