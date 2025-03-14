import pandas as pd
from pathlib import Path
# let's create a set of locals referring to our directory and working directory 
home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
cd_level = (clean_data / 'cd_level')
output = (work_dir / 'output')
code = Path.cwd() 

######################################################################################################################################
# Oct. 2024 Cross-Section 
######################################################################################################################################
oct_2024 = pd.read_excel(f'{raw_data}/2024_medicaid_enrollment.xlsx', header=3)

#####################
# State-Level Dataset
#####################
oct_2024.columns = oct_2024.columns.str.lower() # make all columns lower-case 
oct_2024 = oct_2024.applymap(lambda x: x.lower() if isinstance(x, str) else x)
oct_2024.rename(
    columns = {
        'unnamed: 0': 'state',
        'number of participants': 'num_enrollment_medicaid',
        'participation as a share of total population': 'pct_enrollment_medicaid',
        'number under age 19': 'num_under_19_medicaid',
        'percent under age 19': 'pct_enrollment_under_19_medicaid',
        'percent ages 19-64': 'pct_enrollment_19_to_64_medicaid',
        'percent ages 65 and older': 'pct_enrollment_65_and_over_medicaid'
        }, inplace=True
)
num_cols = ['num_enrollment_medicaid', 'pct_enrollment_medicaid', 'num_under_19_medicaid', 
            'pct_enrollment_under_19_medicaid', 'pct_enrollment_19_to_64_medicaid', 
            'pct_enrollment_65_and_over_medicaid']
for col in num_cols:
    oct_2024[col] = pd.to_numeric(oct_2024[col], errors='coerce')
oct_2024 = oct_2024.dropna(subset=num_cols)
oct_2024['year'] = 2024 # create year variable, equal to 2024 + constant for all observations

oct_2024 = oct_2024[oct_2024['state'] != '50 states + dc'] # drop national total
# we're only interested in state totals drop all observations where the value for 'state' contains 'district'
state_2024 = oct_2024[~oct_2024['state'].str.contains('district', case=False, na=False)]
state_2024.to_csv(f'{state_level}/oct_2024_enrollment_state.csv', index=False)

