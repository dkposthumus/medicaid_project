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
        'total medicaid and chip enrollment': 'num_medicaid_chip_gov',
        'total medicaid enrollment': 'num_medicaid_gov',
        'state name': 'state_name'
    }, inplace=True
)
enrollment['reporting period'] = enrollment['reporting period'].astype(str)  
# Extract year and month
enrollment['year'] = enrollment['reporting period'].str[:4].astype(int)   # First 4 digits → Year
enrollment['month'] = enrollment['reporting period'].str[4:].astype(int)  # Last 2 digits → Month

# restrict enrollment data to when 'final report' == 'Y' EXCEPT for when 'year' == 2024 and 'month' == 10
enrollment = enrollment[(enrollment['final report'] == 'Y') | ((enrollment['year'] == 2024) & (enrollment['month'] == 10))]
enrollment = enrollment[['state_name', 'year', 'month', 'num_medicaid_chip_gov', 'num_medicaid_gov']]

# quick check that 'state_name', 'year', and 'month' are unique identifiers
duplicates = enrollment.duplicated(subset=['state_name', 'year', 'month'], keep=False)
# Print rows that are duplicated
if duplicates.any():
    print("⚠️ Duplicate rows found for ('state_name', 'year', 'month')!")
    #display(enrollment[duplicates].sort_values(['state_name', 'year', 'month']))
else:
    print("✅ 'state_name', 'year', and 'month' uniquely identify each row.")

# before averaging; let's note that we're missing november/december for 2024 data; let's plot the average by month to make sure these months don't tend to be lower
enrollment_filtered = enrollment[enrollment['year'].between(2021, 2023)]
enrollment_2024 = enrollment[enrollment['year'] == 2024]
for df, label in zip([enrollment, enrollment_filtered, enrollment_2024], ['All Years', '2021-2023', '2024 Only']):
    monthly_avg = df.groupby('month').mean(numeric_only=True)
    # Plot the average values by month
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_avg.index, monthly_avg['num_medicaid_gov'], marker='o', linestyle='-')
    # Labels and title
    plt.xlabel("Month")
    plt.ylabel("Average Medicaid Enrollment (Millions)")
    plt.title(f"Average Medicaid Enrollment by Month (Across {label})")
    plt.xticks(ticks=range(1, 13), labels=[
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ])
    plt.grid(True)
    plt.show()

# collapse on averages based on the month 
enrollment = enrollment.groupby(['year', 'state_name'])[['num_medicaid_chip_gov', 
                                                    'num_medicaid_gov']].mean().reset_index()

# now we want to pull in a better dataset for asessing enrollment by age:
enrollment_granular = pd.read_csv(f'{raw_data}/medicaid_eligibility_group.csv')
enrollment_granular.columns = enrollment_granular.columns.str.lower()
enrollment_granular.rename(columns={'state': 'state_name'}, inplace=True)
enrollment_granular["countenrolled"] = enrollment_granular["countenrolled"].replace("DS", np.nan)
# Remove commas and convert to numeric (handles NaN safely)
enrollment_granular["num_enrollment_medicaid_chip_alt"] = (
    enrollment_granular["countenrolled"].str.replace(",", "").astype(float)
)

enrollment_granular['month'] = enrollment_granular['month'].astype(str)  
enrollment_granular['year'] = enrollment_granular['month'].str[:4].astype(int) 
enrollment_granular['month'] = enrollment_granular['month'].str[4:].astype(int)

# now we want to pivot wide 
wide = enrollment_granular.pivot(index=['state_name', 'month', 'year'], 
    columns='majoreligibilitygroup', values='num_enrollment_medicaid_chip_alt').reset_index()

wide.columns = wide.columns.str.lower()
wide.rename(
    columns = {
        'adult': 'num_19_to_64_medi_chip_gov',
        'adult expansion group': 'num_expansion_medi_chip_gov',
        'aged': 'num_65_medi_chip_gov',
        'covid newly-eligible': 'num_covid_medi_chip_gov',
        'children': 'num_18_medi_chip_gov',
        'persons with disabilities': 'num_disabled_medi_chip_gov',
        'unknown': 'num_unknown_med_chip_gov'
    }, inplace=True
)

enrollment_cols = ['num_19_to_64_medi_chip_gov', 'num_expansion_medi_chip_gov', 'num_65_medi_chip_gov',
'num_covid_medi_chip_gov', 'num_18_medi_chip_gov', 'num_disabled_medi_chip_gov', 
'num_unknown_med_chip_gov']
wide = wide.groupby(['year', 'state_name'])[enrollment_cols].mean().reset_index()

# merge 
master = pd.merge(enrollment, wide, on=['year', 'state_name'], how='outer')

master['check'] = (
    master['num_19_to_64_medi_chip_gov']
    + master['num_expansion_medi_chip_gov']
    + master['num_65_medi_chip_gov']
    + master['num_covid_medi_chip_gov']
    + master['num_18_medi_chip_gov']
    + master['num_disabled_medi_chip_gov']
    + master['num_unknown_med_chip_gov']
)

master.to_csv(f'{clean_data}/medicaid_enrollment.csv', index=False)

graphing = master[master['check'] != 0]
plt.scatter(graphing['check'], graphing['num_medicaid_chip_gov'], alpha=0.6)
x_values = np.linspace(min(graphing['check']), max(graphing['check']), 100)
plt.plot(x_values, x_values, color='red', linestyle='--', label='y = x')
plt.xlabel('Manually Summed')
plt.ylabel('Summed by Medicaid.gov')
plt.show()