import pandas as pd
import numpy as np
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
tract_level = (clean_data / 'tract_level')
output = (work_dir / 'output')
code = Path.cwd() 

tract_cd = pd.read_csv(f'{crosswalks}/tract_cd.csv')
for var in ['state', 'county', 'tract_number']:
    tract_cd[var] = tract_cd[var].astype(str)

enroll_educ_tract = pd.read_csv(f'{tract_level}/medicaid_education_tract.csv')
house_2024 = pd.read_csv(f'{clean_data}/cd_level_house_2024.csv')

enroll_educ_tract.drop(
    columns = {
        'census_tract', 'tract_x',
        'name', 'tract_y',
       'pct_enrollment_medicaid_chip_gov', 'pct_enrollment_medicaid_acs',
       'pct_enrollment_medicaid_gov', 'check'
    }, inplace=True
)

for var in ['tract_number', 'county', 'state']:
    for df in [enroll_educ_tract, tract_cd]:
        df[var] = df[var].astype(str)
        # replace '.0' with ''
        df[var] = df[var].str.replace('.0', '')

master_tract = pd.merge(tract_cd, enroll_educ_tract, on=['tract_number', 'county', 'state'], how='outer')

# bring in county_levels data
master_cd = master_tract.groupby(['year', 'cd119', 'state', 'state_name']).sum().reset_index()

master_cd = pd.merge(master_cd, house_2024, on=['cd119', 'state_name', 'year'], how='outer')

for var in ['', '_chip']:
    master_cd[f'pct_enrollment_medicaid{var}_gov'] = (master_cd[f'num_tract_medicaid{var}_gov']
                                                   / master_cd['population'])

master_cd['pct_enrollment_medicaid_acs'] = (master_cd['total_medicaid_enrollees_acs']
                                         / master_cd['population'])

# now we also want estimates of the share of the population under each of the age/gender groups 
for group in ['male_19', 'male_19_64', 'male_65',
              'female_19', 'female_19_64', 'female_65']:
    master_cd[f'ct_{group}_medicaid_gov'] = (master_cd['num_tract_medicaid_gov'] 
                                             * master_cd[f'share_{group}_medicaid_acs'])


# now create republican / democratic variables
master_cd['margin'] = np.abs((master_cd['republican_house_votes'] 
                                   - master_cd['democratic_house_votes']) / 
                                  master_cd['total_house_votes'])
for party in ['republican', 'democratic']:
    master_cd[f'{party}_house_pct'] = (master_cd[f'{party}_house_votes']
                                       / master_cd['total_house_votes'])
# Assign 'r' or 'd' to 'r_cd' based on vote comparison
master_cd['r_cd'] = np.where(master_cd['republican_house_votes'] 
                                  > master_cd['democratic_house_votes'], 'r', 'd')
# Identify close races (margin < 5%)
master_cd['close_race'] = np.where(master_cd['margin'] < 0.05, 1, 0)


master_cd.to_csv(f'{clean_data}/master_cd.csv', index=False)