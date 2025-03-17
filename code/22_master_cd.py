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

master = pd.read_csv(f'{clean_data}/master_county.csv')
for var in ['state', 'county']:
    master[var] = master[var].astype(str)
    master[var] = master[var].str.replace('.0', '', regex=True)
county_cd = pd.read_csv(f'{crosswalks}/county_cd.csv')
for var in ['state', 'county', 'geoid_cd119_20']:
    county_cd[var] = county_cd[var].astype(str)
county_levels = pd.read_csv(f'{county_level}/county_levels_enrollees_educ.csv')
for var in ['state', 'county']:
    county_levels[var] = county_levels[var].astype(str)

# now keep only level variables because we're going to sum on congressional district level
master.drop(
    columns = {
    'share_male_19_medicaid_acs',
       'share_male_19_64_medicaid_acs', 'share_male_65_medicaid_acs',
       'share_female_19_medicaid_acs', 'share_female_19_64_medicaid_acs',
       'share_female_65_medicaid_acs', 'state_total_medicaid_enrollees_acs',
       'county_share_of_state_medicaid', 'pct_college_plus', 'pct_hs_only', 'pct_hs_or_less',
        'share_male_19_medicaid_acs', 'share_male_19_64_medicaid_acs',
        'check', 'pct_enrollment_medicaid_gov', 'pct_enrollment_medicaid_chip_gov',
        'pct_enrollment_medicaid_chip_gov', 'pct_enrollment_medicaid_acs',
        'dem_pct_house_2020', 'rep_pct_house_2020', 'dem_pct_senate_2020', 'rep_pct_senate_2020'
    }, inplace=True
)
# now merge the crosswalk on
master = pd.merge(master, county_cd, on=['county', 'state'], how='outer')
master = master.groupby(['year', 'geoid_cd119_20', 'congressional district', 'state', 'state_name'])[[
    'total_medicaid_enrollees_acs', 'population', 'num_enrollment_medicaid_chip', 'num_enrollment_medicaid',
    'num_19_to_64_medi_chip_gov', 'num_expansion_medi_chip_gov', 'num_65_medi_chip_gov', 
    'num_covid_medi_chip_gov', 'num_18_medi_chip_gov', 'house totalvotes, 2020', 'house totalvotes, 2024',
    'house dem votecount, 2024', 'house rep votecount, 2024', 'democratic_pres_votes',
    'other_pres_votes', 'republican_pres_votes', 'total_pres_votes',
    'senate totalvotes, 2020', 'senate dem votecount, 2020', 'senate rep votecount, 2020', 
    'senate totalvotes, 2024', 'senate dem votecount, 2024', 'senate rep votecount, 2024'
]].sum().reset_index()


# bring in county_levels data
cd_levels = pd.merge(county_levels, county_cd, on=['county', 'state'], how='outer')
cd_levels = cd_levels.groupby(['year', 'geoid_cd119_20', 'congressional district', 
                               'state', 'state_name']).sum().reset_index()

# create education variables
cd_levels['pop_25_over'] = cd_levels['pop_25_over'].replace({0: None})  # Avoid division by zero
# Compute education percentages
cd_levels['pct_college_plus'] = (
    (cd_levels['bachelors'] + cd_levels['masters'] + cd_levels['profschool'] 
     + cd_levels['doctorate'])
    / cd_levels['pop_25_over']
)
cd_levels['pct_hs_only'] = cd_levels['highschool_grad'] / cd_levels['pop_25_over']
cd_levels['pct_hs_or_less'] = (
    (
        cd_levels['no_schooling']
        + cd_levels['nursery_4th']
        + cd_levels['gr5_6']
        + cd_levels['gr7_8']
        + cd_levels['gr9']
        + cd_levels['gr10']
        + cd_levels['gr11']
        + cd_levels['gr12_no_diploma']
        + cd_levels['highschool_grad']
    )
    / cd_levels['pop_25_over']
)

cd_levels.drop(
    columns = {
    'pop_25_over', 'no_schooling', 'nursery_4th', 'gr5_6', 'gr7_8', 'gr9',
       'gr10', 'gr11', 'gr12_no_diploma', 'highschool_grad',
       'somecollege_lt1yr', 'somecollege_1plus', 'associates', 'bachelors',
       'masters', 'profschool', 'doctorate'
    }, inplace=True
)

master = pd.merge(master, cd_levels, on=['state', 'state_name', 'year', 'geoid_cd119_20', 'congressional district'], how='outer')

for var in ['', '_chip']:
    master[f'pct_enrollment_medicaid{var}_gov'] = (master[f'num_enrollment_medicaid{var}']
                                                   / master['population'])

master['pct_enrollment_medicaid_acs'] = (master['total_medicaid_enrollees_acs']
                                         / master['population'])

master.to_csv(f'{clean_data}/master_cd.csv', index=False)