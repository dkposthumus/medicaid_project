import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
home = Path.home()
work_dir = home / 'medicaid_project'
data = work_dir / 'data'
clean_data = data / 'clean'
state_level = clean_data / 'state_level'
county_level = clean_data / 'county_level'

master = pd.read_csv(f'{county_level}/medicaid_education_county.csv')

# now i want to do a quick comp of two measures of enrollment: ACS and Medicaid.gov 

for var in ['', '_chip']:
    x = master['pct_enrollment_medicaid_acs']
    y = master[f'pct_enrollment_medicaid{var}_gov']
    plt.scatter(x, y, alpha=0.7)
    x_values = np.linspace(min(master['pct_enrollment_medicaid_acs']), 
                           max(master['pct_enrollment_medicaid_acs']), 100)
    plt.plot(x_values, x_values, color='red', linestyle='--', label='y = x')
    plt.xlabel('ACS 5-Year Data')
    plt.ylabel(f'Medicaid.gov Data {var}')
    plt.show()


master['acs_gov_spread'] = master['pct_enrollment_medicaid_gov'] - master['pct_enrollment_medicaid_acs']

# collapse on state/year and plot over time 
collapsed = master.groupby(['year', 'state'])['acs_gov_spread'].mean().reset_index()

for state in collapsed['state'].unique():
    state_data = collapsed[collapsed['state'] == state]
    plt.plot(state_data['year'], state_data['acs_gov_spread'], linewidth=0.2)
collapsed_collapsed = collapsed.groupby('year')['acs_gov_spread'].mean().reset_index()
plt.plot(collapsed_collapsed['year'], collapsed_collapsed['acs_gov_spread'], label='All States', color='black')    
plt.legend()
plt.grid(True)
plt.axhline(y=0)
plt.show()

plt.hist(collapsed['acs_gov_spread'])
plt.show()