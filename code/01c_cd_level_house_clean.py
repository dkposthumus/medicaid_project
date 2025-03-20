import pandas as pd
from pathlib import Path

home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
output = (work_dir / 'output')
code = Path.cwd() 

cd_level_house = pd.read_excel(f'{raw_data}/county_house_2024.xlsx', sheet_name='Cong Dist')

cd_level_house.columns = cd_level_house.columns.str.lower()

cd_level_house.rename(columns = {
    'unnamed: 0': 'cd119',
    'unnamed: 1': 'state_name',
    'total vote': 'total_house_votes',
    'democratic.1': 'democratic_house_votes',
    'republican.1': 'republican_house_votes'
}, inplace=True)
cd_level_house = cd_level_house[['cd119', 'state_name', 'total_house_votes', 
                   'democratic_house_votes', 'republican_house_votes']]

cd_level_house = cd_level_house.dropna(subset=['state_name'])

cd_level_house['year'] = 2024

state_mapping = {
    'AL': 'alabama', 'AK': 'alaska', 'AZ': 'arizona', 
    'AR': 'arkansas', 'CA': 'california',
    'CO': 'colorado', 'CT': 'connecticut', 'DE': 'delaware', 
    'FL': 'florida', 'GA': 'georgia',
    'HI': 'hawaii', 'ID': 'idaho', 'IL': 'illinois', 
    'IN': 'indiana', 'IA': 'iowa',
    'KS': 'kansas', 'KY': 'kentucky', 'LA': 'louisiana', 
    'ME': 'maine', 'MD': 'maryland',
    'MA': 'massachusetts', 'MI': 'michigan', 'MN': 'minnesota', 
    'MS': 'mississippi', 'MO': 'missouri',
    'MT': 'montana', 'NE': 'nebraska', 'NV': 'nevada', 
    'NH': 'new hampshire', 'NJ': 'new jersey',
    'NM': 'new mexico', 'NY': 'new york', 
    'NC': 'north carolina', 'ND': 'north dakota',
    'OH': 'ohio', 'OK': 'oklahoma', 'OR': 'oregon', 
    'PA': 'pennsylvania', 'RI': 'rhode island',
    'SC': 'south carolina', 'SD': 'south dakota', 'TN': 'tennessee', 
    'TX': 'texas', 'UT': 'utah',
    'VT': 'vermont', 'VA': 'virginia', 'WA': 'washington', 
    'WV': 'west virginia', 'WI': 'wisconsin', 'WY': 'wyoming'
}
cd_level_house['state_name'] = cd_level_house['state_name'].map(state_mapping)

cd_level_house = cd_level_house[cd_level_house['cd119'].str.contains('District', na=False) | (cd_level_house['cd119'] == 'At Large')]
# Modify 'cd119' column
cd_level_house['cd119'] = cd_level_house['cd119'].str.replace('District ', '', regex=False)  # Remove 'District'
cd_level_house.loc[cd_level_house['cd119'] == 'At Large', 'cd119'] = 0  # Set 'At Large' to 0
# Convert 'cd119' to integer (optional)
cd_level_house['cd119'] = cd_level_house['cd119'].astype(int)

cd_level_house = cd_level_house[cd_level_house['total_house_votes'] > 0]

cd_level_house.to_csv(f'{clean_data}/cd_level_house_2024.csv', index=False)