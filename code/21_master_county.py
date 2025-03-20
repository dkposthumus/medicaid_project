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

# now we also want estimates of the share of the population under each of the age/gender groups 
for group in ['male_19', 'male_19_64', 'male_65',
              'female_19', 'female_19_64', 'female_65']:
    master[f'ct_{group}_medicaid_gov'] = (master['num_county_medicaid_gov'] 
                                             * master[f'share_{group}_medicaid_acs'])

master.to_csv(f'{clean_data}/master_county.csv', index=False)