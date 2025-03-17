import re
import pandas as pd
from pathlib import Path
home = Path.home()
work_dir = home / 'medicaid_project'
data = work_dir / 'data'
clean_data = data / 'clean'
state_level = clean_data / 'state_level'
county_level = clean_data / 'county_level'

def parse_tract_name(name):
    # This regex assumes the pattern "Census Tract ..., County Name, State Name"
    match = re.search(r"census tract .+?, (.+), (.+)", str(name))
    if match:
        return match.group(1), match.group(2)
    return None, None

# -----------------------------------------------------------------------------
# 1. Load/clean ACS 5-Year Data -- creating 1) county-level and 2) state-level datasets
# -----------------------------------------------------------------------------
county_acs5 = pd.read_csv(f'{clean_data}/acs5_county.csv')
county_acs5.columns = county_acs5.columns.str.lower()  # Make all column names lowercase
county_acs5 = county_acs5.applymap(lambda x: x.lower() if isinstance(x, str) else x)  # Convert strings

county_acs5[['county', 'state']] = county_acs5['census_tract'].apply(
    lambda x: pd.Series(parse_tract_name(x))
)

# now we want to produce, on the county-level, 
# the shares of ALL medicaid enrollees belonging to each 'group' 
medicaid_cols = [col for col in county_acs5.columns if col.endswith('medicaid_acs')]
# Step 2: Compute total Medicaid enrollment
county_acs5['total_medicaid_enrollees_acs'] = county_acs5[medicaid_cols].sum(axis=1)
# Step 3: Compute share of each group
for col in medicaid_cols:
    share_col = col.replace('num', 'share')
    county_acs5[share_col] = county_acs5[col] / county_acs5['total_medicaid_enrollees_acs']

# now we want the share of statewide total medicaid enrollees residing in that county for that year 
state_totals = county_acs5.groupby(['state', 'year'])['total_medicaid_enrollees_acs'].sum().reset_index()
state_totals.rename(columns={'total_medicaid_enrollees_acs': 'state_total_medicaid_enrollees_acs'}, 
                    inplace=True)

# Step 4: Merge state totals back into the main DataFrame
county_acs5 = county_acs5.merge(state_totals, on=['state', 'year'], how='left')
# Step 5: Compute share of state Medicaid enrollees in each county
county_acs5['county_share_of_state_medicaid'] = (county_acs5['total_medicaid_enrollees_acs'] 
                                                 / county_acs5['state_total_medicaid_enrollees_acs'])

data_copy = county_acs5.copy()
data_copy.drop(
    columns = {
        'census_tract', 'tract', 'pct_college_plus', 'pct_hs_only', 'pct_hs_or_less',
        'share_male_19_medicaid_acs', 'share_male_19_64_medicaid_acs', 'share_male_65_medicaid_acs',
        'share_female_19_medicaid_acs', 'share_female_19_64_medicaid_acs', 'share_female_65_medicaid_acs',
        'county_share_of_state_medicaid', 'state_total_medicaid_enrollees_acs'
    }, inplace=True
)

# drop unnecessary columns for each of these datasets
county_acs5.drop(
    columns = {
    'census_tract', 'male_under_19_medicaid', 'male_19_to_64_medicaid',
       'male_65_and_over_medicaid', 'female_under_19_medicaid',
       'female_19_to_64_medicaid', 'female_65_and_over_medicaid',
       'num_male_19_medicaid_acs', 'num_male_19_64_medicaid_acs',
       'num_male_65_medicaid_acs', 'num_female_19_medicaid_acs',
       'num_female_19_64_medicaid_acs', 'num_female_65_medicaid_acs',
       'pop_25_over', 'no_schooling', 'nursery_4th', 'gr5_6', 'gr7_8', 'gr9',
       'gr10', 'gr11', 'gr12_no_diploma', 'highschool_grad',
       'somecollege_lt1yr', 'somecollege_1plus', 'associates', 'bachelors',
       'masters', 'profschool', 'doctorate', 'tract'
    }, inplace=True
)

state_acs5 = data_copy.groupby(['state', 'year']).sum().reset_index()
# Compute total population 25+ years old (already exists, just a safeguard)
state_acs5['pop_25_over'] = state_acs5['pop_25_over'].replace({0: None})  # Avoid division by zero
# Compute education percentages
state_acs5['pct_college_plus'] = (
    (state_acs5['bachelors'] + state_acs5['masters'] + state_acs5['profschool'] 
     + state_acs5['doctorate'])
    / state_acs5['pop_25_over']
)
state_acs5['pct_hs_only'] = state_acs5['highschool_grad'] / state_acs5['pop_25_over']
state_acs5['pct_hs_or_less'] = (
    (
        state_acs5['no_schooling']
        + state_acs5['nursery_4th']
        + state_acs5['gr5_6']
        + state_acs5['gr7_8']
        + state_acs5['gr9']
        + state_acs5['gr10']
        + state_acs5['gr11']
        + state_acs5['gr12_no_diploma']
        + state_acs5['highschool_grad']
    )
    / state_acs5['pop_25_over']
)

state_acs5.drop(
    columns = {
    'pop_25_over', 'no_schooling', 'nursery_4th', 'gr5_6', 'gr7_8', 'gr9',
       'gr10', 'gr11', 'gr12_no_diploma', 'highschool_grad',
       'somecollege_lt1yr', 'somecollege_1plus', 'associates', 'bachelors',
       'masters', 'profschool', 'doctorate'
    }, inplace=True
)

# -----------------------------------------------------------------------------
# 2. Load Population Data
# -----------------------------------------------------------------------------
county_pop = pd.read_csv(f'{clean_data}/acs5_county_population.csv')
county_pop.columns = county_pop.columns.str.lower()  # Make all column names lowercase
county_pop = county_pop.applymap(lambda x: x.lower() if isinstance(x, str) else x)  # Convert strings 
county_pop.drop(columns={'county'}, inplace=True)
county_pop.rename(columns={'total_population_county': 'population',
                           'county_name': 'county'}, inplace=True)
state_pop = county_pop.groupby(['year', 'state'])['population'].sum().reset_index() 

# -----------------------------------------------------------------------------
# 3. Load Medicaid.gov enrollment data
# -----------------------------------------------------------------------------
medicaid_enrollment = pd.read_csv(f'{clean_data}/medicaid_enrollment.csv')
medicaid_enrollment.columns = medicaid_enrollment.columns.str.lower()  # Make all column names lowercase
# convert all string values to lowercase 
medicaid_enrollment = medicaid_enrollment.applymap(lambda x: x.lower() if isinstance(x, str) else x)  # Convert strings

# -----------------------------------------------------------------------------
# 4. Merge/Prep State-Level Dataset
# -----------------------------------------------------------------------------
master_state = pd.merge(state_acs5, state_pop, on=['state', 'year'], how='outer')
master_state = pd.merge(master_state, medicaid_enrollment, on=['state', 'year'], how='outer')

# compute state-wide enrollment:
master_state['pct_enrollment_medicaid_chip_gov'] = (master_state['num_enrollment_medicaid_chip'] 
                                          / master_state['population'])
master_state['pct_enrollment_medicaid_gov'] = (master_state['num_enrollment_medicaid']
                                          / master_state['population'])
master_state.to_csv(f'{state_level}/medicaid_education_state.csv', index=False)


# -----------------------------------------------------------------------------
# 5. Merge/Prep County-Level Dataset
# -----------------------------------------------------------------------------
master_county = pd.merge(county_acs5, county_pop, on=['county', 'state', 'year'], how='outer')
master_county = pd.merge(master_county, medicaid_enrollment, on=['state', 'year'], how='outer')

# first, estimate the number of medicaid/chip enrollees on county-level
for var in ['', '_chip']:
    master_county[f'num_county_medicaid{var}'] = (master_county[f'num_enrollment_medicaid{var}']
                                                 * master_county['county_share_of_state_medicaid'])
    master_county[f'pct_enrollment_medicaid{var}_gov'] = (master_county[f'num_county_medicaid{var}'] 
                                          / master_county['population'])
    
master_county['pct_enrollment_medicaid_acs'] = (master_county[f'total_medicaid_enrollees_acs']
                                        / master_county['population'])

master_county.to_csv(f'{county_level}/medicaid_education_county.csv', index=False)