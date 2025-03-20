import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

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

# we want to do a bunch of scatterplots

# first: pct_enrollment in medicaid and education (% high school or less) (fixed to 2024)
df_2024 = master[master['year'] == 2024]
x = df_2024['pct_college_plus']
y = df_2024['pct_enrollment_medicaid_gov']
plt.scatter(x, y)
plt.xlabel('%\ of Population w/Post-Secondary Studies')
plt.ylabel('%\ Enrolled in Medicaid')
plt.show()


party_mapping = {
    'r': ('Republican', 'red'),
    'd': ('Democratic', 'blue')
}
# Create scatter plot
plt.figure(figsize=(8, 6))  # Adjust figure size
for value, (party_label, color) in party_mapping.items():
    party_df = df_2024[df_2024['r_cd'] == value]  # Filter data
    plt.scatter(party_df['pct_college_plus'], party_df['pct_enrollment_medicaid_gov'],
                label=party_label, color=color, alpha=0.7)
plt.xlabel('% of Population w/Post-Secondary Studies')
plt.ylabel('% Enrolled in Medicaid')
plt.legend(title="Party")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()