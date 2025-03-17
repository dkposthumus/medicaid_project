import pandas as pd
from pathlib import Path
# let's create a set of locals referring to our directory and working directory 
home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
crosswalks = (data / 'crosswalks')
state_level = (clean_data / 'state_level')
election_results = (state_level / 'election_results')
county_level = (clean_data / 'county_level')
output = (work_dir / 'output')
code = Path.cwd() 

# pull in county-level enrollment variables 
enrollment_education = pd.read_csv(f'{county_level}/medicaid_education_county.csv')
house_2020_2024 = pd.read_csv(f'{clean_data}/house_2020_2024.csv')
pres = pd.read_csv(f'{clean_data}/pres_election_2000_2024_county.csv')
senate_2020_2024 = pd.read_csv(f'{clean_data}/senate_2020_2024.csv')

master = pd.merge(enrollment_education, house_2020_2024, on=['county_name', 'state_name'], how='left')
master = pd.merge(master, pres, on=['year', 'state_name', 'county_name'], how='outer')
master = pd.merge(master, senate_2020_2024, on=['state_name', 'county_name'], how='outer')

for var in ['', '_chip']:
    master[f'pct_enrollment_medicaid{var}_gov'] = (master[f'num_enrollment_medicaid{var}']
                                                   / master['population'])

master['pct_enrollment_medicaid_acs'] = (master['total_medicaid_enrollees_acs']
                                         / master['population'])

master.to_csv(f'{clean_data}/master_county.csv', index=False)