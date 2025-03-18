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

######################################################################################################################################
# FMAP (not-enhanced) state-leel data 
######################################################################################################################################
# specify the place where the raw KFF medicaid births data is located 
kff_data = (raw_data / 'kff_fmap')
fmap_cleaned = pd.DataFrame()
# loop through for each year 
for year in range(2004, 2027):
    #print(year)
    df = pd.read_csv(f'{kff_data}/fmap_{year}.csv', header=2)
    df.drop(columns={'Footnotes'}, inplace=True)
    df['year'] = year # create year column
    #print(year)
    #print(df['Number of Births Financed by Medicaid'].dtype)
    for col in ['FMAP Percentage', 'Multiplier']:
        if pd.api.types.is_string_dtype(df[col]):
            # small problem: number of births includes commas; drop the commas and convert into int.type 
            df[col] = df[col].str.replace(',', '').astype(float)
            df[col] = df[col].str.replace('%', '').astype(float)
        df = df.dropna(subset=col)
    fmap_cleaned = pd.concat([fmap_cleaned, df], axis=0, ignore_index=True)
fmap_cleaned.rename(
    columns = {
        'Location': 'state_name',
        'FMAP Percentage': 'fmap_pct',
        'Multiplier': 'fmap_multiplier'
    }, inplace=True
)
# now replace everything with lowercase values for 'state' column 
fmap_cleaned = fmap_cleaned.applymap(lambda x: x.lower() if isinstance(x, str) else x)
fmap_cleaned = fmap_cleaned[fmap_cleaned['state_name'] != 'united states']

######################################################################################################################################
# Enhanced FMAP state-level data
######################################################################################################################################
kff_data = (raw_data / 'kff_enhanced_fmap')
enhanced_cleaned = pd.DataFrame()
# loop through for each year 
for year in range(2003, 2027):
    #print(year)
    df = pd.read_csv(f'{kff_data}/enhanced_{year}.csv', header=2)
    df.drop(columns={'Footnotes'}, inplace=True)
    df['year'] = year # create year column
    #print(year)
    #print(df['Number of Births Financed by Medicaid'].dtype)
    for col in ['Enhanced FMAP']:
        if pd.api.types.is_string_dtype(df[col]):
            # small problem: number of births includes commas; drop the commas and convert into int.type 
            df[col] = df[col].str.replace(',', '').astype(float)
            df[col] = df[col].str.replace('%', '').astype(float)
        df = df.dropna(subset=col)
    enhanced_cleaned = pd.concat([enhanced_cleaned, df], axis=0, ignore_index=True)
enhanced_cleaned.rename(
    columns = {
        'Location': 'state_name',
        'Enhanced FMAP': 'enhanced_fmap_pct'
    }, inplace=True
)
# now replace everything with lowercase values for 'state' column 
enhanced_cleaned = enhanced_cleaned.applymap(lambda x: x.lower() if isinstance(x, str) else x)
enhanced_cleaned = enhanced_cleaned[enhanced_cleaned['state_name'] != 'united states']

# now merge two fmap datasets together
fmap_master = pd.merge(enhanced_cleaned, fmap_cleaned, on=['year', 'state_name'], how='outer')

fmap_master.to_csv(f'{state_level}/fmap_state.csv', index=False)