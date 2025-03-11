import pandas as pd
from pathlib import Path
# let's create a set of locals referring to our directory and working directory 
home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
cd_level = (clean_data / 'cd_level')
output = (work_dir / 'output')
code = Path.cwd() 

######################################################################################################################################
# Oct. 2024 Cross-Section 
######################################################################################################################################
oct_2024 = pd.read_excel(f'{raw_data}/2024_medicaid_enrollment.xlsx', header=3)

#####################
# State-Level Dataset
#####################

