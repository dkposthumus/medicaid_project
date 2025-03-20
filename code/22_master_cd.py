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
tract_level = (clean_data / 'tract_level')
output = (work_dir / 'output')
code = Path.cwd() 

tract_cd = pd.read_csv(f'{crosswalks}/tract_cd.csv')
for var in ['state', 'county', 'tract_number']:
    tract_cd[var] = tract_cd[var].astype(str)

enroll_educ_tract = pd.read_csv(f'{tract_level}/medicaid_education_tract.csv')

enroll_educ_tract.drop(
    columns = {
        'census_tract', 'tract_x', 'pct_college_plus', 'pct_hs_only', 'pct_hs_or_less',
       'tract_share_of_state_medicaid', 'name', 'tract_y',
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

# create education variables
def educ_var_create(df):
    df['pop_25_over'] = df['pop_25_over'].replace({0: None})  # Avoid division by zero
# Compute education percentages
    df['pct_college_plus'] = (
        (df['bachelors'] + df['masters'] + df['profschool'] 
        + df['doctorate'])
        / df['pop_25_over'] 
    )
    df['pct_hs_only'] = df['highschool_grad'] / df['pop_25_over']
    df['pct_hs_or_less'] = (
        (
            df['no_schooling']
            + df['nursery_4th']
            + df['gr5_6']
            + df['gr7_8']
            + df['gr9']
            + df['gr10']
            + df['gr11']
            + df['gr12_no_diploma']
            + df['highschool_grad']
        )
        / df['pop_25_over']
    )
    return df

master_cd = educ_var_create(master_cd)

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

master_cd.to_csv(f'{clean_data}/master_cd.csv', index=False)