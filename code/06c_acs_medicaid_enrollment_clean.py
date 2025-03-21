import re
import pandas as pd
from pathlib import Path
home = Path.home()
work_dir = home / 'medicaid_project'
data = work_dir / 'data'
clean_data = data / 'clean'
state_level = clean_data / 'state_level'
county_level = clean_data / 'county_level'
tract_level = clean_data / 'tract_level'

def parse_tract_name(name):
    # This regex now accepts either a comma or semicolon as the separator:
    # It assumes the pattern "Census Tract <tract_number> [,;] <County Name> [,;] <State Name>"
    match = re.search(r"census tract ([\d\.]+)[,;]\s*(.+)[,;]\s*(.+)", str(name), re.IGNORECASE)
    if match:
        # match.group(1) is the tract number, group(2) is the county, group(3) is the state
        return match.group(1), match.group(2), match.group(3)
    return None, None, None

# -----------------------------------------------------------------------------
# 1. Load/clean ACS 5-Year Data -- creating 1) county-level and 2) state-level datasets
# -----------------------------------------------------------------------------
tract_acs5 = pd.read_csv(f'{tract_level}/acs5_tract.csv')
tract_acs5.columns = tract_acs5.columns.str.lower()  # Make all column names lowercase
tract_acs5 = tract_acs5.applymap(lambda x: x.lower() if isinstance(x, str) else x)  # Convert strings

tract_acs5[['tract_number', 'county_name', 'state_name']] = tract_acs5['census_tract'].apply(
    lambda x: pd.Series(parse_tract_name(x))
)

county_acs5 = tract_acs5.copy()

# now we want to produce, on the tract-level, 
# the shares of ALL medicaid enrollees belonging to each 'group' 
medicaid_cols = [col for col in tract_acs5.columns if col.endswith('medicaid_acs')]
# Step 2: Compute total Medicaid enrollment
tract_acs5['total_medicaid_enrollees_acs'] = tract_acs5[medicaid_cols].sum(axis=1)
# Step 3: Compute share of each group
for col in medicaid_cols:
    share_col = col.replace('num', 'share')
    tract_acs5[share_col] = tract_acs5[col] / tract_acs5['total_medicaid_enrollees_acs']

# now we want the share of statewide total medicaid enrollees residing in that county for that year 
state_totals = tract_acs5.groupby(['state_name', 'state', 'year'])['total_medicaid_enrollees_acs'].sum().reset_index()
state_totals.rename(columns={'total_medicaid_enrollees_acs': 'state_total_medicaid_enrollees_acs'}, 
                    inplace=True)

# Step 4: Merge state totals back into the main DataFrame
tract_acs5 = tract_acs5.merge(state_totals, on=['state', 'state_name', 'year'], how='left')
# Step 5: Compute share of state Medicaid enrollees in each county
tract_acs5['tract_share_of_state_medicaid'] = (tract_acs5['total_medicaid_enrollees_acs'] 
                                                 / tract_acs5['state_total_medicaid_enrollees_acs'])

county_acs5.drop(columns={'pct_college_plus', 'pct_hs_only', 'pct_hs_or_less', 
                          'census_tract', 'tract', 'tract_number'}, inplace=True)

county_acs5 = county_acs5.groupby(['year', 'county', 'state', 'county_name', 'state_name']).sum().reset_index()

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
state_totals = county_acs5.groupby(['state_name', 'state', 'year'])['total_medicaid_enrollees_acs'].sum().reset_index()
state_totals.rename(columns={'total_medicaid_enrollees_acs': 'state_total_medicaid_enrollees_acs'}, 
                    inplace=True)

# Step 4: Merge state totals back into the main DataFrame
county_acs5 = county_acs5.merge(state_totals, on=['state', 'state_name', 'year'], how='left')
# Step 5: Compute share of state Medicaid enrollees in each county
county_acs5['county_share_of_state_medicaid'] = (county_acs5['total_medicaid_enrollees_acs'] 
                                                 / county_acs5['state_total_medicaid_enrollees_acs'])

data_copy = county_acs5.copy()
data_copy.drop(
    columns = {
        'county_share_of_state_medicaid', 'state_total_medicaid_enrollees_acs', 'county',
        'county_name'
    }, inplace=True
)

county_levels = county_acs5[[
    'state', 'state_name', 'county_name', 'county', 'year', 'male_under_19_medicaid', 
    'male_19_to_64_medicaid',
       'male_65_and_over_medicaid', 'female_under_19_medicaid',
       'female_19_to_64_medicaid', 'female_65_and_over_medicaid',
       'num_male_19_medicaid_acs', 'num_male_19_64_medicaid_acs',
       'num_male_65_medicaid_acs', 'num_female_19_medicaid_acs',
       'num_female_19_64_medicaid_acs', 'num_female_65_medicaid_acs'
]]
county_levels.to_csv(f'{county_level}/county_levels_enrollees_educ.csv', index=False)
state_acs5 = data_copy.groupby(['state', 'state_name', 'year']).sum().reset_index()

# -----------------------------------------------------------------------------
# 2. Load Population Data
# -----------------------------------------------------------------------------
tract_pop = pd.read_csv(f'{tract_level}/acs5_tract_population.csv')
tract_pop.columns = tract_pop.columns.str.lower()  # Make all column names lowercase
tract_pop = tract_pop.applymap(lambda x: x.lower() if isinstance(x, str) else x)  # Convert strings 
tract_pop[['tract_number', 'county_name', 'state_name']] = tract_pop['name'].apply(
    lambda x: pd.Series(parse_tract_name(x))
)
tract_pop.rename(columns={'total_population_tract': 'population'}, inplace=True)
tract_pop_2023 = tract_pop[tract_pop['year'] == 2023].copy()
tract_pop_2024 = tract_pop_2023.copy()
tract_pop_2024['year'] = 2024
tract_pop = pd.concat([tract_pop, tract_pop_2024], ignore_index=True)

county_pop = tract_pop.copy()
county_pop.drop(
    columns = {'tract', 'tract_number'}, inplace=True
)
county_pop = county_pop.groupby(['year', 'state_name', 'state', 'county', 
                                 'county_name'])['population'].sum().reset_index()

state_pop = county_pop.copy()
state_pop.drop(
    columns = {'county', 'county_name'}, inplace=True
)
state_pop = state_pop.groupby(['year', 'state_name', 
                               'state'])['population'].sum().reset_index() 

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
master_state = pd.merge(state_acs5, state_pop, on=['state', 'state_name', 'year'], how='outer')
master_state = pd.merge(master_state, medicaid_enrollment, on=['state_name', 'year'], how='outer')

master_state['population'] = master_state.groupby('state_name')['population'].ffill()

# compute state-wide enrollment:
master_state['pct_enrollment_medicaid_chip_gov'] = (master_state['num_medicaid_chip_gov'] 
                                          / master_state['population'])
master_state['pct_enrollment_medicaid_gov'] = (master_state['num_medicaid_gov']
                                          / master_state['population'])

master_state['pct_enrollment_medicaid_acs'] = (master_state['total_medicaid_enrollees_acs']
                                               / master_state['population'])

master_state.to_csv(f'{state_level}/medicaid_education_state.csv', index=False)

# -----------------------------------------------------------------------------
# 5. Merge/Prep County-Level Dataset
# -----------------------------------------------------------------------------
master_county = pd.merge(county_acs5, county_pop, on=['county', 'county_name', 'state', 'state_name', 'year'], how='outer')
master_county = pd.merge(master_county, medicaid_enrollment, on=['state_name', 'year'], how='outer')

master_county['population'] = master_county.groupby(['state_name', 'county_name'])['population'].ffill()
master_county['county_share_of_state_medicaid'] = master_county.groupby(['county_name', 'state_name'])['county_share_of_state_medicaid'].ffill()

# first, estimate the number of medicaid/chip enrollees on county-level
for var in ['', '_chip']:
    master_county[f'num_county_medicaid{var}_gov'] = (master_county[f'num_medicaid{var}_gov']
                                                 * master_county['county_share_of_state_medicaid'])
    master_county[f'pct_enrollment_medicaid{var}_gov'] = (master_county[f'num_county_medicaid{var}_gov'] 
                                          / master_county['population'])
    
for var in ['19_to_64_medi_chip_gov', 'expansion_medi_chip_gov', '65_medi_chip_gov',
       'covid_medi_chip_gov', '18_medi_chip_gov', 'disabled_medi_chip_gov', 
       'unknown_med_chip_gov']:
    master_county[f'num_county_{var}'] = (master_county[f'num_{var}']
                                          * master_county['county_share_of_state_medicaid'])

master_county['pct_enrollment_medicaid_acs'] = (master_county['total_medicaid_enrollees_acs']
                                        / master_county['population'])

master_county.to_csv(f'{county_level}/medicaid_education_county.csv', index=False)

# -----------------------------------------------------------------------------
# 5. Merge/Prep Tract-Level Dataset
# -----------------------------------------------------------------------------
tract_acs5['tract_number'] = tract_acs5['tract_number'].astype(str)
tract_pop['tract_number'] = tract_pop['tract_number'].astype(str)

master_tract = pd.merge(tract_acs5, tract_pop, on=['tract_number', 'county', 'county_name', 'state', 'state_name', 'year'], how='outer')
master_tract = pd.merge(master_tract, medicaid_enrollment, on=['state_name', 'year'], how='outer')

master_tract['population'] = master_tract.groupby(['state_name', 'county_name', 'tract_number'])['population'].ffill()
master_tract['tract_share_of_state_medicaid'] = master_tract.groupby(['county_name', 'state_name', 'tract_number'])['tract_share_of_state_medicaid'].ffill()

for var in ['', '_chip']:
    master_tract[f'num_tract_medicaid{var}_gov'] = (master_tract[f'num_medicaid{var}_gov']
                                                 * master_tract['tract_share_of_state_medicaid'])
    master_tract[f'pct_enrollment_medicaid{var}_gov'] = (master_tract[f'num_tract_medicaid{var}_gov'] 
                                          / master_tract['population'])

for var in ['19_to_64_medi_chip_gov', 'expansion_medi_chip_gov', '65_medi_chip_gov',
       'covid_medi_chip_gov', '18_medi_chip_gov', 'disabled_medi_chip_gov', 
       'unknown_med_chip_gov']:
    master_tract[f'num_tract_{var}'] = (master_tract[f'num_{var}']
                                          * master_tract['tract_share_of_state_medicaid'])

master_tract['pct_enrollment_medicaid_acs'] = (master_tract['total_medicaid_enrollees_acs']
                                        / master_tract['population'])

master_tract.to_csv(f'{tract_level}/medicaid_education_tract.csv', index=False)