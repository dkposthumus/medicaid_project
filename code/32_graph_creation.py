import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

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
r_states = state_level[state_level['year'].isin([2016, 2020, 2024])].groupby('state').filter(
    lambda g: all(g['republican_pres_votes'] > g['democratic_pres_votes'])
)['state'].unique()
print(r_states)
df_r_states = state_level[state_level['state'].isin(r_states)]
# fill missing observations of pct_enrollment with 0
df_r_states['pct_enrollment_medicaid'] = df_r_states['pct_enrollment_medicaid'].fillna(0)
df_r_states = df_r_states[(df_r_states['year'] >= 2012) & (df_r_states['year'] <= 2024)]

df_r_states_grouped = df_r_states.groupby('year').agg({
    'num_enrollment_medicaid': 'sum',  # Total number of enrollments
    'pct_enrollment_medicaid': 'mean'  # Average percentage enrollment
}).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 6))

# Left y-axis (Medicaid enrollment numbers)
color1 = 'tab:blue'
ax1.set_xlabel("Year")
ax1.set_ylabel("Total Medicaid Enrollment (millions)", color=color1)
ax1.plot(df_r_states_grouped['year'], df_r_states_grouped['num_enrollment_medicaid'] / 1e6, 
         marker='o', linestyle='-', color=color1, label="Medicaid Enrollment (millions)")
ax1.tick_params(axis='y', labelcolor=color1)

# Create second y-axis (percentage of Medicaid enrollment)
ax2 = ax1.twinx()
color2 = 'tab:red'
ax2.set_ylabel("Percentage of Medicaid Enrollment (%)", color=color2)
ax2.plot(df_r_states_grouped['year'], df_r_states_grouped['pct_enrollment_medicaid'], 
         marker='s', linestyle='--', color=color2, label="Medicaid Enrollment (%)")
ax2.tick_params(axis='y', labelcolor=color2)

# Title and grid
plt.title("Medicaid Enrollment Trends in Republican States (2016-2024)")
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

# Add legends
leg1 = ax1.legend(loc='upper left', bbox_to_anchor=(0, 1)) 
leg2 = ax2.legend(loc='upper left', bbox_to_anchor=(0, 0.88))  

plt.show()

######################################################################################################################################
# Change in medicaid enrollment against change in turmp vote share 
######################################################################################################################################
