import re
import pandas as pd
from pathlib import Path
home = Path.home()
work_dir = home / 'medicaid_project'
data = work_dir / 'data'
clean_data = data / 'clean'
state_level = clean_data / 'state_level'

# -----------------------------------------------------------------------------
# 2. Load ACS 5-Year Data
# -----------------------------------------------------------------------------
acs5 = pd.read_csv(f'{clean_data}/acs5_county.csv')
acs5.columns = acs5.columns.str.lower()  # Make all column names lowercase

# -----------------------------------------------------------------------------
# 3. Parse State & County Names
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

# -----------------------------------------------------------------------------
# 4. Format Columns (Lowercase & Remove Unnecessary Columns)
# -----------------------------------------------------------------------------
acs5 = acs5.applymap(lambda x: x.lower() if isinstance(x, str) else x)  # Convert strings
# Drop unnecessary location-related columns
acs5.drop(columns=['census_tract', 'county', 'tract', 'county_name'], inplace=True)
# -----------------------------------------------------------------------------
# 5. Aggregate to State-Level Data
# -----------------------------------------------------------------------------
state_acs5 = acs5.groupby(['state', 'year']).sum().reset_index()
state_acs5.to_csv(f'{clean_data}/acs5_state.csv', index=False)

# -----------------------------------------------------------------------------
# 6. Medicaid Enrollment Cleaning
# -----------------------------------------------------------------------------
def acs5_cleaning(df):
    # Compute total Medicaid enrollment
    df['num_enrollment_medicaid'] = (
        df['male_under_19_with_medicaid']
        + df['male_19_to_64_with_medicaid']
        + df['male_65_and_over_with_medicaid']
        + df['female_under_19_with_medicaid']
        + df['female_19_to_64_with_medicaid']
        + df['female_65_and_over_with_medicaid']
    )

    # Compute percentage Medicaid enrollment
    df['pct_enrollment_medicaid'] = df['num_enrollment_medicaid'] / df['total_population_county']
    # Compute age-specific and gender-specific Medicaid enrollment
    for age in ['under_19', '19_to_64', '65_and_over']:
        for gender in ['female', 'male']:
            df[f'{gender}_{age}'] = df[f'{gender}_{age}_no_medicaid'] + df[f'{gender}_{age}_with_medicaid']
            df[f'pct_enrollment_{gender}_{age}_medicaid'] = df[f'{gender}_{age}_with_medicaid'] / df[f'{gender}_{age}']

        df[f'total_{age}'] = df[f'male_{age}'] + df[f'female_{age}']
        df[f'num_enrollment_{age}_medicaid'] = df[f'male_{age}_with_medicaid'] + df[f'female_{age}_with_medicaid']
        df[f'pct_enrollment_{age}_medicaid'] = df[f'num_enrollment_{age}_medicaid'] / df[f'total_{age}']
    for gender in ['female', 'male']:
        df[f'{gender}_total'] = (df[f'{gender}_under_19'] + df[f'{gender}_19_to_64'] 
                                        + df[f'{gender}_65_and_over'])
    # Compute gender-specific Medicaid enrollment
    for gender in ['female', 'male']:
        df[f'total_{gender}_medicaid'] = (
            df[f'{gender}_under_19_with_medicaid']
            + df[f'{gender}_19_to_64_with_medicaid']
            + df[f'{gender}_65_and_over_with_medicaid']
        )
        df[f'pct_enrollment_{gender}_medicaid'] = df[f'total_{gender}_medicaid'] / df[f'{gender}_total']

    return df

# Apply cleaning function
state_acs5 = acs5_cleaning(state_acs5)

# -----------------------------------------------------------------------------
# 7. Education Data Cleaning
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 8. Select Relevant Columns
# -----------------------------------------------------------------------------
state_acs5 = state_acs5[[
    'year', 'state', 'num_enrollment_medicaid',
    'pct_enrollment_medicaid',
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
    'pct_enrollment_65_and_over_medicaid',
    'pct_college_plus',  # New education column
    'pct_hs_only',       # New education column
    'pct_hs_or_less'     # New education column
]]

# -----------------------------------------------------------------------------
# 9. Save Cleaned Data
# -----------------------------------------------------------------------------
state_acs5.to_csv(f'{state_level}/medicaid_education_state.csv', index=False)

print(f"Cleaned state-level Medicaid and education data saved to '{state_level}/medicaid_education_state.csv'.")