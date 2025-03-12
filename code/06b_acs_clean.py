import re
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
# let's create a set of locals referring to our directory and working directory 
home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
county_level = (clean_data / 'cd_level')
output = (work_dir / 'output')
code = Path.cwd() 

# clean ACS medicaid data 
acs5 = pd.read_csv(f'{clean_data}/acs5_county.csv')
# first we want to create a state-level dataset
def parse_tract_name(name):
    # This regex assumes the pattern "Census Tract ..., County Name, State Name"
    match = re.search(r"Census Tract .+?, (.+), (.+)", name)
    if match:
        return match.group(1), match.group(2)
    return None, None
# Apply the function to create new columns
acs5[['county_name', 'state']] = acs5['Census_Tract'].apply(
    lambda x: pd.Series(parse_tract_name(x))
)
# make all columns lowercase 
acs5.columns = acs5.columns.str.lower()
# make all string values lowercase 
acs5 = acs5.applymap(lambda x: x.lower() if isinstance(x, str) else x)

acs5.drop(
    columns = {'census_tract', 'county', 'tract', 'county_name'}, inplace=True
)
# first make state-level dataset 
state_acs5 = acs5.groupby(['state', 'year']).sum().reset_index()

def acs5_cleaning(df):
    # create column summing all columns 'with medicaid'
    df['num_enrollment_medicaid'] = (
        df['male_under_19_with_medicaid']
        + df['male_19_to_64_with_medicaid']
        + df['male_65_and_over_with_medicaid']
        + df['female_under_19_with_medicaid']
        + df['female_19_to_64_with_medicaid']
        + df['female_65_and_over_with_medicaid']
    )
    df['pct_enrollment_medicaid'] = (
        df['num_enrollment_medicaid'] / df['total_population_census_tract']
    )
    for age in ['under_19', '19_to_64', '65_and_over']:
        for gender in ['female', 'male']:
            df[f'pct_enrollment_{gender}_{age}_medicaid'] = (
                df[f'{gender}_{age}_with_medicaid'] / df[f'{gender}_{age}']
            )
            df.drop(columns={f'{gender}_{age}_no_medicaid'}, inplace=True)
        df[f'total_{age}'] = df[f'male_{age}'] + df[f'female_{age}'] 
        df[f'num_enrollment_{age}_medicaid'] = (
            df[f'male_{age}_with_medicaid'] + df[f'female_{age}_with_medicaid']
        )
        df[f'pct_enrollment_{age}_medicaid'] = (
            df[f'num_enrollment_{age}_medicaid'] / df[f'total_{age}']
        )
    for gender in ['female', 'male']:
        df[f'total_{gender}_medicaid'] = (
            df[f'{gender}_under_19_with_medicaid']
            + df[f'{gender}_19_to_64_with_medicaid']
            + df[f'{gender}_65_and_over_with_medicaid']
        )
        df[f'pct_enrollment_{gender}_medicaid'] = (
            df[f'total_{gender}_medicaid'] / df[f'{gender}_total']
        )
    return df
 
# put state-level data through cleaning function 
state_acs5 = acs5_cleaning(state_acs5)
# for now, let's restrict to the key enrollment rates 
state_acs5 = state_acs5[['year', 'state', 'pct_enrollment_medicaid', 
                         'pct_enrollment_female_under_19_medicaid',
                         'pct_enrollment_male_under_19_medicaid',
                         'pct_enrollment_female_19_to_64_medicaid',
                         'pct_enrollment_male_19_to_64_medicaid',
                         'pct_enrollment_female_65_and_over_medicaid',
                         'pct_enrollment_male_65_and_over_medicaid',
                         'pct_enrollment_female_medicaid',
                         'pct_enrollment_male_medicaid',
                         'pct_enrollment_under_19_medicaid',
                         'pct_enrollment_19_to_64_medicaid',
                         'pct_enrollment_65_and_over_medicaid']]
state_acs5.to_csv(f'{state_level}/medicaid_enrollment_state.csv', index=False)

