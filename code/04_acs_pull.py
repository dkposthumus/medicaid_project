import requests
import pandas as pd
from pathlib import Path
# let's create a set of locals referring to our directory and working directory 
home = Path.home()
work_dir = (home / 'medicaid_project')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
state_level = (clean_data / 'state_level')
county_level = (clean_data / 'cd_level')
output = (work_dir / 'output')
code = Path.cwd() 

# Define API base URL for ACS 1-Year Data
BASE_URL = "https://api.census.gov/data"

# Define the variables from Table C27007 (Medicaid by Sex and Age) with Medicaid explicitly in names
medicaid_vars = {
    ## pull population vars
    "C27007_003E": "male_19_pop_acs",
    "C27007_006E": "male_19_64_pop_acs",
    "C27007_009E": "male_65_pop_acs",
    "C27007_013E": "female_19_pop_acs",
    "C27007_016E": "female_19_64_pop_acs",
    "C27007_019E": "female_65_pop_acs",

    ## pull medicaid enrollment vars
    "C27007_004E": "num_male_19_medicaid_acs",
    "C27007_007E": "num_male_19_64_medicaid_acs",
    "C27007_010E": "num_male_65_medicaid_acs",
    "C27007_014E": "num_female_19_medicaid_acs",
    "C27007_017E": "num_female_19_64_medicaid_acs",
    "C27007_020E": "num_female_65_medicaid_acs",
}

########################################################################
# PART 2: Pull ACS 5-Year Data (Census Tracts) for 2012–2024
########################################################################

"""
Pull Medicaid + Education data from ACS 5-Year Data for all census tracts in the US
from 2012 to 2024.
Note: "No Medicaid data before 2009" – typically 5-year ACS for 2009 includes 2005–2009,
  but we’ll respect your original note and start at 2012. Adjust as needed.
"""

BASE_URL_TEMPLATE_5YR = "https://api.census.gov/data/{year}/acs/acs5"

# List of all state FIPS codes (50 states + DC)
state_fips_codes = [
    "01","02","04","05","06","08","09","10","11","12","13","15","16","17",
    "18","19","20","21","22","23","24","25","26","27","28","29","30","31",
    "32","33","34","35","36","37","38","39","40","41","42","44","45","46",
    "47","48","49","50","51","53","54","55","56",
]

# Range of years you want to attempt for ACS 5-year
years_5yr = list(range(2012, 2025))  # 2012 through 2024

# Combine the same dictionaries for 5-year
variables_5yr = {**medicaid_vars}
variable_keys_5yr = ",".join(variables_5yr.keys())

# Initialize an empty list to store the data
all_data_5yr = []

# Loop through each year
for year in years_5yr:
    print(f"Fetching 5-year data for {year}...")

    # Loop through each state and fetch census tract data
    for state_fips in state_fips_codes:
        print(f"  - State FIPS {state_fips} in {year}...")
        # Construct the API URL for the given year and state
        api_url_5yr = (
            f"{BASE_URL_TEMPLATE_5YR.format(year=year)}"
            f"?get=NAME,{variable_keys_5yr}"
            f"&for=tract:*&in=state:{state_fips}"
        )

        # Fetch data from the Census API
        response_5yr = requests.get(api_url_5yr)

        if response_5yr.status_code == 200:
            data_json_5yr = response_5yr.json()
            df_5yr = pd.DataFrame(data_json_5yr[1:], columns=data_json_5yr[0])

            # Rename columns
            df_5yr.rename(columns=variables_5yr, inplace=True)
            df_5yr.rename(columns={"NAME": "Census_Tract"}, inplace=True)

            # Convert numeric columns to numeric dtype
            for col in variables_5yr.values():
                df_5yr[col] = pd.to_numeric(df_5yr[col], errors="coerce")

            # Add year column
            df_5yr["Year"] = year

# Combine all 5-year data
if all_data_5yr:
    final_df_5yr = pd.concat(all_data_5yr, ignore_index=True)
    # Save as a single CSV file
    output_path_5yr = f"{clean_data}/acs5_tract.csv"
    final_df_5yr.to_csv(output_path_5yr, index=False)
    print(f"5-year data saved to '{output_path_5yr}'")
else:
    print("No 5-year data collected. Skipping file save for ACS5.")