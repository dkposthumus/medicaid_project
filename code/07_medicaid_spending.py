import pandas as pd
from pathlib import Path

# let's create a set of locals referring to our directory and working directory 
home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
spending = (raw_data / 'medicaid_spending_mac')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
county_level = (clean_data / 'cd_level')
output = (work_dir / 'output')
code = Path.cwd() 

states = pd.Series([
    "alabama",
    "alaska",
    "arizona",
    "arkansas",
    "california",
    "colorado",
    "connecticut",
    "delaware",
    "florida",
    "georgia",
    "hawaii",
    "idaho",
    "illinois",
    "indiana",
    "iowa",
    "kansas",
    "kentucky",
    "louisiana",
    "maine",
    "maryland",
    "massachusetts",
    "michigan",
    "minnesota",
    "mississippi",
    "missouri",
    "montana",
    "nebraska",
    "nevada",
    "new hampshire",
    "new jersey",
    "new mexico",
    "new york",
    "north carolina",
    "north dakota",
    "ohio",
    "oklahoma",
    "oregon",
    "pennsylvania",
    "rhode island",
    "south carolina",
    "south dakota",
    "tennessee",
    "texas",
    "utah",
    "vermont",
    "virginia",
    "washington",
    "west virginia",
    "wisconsin",
    "wyoming"
])

medicaid_spending = pd.DataFrame()
for year in range(2010, 2024):
    if year in range(2019, 2024):
        df = pd.read_excel(f'{spending}/{year}_medicaid_spending.xlsx', header=3)
    else:
        df = pd.read_csv(f'{spending}/{year}_medicaid_spending.csv', header=1)
    df.rename(
        columns = {
            'Unnamed: 0': 'state_name',
            'Total': 'benefits_total',
            'Federal': 'benefits_federal',
            'State': 'benefits_state',
            'Total.1': 'administration_total',
            'Federal.1': 'administration_federal',
            'State.1': 'administration_state',
            'Total.2': 'medicaid_total',
            'Federal.2': 'medicaid_federal',
            'State.2': 'medicaid_state'
        }, inplace=True
    )
    if year in range(2019, 2024):
        df.drop(columns={'Unnamed: 8', 'Unnamed: 10'}, inplace=True)
    df.columns = df.columns.str.lower()
    df['year'] = year 
    df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    df = df[df['state_name'].isin(states)]
    # create list of all columns in df except for 'state':
    cols = df.columns.drop('state_name').tolist()
    for col in cols:
        if pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].str.replace('$', '')
            df[col] = df[col].str.replace(',', '').astype(float)
    medicaid_spending = pd.concat([medicaid_spending, df], axis=0, ignore_index=True)

medicaid_spending.to_csv(f'{state_level}/medicaid_spending_state.csv', index=False)