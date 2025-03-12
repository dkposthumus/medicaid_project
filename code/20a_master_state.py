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
medicaid_enrollment = pd.read_csv(f'{state_level}/medicaid_enrollment_state.csv')
# let's concatenate our two medicaid_enrollment datasets
medicaid_enrollment = pd.concat([oct_2024_medicaid_chips_enrollment, medicaid_enrollment], axis=0, ignore_index=True)
# state government partisan control
state_govt_ctrl = pd.read_csv(f'{state_level}/state_trifectas_ballotpedia_scrape.csv')
# presidential election results (2000-2024)
pres_election_results = pd.read_csv(f'{election_results}/pres_election_2000_2024_state.csv')
# fmap percentages and multiplier
fmap = pd.read_csv(f'{state_level}/fmap_state.csv')
# medicaid spending
medicaid_spending = pd.read_csv(f'{state_level}/medicaid_spending_state.csv')

# merge all state-level datasets pulled in
master = pd.merge(medicaid_births, medicaid_enrollment, on=['state', 'year'], how='outer')
master = pd.merge(master, state_govt_ctrl, on=['year', 'state'], how='outer')
master = pd.merge(master, pres_election_results, on=['year', 'state'], how='outer')
master = pd.merge(master, fmap, on=['year', 'state'], how='outer')
master = pd.merge(master, medicaid_spending, on=['year', 'state'], how='outer')

# save master dataset
master.to_csv(f'{clean_data}/master_state_level.csv', index=False)

