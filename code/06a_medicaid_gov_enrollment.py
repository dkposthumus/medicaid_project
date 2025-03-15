import pandas as pd
from pathlib import Path
import numpy as np
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

# pull in dataset
enrollment = pd.read_csv(f'{raw_data}/medicaid_gov_data.csv')
enrollment.columns = enrollment.columns.str.lower()
enrollment.rename(
    columns = {
        'total medicaid and chip enrollment': 'num_enrollment_medicaid_chip',
        'total medicaid enrollment': 'num_enrollment_medicaid',
        'state name': 'state'
    }, inplace=True
)
enrollment['reporting period'] = enrollment['reporting period'].astype(str)  
# Extract year and month
enrollment['year'] = enrollment['reporting period'].str[:4].astype(int)   # First 4 digits → Year
enrollment['month'] = enrollment['reporting period'].str[4:].astype(int)  # Last 2 digits → Month

enrollment = enrollment[['state', 'year', 'month', 'num_enrollment_medicaid_chip', 'num_enrollment_medicaid']]
# collapse on averages based on the month 
enrollment = enrollment.groupby(['year', 'state'])[['num_enrollment_medicaid_chip', 
                                                    'num_enrollment_medicaid']].mean().reset_index()

# now we want to pull in a better dataset for asessing enrollment by age:
enrollment_granular = pd.read_csv(f'{raw_data}/medicaid_eligibility_group.csv')
enrollment_granular.columns = enrollment_granular.columns.str.lower()
enrollment_granular["countenrolled"] = enrollment_granular["countenrolled"].replace("DS", np.nan)
# Remove commas and convert to numeric (handles NaN safely)
enrollment_granular["num_enrollment_medicaid_chip_alt"] = (
    enrollment_granular["countenrolled"].str.replace(",", "").astype(float)
)

enrollment_granular['month'] = enrollment_granular['month'].astype(str)  
enrollment_granular['year'] = enrollment_granular['month'].str[:4].astype(int) 
enrollment_granular['month'] = enrollment_granular['month'].str[4:].astype(int)

# now we want to pivot wide 
wide = enrollment_granular.pivot(index=['state', 'month', 'year'], 
    columns='majoreligibilitygroup', values='num_enrollment_medicaid_chip_alt').reset_index()

wide.columns = wide.columns.str.lower()
wide.rename(
    columns = {
        'adult': 'num_enrollment_19_to_64_medicaid',
        'adult expansion group': 'num_enrollment_expansion_adult_medicaid',
        'aged': 'num_enrollment_65_and_over_medicaid',
        'covid newly-eligible': 'num_enrollment_covid_medicaid',
        'children': 'num_enrollment_under_18_medicaid',
        'persons with disabilities': 'num_enrollment_disabled_medicaid',
        'unknown': 'num_enrollment_unknown_medicaid'
    }, inplace=True
)

enrollment_cols = ['num_enrollment_19_to_64_medicaid', 'num_enrollment_expansion_adult_medicaid',
        'num_enrollment_65_and_over_medicaid', 'num_enrollment_covid_medicaid', 
        'num_enrollment_under_18_medicaid', 'num_enrollment_disabled_medicaid',
        'num_enrollment_unknown_medicaid']
wide = wide.groupby(['year', 'state'])[enrollment_cols].mean().reset_index()

# merge 
master = pd.merge(enrollment, wide, on=['year', 'state'], how='outer')

master['check'] = (
    master['num_enrollment_19_to_64_medicaid']
    + master['num_enrollment_expansion_adult_medicaid']
    + master['num_enrollment_65_and_over_medicaid']
    + master['num_enrollment_covid_medicaid']
    + master['num_enrollment_under_18_medicaid']
    + master['num_enrollment_disabled_medicaid']
    + master['num_enrollment_unknown_medicaid']
)

master.to_csv(f'{clean_data}/medicaid_enrollment.csv', index=False)

graphing = master[master['check'] != 0]
plt.scatter(graphing['check'], graphing['num_enrollment_medicaid_chip'], alpha=0.6)
x_values = np.linspace(min(graphing['check']), max(graphing['check']), 100)
plt.plot(x_values, x_values, color='red', linestyle='--', label='y = x')
plt.xlabel('Manually Summed')
plt.ylabel('Summed by Medicaid.gov')
plt.close