import pandas as pd
from pathlib import Path
import warnings # suppress noisy warnings in jupyter output
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

# let's create a set of locals referring to our directory and working directory 
home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
output = (work_dir / 'output')
code = Path.cwd() 

historic_house = pd.read_csv(f'{raw_data}/1976_2022_house.csv')
