import pandas as pd
from pathlib import Path
# let's create a set of locals referring to our directory and working directory 
home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
election_results = (state_level / 'election_results')
county_level = (clean_data / 'county_level')
output = (work_dir / 'output')
code = Path.cwd() 

# pull in county-level enrollment variables 
enrollment_education = pd.read_csv(f'{county_level}/medicaid_education_county.csv')
house_2020_2024 = pd.read_csv(f'{clean_data}/house_2020_2024.csv')
house_2020_2024.rename(
    columns={'county_name': 'county'}, inplace=True
)
pres = pd.read_csv(f'{clean_data}/pres_election_2000_2024_county.csv')
senate_2020_2024 = pd.read_csv(f'{clean_data}/senate_2020_2024.csv')

master = pd.merge(enrollment_education, house_2020_2024, left_on='county', right_on='county_name')