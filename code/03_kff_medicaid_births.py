import pandas as pd
from pathlib import Path
# let's create a set of locals referring to our directory and working directory 
home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
output = (work_dir / 'output')
code = Path.cwd() 

# specify the place where the raw KFF medicaid births data is located 
kff_data = (raw_data / 'kff_medicaid_births')
kff_cleaned = pd.DataFrame()
# loop through for each year 
for year in range(2016, 2024):
    #print(year)
    df = pd.read_csv(f'{kff_data}/kff_medicaid_births_{year}.csv', header=2)
    df['year'] = year # create year column
    #print(year)
    #print(df['Number of Births Financed by Medicaid'].dtype)
    if pd.api.types.is_string_dtype(df['Number of Births Financed by Medicaid']):
        # small problem: number of births includes commas; drop the commas and convert into int.type 
        df['Number of Births Financed by Medicaid'] = df['Number of Births Financed by Medicaid'].str.replace(',', '').astype(float)
    kff_cleaned = pd.concat([kff_cleaned, df], axis=0, ignore_index=True)

kff_cleaned.rename(
    columns = {
        'Location': 'state_name',
        'Number of Births Financed by Medicaid': 'medicaid_births',
        'Percent of Births Financed by Medicaid': 'pct_medicaid_births'
    }, inplace=True
)
kff_cleaned = kff_cleaned[kff_cleaned['state_name'] != 'United States'] # make sure we only have states, NOT the national total
kff_cleaned = kff_cleaned.applymap(lambda x: x.lower() if isinstance(x, str) else x) # make all values (really just states) lowercase
# now drop all observations where medicaid_births is missing
kff_cleaned = kff_cleaned.dropna(subset=['medicaid_births'])

# now save in cleaned dataset 
kff_cleaned.to_csv(f'{state_level}/kff_births_2016_2023.csv', index=False)