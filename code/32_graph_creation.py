import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
output = (work_dir / 'output')
code = Path.cwd() 

## pull in county-level and state-level master data 
state_level = pd.read_csv(f'{clean_data}/master_state_level.csv')

######################################################################################################################################
# Change in medicaid enrollment against change in turmp vote share 
######################################################################################################################################
