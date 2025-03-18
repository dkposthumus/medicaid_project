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
cd_level = (clean_data / 'cd_level')
output = (work_dir / 'output')
code = Path.cwd() 

######################################################################################################################################
# Load in state-level datasets
######################################################################################################################################

# medicaid births
medicaid_births = pd.read_csv(f'{state_level}/kff_births_2016_2023.csv')
# medicaid enrollment (ONLY 2024)
oct_2024_medicaid_chips_enrollment = pd.read_csv(f'{state_level}/oct_2024_enrollment_state.csv')
# medicaid enrollment (full time-series)
medicaid_enrollment = pd.read_csv(f'{state_level}/medicaid_education_state.csv')
# let's concatenate our two medicaid_enrollment datasets
#medicaid_enrollment = pd.concat([oct_2024_medicaid_chips_enrollment, medicaid_enrollment], axis=0, ignore_index=True)
# state government partisan control
state_govt_ctrl = pd.read_csv(f'{state_level}/state_trifectas_ballotpedia_scrape.csv')
# presidential election results (2000-2024)
pres_election_results = pd.read_csv(f'{election_results}/pres_election_2000_2024_state.csv')
# fmap percentages and multiplier
fmap = pd.read_csv(f'{state_level}/fmap_state.csv')
# medicaid spending
medicaid_spending = pd.read_csv(f'{state_level}/medicaid_spending_state.csv')

for df in [medicaid_births, medicaid_enrollment, 
           state_govt_ctrl, pres_election_results, fmap, medicaid_spending]:
    df.loc[df['state_name'] == "hawai'i", 'state_name'] = 'hawaii'

# merge all state-level datasets pulled in
master = pd.merge(medicaid_births, medicaid_enrollment, on=['state_name', 'year'], how='outer')
master = pd.merge(master, state_govt_ctrl, on=['year', 'state_name'], how='outer')
master = pd.merge(master, pres_election_results, on=['year', 'state_name'], how='outer')
master = pd.merge(master, fmap, on=['year', 'state_name'], how='outer')
master = pd.merge(master, medicaid_spending, on=['year', 'state_name'], how='outer')

# create dummy if a usa state, as opposed to a territory
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
master['usa_state_dummy'] = (master['state_name'].isin(states)).astype(int)

# save master dataset
master.to_csv(f'{clean_data}/master_state_level.csv', index=False)