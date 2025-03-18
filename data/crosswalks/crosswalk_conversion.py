import pandas as pd
from pathlib import Path

home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
crosswalks = (data / 'crosswalks')

county_cd_crosswalk = pd.read_csv(
        f'{crosswalks}/county_cd.txt',
        sep='|',
        dtype={
            'GEOID_COUNTY_20': str,
            'GEOID_CD119_20': str
        }
    )
# now let's clean the county --> cd crosswalk 
county_cd_crosswalk.columns = county_cd_crosswalk.columns.str.lower() # all columns lowercase
# create 'state' variable equal to first two characters in GEO_ID column
county_cd_crosswalk['state'] = county_cd_crosswalk['geoid_county_20'].str[:2]
county_cd_crosswalk['county'] = county_cd_crosswalk['geoid_county_20'].str[2:5]
# now we want to clean the congressional district variable
county_cd_crosswalk['congressional district'] = county_cd_crosswalk['geoid_cd119_20'].str[2:4]
# keep only necessary columns
county_cd_crosswalk = county_cd_crosswalk[['state', 'county', 'congressional district',
                                            'geoid_county_20', 'geoid_cd119_20']]
# drop all other columns
county_cd_crosswalk.to_csv(f'{crosswalks}/county_cd.csv', index=False)

# now pull tract-level data
tract_cd_crosswalk = pd.read_csv(f'{crosswalks}/tract_cd_raw.csv', encoding='latin1',
                           dtype = {
                               'county': str,
                               'tract': str,
                               'state': str
                           })
tract_cd_crosswalk['county'] = tract_cd_crosswalk['county'].astype(str)
tract_cd_crosswalk['county'] = tract_cd_crosswalk['county'].str[2:5]

tract_cd_crosswalk.rename(columns={'pop20': 'pop_crosswalk', 'tract': 'tract_number'}, inplace=True)

tract_cd_crosswalk = tract_cd_crosswalk[['county', 'tract_number', 'state', 'cd119', 'pop_crosswalk']]

tract_cd_crosswalk.to_csv(f'{crosswalks}/tract_cd.csv', index=False)