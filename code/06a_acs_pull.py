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

"""
Pull Medicaid data from ACS 1-Year Data (Table C27007) for all counties in the US from 2009 to 2023.
No data in 2020.
No Medicaid data before 2009.
"""
# Define API base URL for ACS 1-Year Data
BASE_URL = "https://api.census.gov/data"
years_1yr = list(range(2009, 2025))

# Define the variables from Table C27007 (Medicaid by Sex and Age) with Medicaid explicitly in names
medicaid_vars = {
    "C27007_002E": "Male_Total_Medicaid",
    "C27007_003E": "Male_Under_19_Medicaid",
    "C27007_004E": "Male_Under_19_With_Medicaid",
    "C27007_005E": "Male_Under_19_No_Medicaid",
    "C27007_006E": "Male_19_to_64_Medicaid",
    "C27007_007E": "Male_19_to_64_With_Medicaid",
    "C27007_008E": "Male_19_to_64_No_Medicaid",
    "C27007_009E": "Male_65_and_Over_Medicaid",
    "C27007_010E": "Male_65_and_Over_With_Medicaid",
    "C27007_011E": "Male_65_and_Over_No_Medicaid",
    "C27007_012E": "Female_Total_Medicaid",
    "C27007_013E": "Female_Under_19_Medicaid",
    "C27007_014E": "Female_Under_19_With_Medicaid",
    "C27007_015E": "Female_Under_19_No_Medicaid",
    "C27007_016E": "Female_19_to_64_Medicaid",
    "C27007_017E": "Female_19_to_64_With_Medicaid",
    "C27007_018E": "Female_19_to_64_No_Medicaid",
    "C27007_019E": "Female_65_and_Over_Medicaid",
    "C27007_020E": "Female_65_and_Over_With_Medicaid",
    "C27007_021E": "Female_65_and_Over_No_Medicaid",
}

edu_vars = {
    "B15003_001E": "Pop_25_Over",
    "B15003_002E": "No_Schooling",
    "B15003_003E": "Nursery_4th",
    "B15003_004E": "Gr5_6",
    "B15003_005E": "Gr7_8",
    "B15003_006E": "Gr9",
    "B15003_007E": "Gr10",
    "B15003_008E": "Gr11",
    "B15003_009E": "Gr12_No_Diploma",
    "B15003_010E": "HighSchool_Grad",
    "B15003_011E": "SomeCollege_LT1yr",
    "B15003_012E": "SomeCollege_1plus",
    "B15003_013E": "Associates",
    "B15003_014E": "Bachelors",
    "B15003_015E": "Masters",
    "B15003_016E": "ProfSchool",
    "B15003_017E": "Doctorate",
}

pop_var = {
    "B01003_001E": "Total_Population_County"
}

variables_1yr = {**pop_var, **medicaid_vars, **edu_vars}
variable_keys_1yr = ",".join(variables_1yr.keys())

# Initialize an empty DataFrame to store all years of data
all_years_data_1yr = []

# Loop over each year to fetch data
for year in years_1yr:
    print(f"Fetching 1-year data for {year}...")
    api_url = (
        f"{BASE_URL}/{year}/acs/acs1?get=NAME,{variable_keys_1yr}"
        "&for=county:*&in=state:*"
    )

    response = requests.get(api_url)

    if response.status_code == 200:
        data_json = response.json()
        df = pd.DataFrame(data_json[1:], columns=data_json[0])  # Convert JSON to DataFrame

        # Rename columns using our dictionary
        df.rename(columns=variables_1yr, inplace=True)
        df.rename(columns={"NAME": "County"}, inplace=True)

        # Add a 'Year' column
        df["Year"] = year

        # Convert numeric columns to numeric dtype
        for col in variables_1yr.values():
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # --------------------------------------------------
        # DERIVE EDUCATIONAL ATTAINMENT PERCENTAGES
        # --------------------------------------------------
        # Avoid division by zero (Pop_25_Over might be 0 in small counties).
        df["Pop_25_Over"] = df["Pop_25_Over"].replace({0: None})

        # % with Bachelor's or higher
        df["Pct_College_Plus"] = (
            (df["Bachelors"] + df["Masters"] + df["ProfSchool"] + df["Doctorate"])
            / df["Pop_25_Over"]
            * 100
        )

        # % with exactly high school (includes equivalency)
        df["Pct_HS_Only"] = (
            df["HighSchool_Grad"] / df["Pop_25_Over"] * 100
        )

        # % with High School or less (HS grad + anything below)
        df["Pct_HS_or_Less"] = (
            (
                df["No_Schooling"]
                + df["Nursery_4th"]
                + df["Gr5_6"]
                + df["Gr7_8"]
                + df["Gr9"]
                + df["Gr10"]
                + df["Gr11"]
                + df["Gr12_No_Diploma"]
                + df["HighSchool_Grad"]
            )
            / df["Pop_25_Over"]
            * 100
        )

        # Append this DataFrame to our list
        all_years_data_1yr.append(df)
    else:
        print(f"Skipping {year}: Error {response.status_code} ({response.text})")

# Concatenate all years into a single DataFrame
if len(all_years_data_1yr) > 0:
    final_df_1yr = pd.concat(all_years_data_1yr, ignore_index=True)
    # Save to CSV
    output_path_1yr = f"{clean_data}/acs1_county.csv"
    final_df_1yr.to_csv(output_path_1yr, index=False)
    print(f"1-year data saved to '{output_path_1yr}'")
else:
    print("No 1-year data collected. Skipping file save for ACS1.")

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
variables_5yr = {**pop_var, **medicaid_vars, **edu_vars}
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

            # --------------------------------------------------
            # DERIVE EDUCATIONAL ATTAINMENT PERCENTAGES
            # --------------------------------------------------
            df_5yr["Pop_25_Over"] = df_5yr["Pop_25_Over"].replace({0: None})

            df_5yr["Pct_College_Plus"] = (
                (df_5yr["Bachelors"] + df_5yr["Masters"] + df_5yr["ProfSchool"] + df_5yr["Doctorate"])
                / df_5yr["Pop_25_Over"]
                * 100
            )
            df_5yr["Pct_HS_Only"] = (
                df_5yr["HighSchool_Grad"] / df_5yr["Pop_25_Over"] * 100
            )
            df_5yr["Pct_HS_or_Less"] = (
                (
                    df_5yr["No_Schooling"]
                    + df_5yr["Nursery_4th"]
                    + df_5yr["Gr5_6"]
                    + df_5yr["Gr7_8"]
                    + df_5yr["Gr9"]
                    + df_5yr["Gr10"]
                    + df_5yr["Gr11"]
                    + df_5yr["Gr12_No_Diploma"]
                    + df_5yr["HighSchool_Grad"]
                )
                / df_5yr["Pop_25_Over"]
                * 100
            )

            # Append to all_data_5yr
            all_data_5yr.append(df_5yr)
        else:
            print(
                f"  ⚠️ Error for state {state_fips} in {year}: "
                f"{response_5yr.status_code}, {response_5yr.text}"
            )

# Combine all 5-year data
if all_data_5yr:
    final_df_5yr = pd.concat(all_data_5yr, ignore_index=True)
    # Save as a single CSV file
    output_path_5yr = f"{clean_data}/acs5_county.csv"
    final_df_5yr.to_csv(output_path_5yr, index=False)
    print(f"5-year data saved to '{output_path_5yr}'")
else:
    print("No 5-year data collected. Skipping file save for ACS5.")