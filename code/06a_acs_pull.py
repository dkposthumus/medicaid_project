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
years = list(range(2009, 2024))

# Define the variables from Table C27007 (Medicaid by Sex and Age) with Medicaid explicitly in names
variables = {
    "B01003_001E": "Total_Population_County",  # Total population of the county
    "C27007_001E": "Total_Population_Medicaid",
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

# Initialize an empty DataFrame to store all years of data
all_years_data = []

# Loop over each year to fetch data
for year in years:
    print(f"Fetching data for {year}...")
    api_url = f"{BASE_URL}/{year}/acs/acs1?get=NAME,{','.join(variables.keys())}&for=county:*&in=state:*"

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])  # Convert JSON to DataFrame

        # Rename columns to descriptive names
        df.rename(columns=variables, inplace=True)
        df.rename(columns={"NAME": "County"}, inplace=True)

        # Add year column
        df["Year"] = year

        # Convert numeric columns
        for col in variables.values():
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Append to the list
        all_years_data.append(df)
    else:
        print(f"Skipping {year}: C27007 not available (Error {response.status_code})")

# Concatenate all years into a single DataFrame
final_df = pd.concat(all_years_data, ignore_index=True)

# Save to CSV
output_path = f"{county_level}/acs1_c27007_medicaid_all_counties_2009_2023.csv"
final_df.to_csv(output_path, index=False)

print(f"Data saved as '{output_path}'")

"""
Pull Medicaid data from ACS 5-Year Data (Table C27007) for all census tracts in the US from 2009 to 2023.
No data in 2020.
No Medicaid data before 2012.
"""
BASE_URL_TEMPLATE = "https://api.census.gov/data/{year}/acs/acs5"

# Define variables
variables = {
    "B01003_001E": "Total_Population_Census_Tract",
    "C27007_001E": "Total_Population",
    "C27007_002E": "Male_Total",
    "C27007_003E": "Male_Under_19",
    "C27007_004E": "Male_Under_19_With_Medicaid",
    "C27007_005E": "Male_Under_19_No_Medicaid",
    "C27007_006E": "Male_19_to_64",
    "C27007_007E": "Male_19_to_64_With_Medicaid",
    "C27007_008E": "Male_19_to_64_No_Medicaid",
    "C27007_009E": "Male_65_and_Over",
    "C27007_010E": "Male_65_and_Over_With_Medicaid",
    "C27007_011E": "Male_65_and_Over_No_Medicaid",
    "C27007_012E": "Female_Total",
    "C27007_013E": "Female_Under_19",
    "C27007_014E": "Female_Under_19_With_Medicaid",
    "C27007_015E": "Female_Under_19_No_Medicaid",
    "C27007_016E": "Female_19_to_64",
    "C27007_017E": "Female_19_to_64_With_Medicaid",
    "C27007_018E": "Female_19_to_64_No_Medicaid",
    "C27007_019E": "Female_65_and_Over",
    "C27007_020E": "Female_65_and_Over_With_Medicaid",
    "C27007_021E": "Female_65_and_Over_No_Medicaid",
}

# List of all state FIPS codes (50 states + DC)
state_fips_codes = [
    "01",
    "02",
    "04",
    "05",
    "06",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
    "31",
    "32",
    "33",
    "34",
    "35",
    "36",
    "37",
    "38",
    "39",
    "40",
    "41",
    "42",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "50",
    "51",
    "53",
    "54",
    "55",
    "56",
]

# List of years to query (adjust if older ACS 5-year data is needed)
years = list(range(2012, 2023))  # Modify as needed to include older years

# Convert variable dictionary keys into a comma-separated string for the API request
variable_str = ",".join(variables.keys())

# Initialize an empty list to store all years' data
all_data = []

# Loop through each year
for year in years:
    print(f"Fetching data for {year}...")

    # Loop through each state and fetch census tract data
    for state_fips in state_fips_codes:
        print(f"  - Fetching data for state FIPS {state_fips} in {year}...")

        # Construct the API URL for the given year and state
        api_url = f"{BASE_URL_TEMPLATE.format(year=year)}?get=NAME,{variable_str}&for=tract:*&in=state:{state_fips}"

        # Fetch data from the Census API
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0])  # Convert JSON to DataFrame

            # Rename columns for clarity using the dictionary
            df.rename(columns=variables, inplace=True)
            df.rename(columns={"NAME": "Census_Tract"}, inplace=True)

            # Convert numeric columns to appropriate data type
            for col in variables.values():
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Add year column
            df["Year"] = year

            # Append data to the list
            all_data.append(df)
        else:
            print(
                f"  ⚠️ Error fetching data for state {state_fips} in {year}: {response.status_code}, {response.text}"
            )

# Combine all data into a single DataFrame
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)

    # Save as a single CSV file
    output_path = f"{county_level}/acs5_medicaid_enrollment_all_years.csv"
    final_df.to_csv(output_path, index=False)

    print(f"All years' data saved as '{output_path}'")
else:
    print("No data collected. Skipping file save.")
