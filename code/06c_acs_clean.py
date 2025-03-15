import re
import pandas as pd
from pathlib import Path
home = Path.home()
work_dir = home / 'medicaid_project'
data = work_dir / 'data'
clean_data = data / 'clean'
state_level = clean_data / 'state_level'

# -----------------------------------------------------------------------------
# 1. Load ACS 5-Year Data
# -----------------------------------------------------------------------------
acs5 = pd.read_csv(f'{clean_data}/acs5_county.csv')
acs5.columns = acs5.columns.str.lower()  # Make all column names lowercase
acs5 = acs5.applymap(lambda x: x.lower() if isinstance(x, str) else x)  # Convert strings

population = pd.read_csv(f'{clean_data}/acs5_county_population.csv')
population.columns = population.columns.str.lower()  # Make all column names lowercase
population = population.groupby(['state', 'year'])['total_population_county'].sum().reset_index()
population = population.applymap(lambda x: x.lower() if isinstance(x, str) else x)  # Convert strings 
population.rename(columns={'total_population_county': 'population'}, inplace=True)

medicaid_enrollment = pd.read_csv(f'{clean_data}/medicaid_enrollment.csv')
medicaid_enrollment.columns = medicaid_enrollment.columns.str.lower()  # Make all column names lowercase
# convert all string values to lowercase 
medicaid_enrollment = medicaid_enrollment.applymap(lambda x: x.lower() if isinstance(x, str) else x)  # Convert strings

# -----------------------------------------------------------------------------
# 2. Parse State & County Names
# -----------------------------------------------------------------------------
def parse_tract_name(name):
    # This regex assumes the pattern "Census Tract ..., County Name, State Name"
    match = re.search(r"Census Tract .+?, (.+), (.+)", str(name))
    if match:
        return match.group(1), match.group(2)
    return None, None

acs5[['county_name', 'state']] = acs5['census_tract'].apply(
    lambda x: pd.Series(parse_tract_name(x))
)
acs5.drop(columns=['census_tract', 'county', 'tract', 'county_name'], inplace=True)

state_acs5 = acs5.groupby(['state', 'year']).sum().reset_index()
state_acs5.to_csv(f'{clean_data}/acs5_state.csv', index=False)

########## merge w/enrollment data 
master = pd.merge(state_acs5, medicaid_enrollment, on=['year', 'state'], how='outer')
master = pd.merge(master, population, on=['year', 'state'], how='outer')

# compute state-wide enrollment:
master['pct_enrollment_medicaid_chip'] = (master['num_enrollment_medicaid_chip'] 
                                          / master['population'])
master['pct_enrollment_medicaid'] = (master['num_enrollment_medicaid']
                                          / master['population'])

# -----------------------------------------------------------------------------
# 5. Education Data Cleaning
# -----------------------------------------------------------------------------
# Compute total population 25+ years old (already exists, just a safeguard)
master['pop_25_over'] = master['pop_25_over'].replace({0: None})  # Avoid division by zero

# Compute education percentages
master['pct_college_plus'] = (
    (master['bachelors'] + master['masters'] + master['profschool'] 
     + master['doctorate'])
    / master['pop_25_over']
)

master['pct_hs_only'] = master['highschool_grad'] / master['pop_25_over']

master['pct_hs_or_less'] = (
    (
        master['no_schooling']
        + master['nursery_4th']
        + master['gr5_6']
        + master['gr7_8']
        + master['gr9']
        + master['gr10']
        + master['gr11']
        + master['gr12_no_diploma']
        + master['highschool_grad']
    )
    / master['pop_25_over']
)

# -----------------------------------------------------------------------------
# 6. Save Cleaned Data
# -----------------------------------------------------------------------------
master.to_csv(f'{state_level}/medicaid_education_state.csv', index=False)

print(f"Cleaned state-level Medicaid and education data saved to '{state_level}/medicaid_education_state.csv'.")