import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
output = (work_dir / 'output')
code = Path.cwd() 

master = pd.read_csv(f'{clean_data}/master_cd.csv')
master['cd119'] = master['cd119'].astype(str)
master['cd-state'] = (master['cd119'] + '-' + master['state_name'])
master = master[master['year'] == 2024]

# Create scatter plot
plt.figure(figsize=(8, 6))  # Adjust figure size
dem_df = master[master['r_cd'] == 'd']
rep_df = master[master['r_cd'] == 'r']
close_df = master[master['close_race'] == 1]
for df, type, color in zip([dem_df, rep_df, close_df],
                        ['Democratic', 'Republican', 'Close-Call'],
                       ['blue', 'red', 'purple']):
    sns.kdeplot(df['pct_enrollment_medicaid_chip_gov'], 
                label=f'{type} Congressional Districts (119th)', 
                shade=False, linewidth=2, color=color)
plt.legend()
plt.show()