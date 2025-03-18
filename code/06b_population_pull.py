import pandas as pd
from pathlib import Path
import requests
import re

home = Path.home()
work_dir = home / 'medicaid_project'
data = work_dir / 'data'
clean_data = data / 'clean'
state_level = clean_data / 'state_level'
tract_level = clean_data / 'tract_level'

# Define Census API base URL
BASE_URL = "https://api.census.gov/data/{year}/acs/acs5"

# Define years to pull data for
years = list(range(2012, 2025)) 

# Define the variable for total county population
pop_var = {
    "B01003_001E": "Total_Population_Tract"
}

api_key = '680d2ddd22bf2e45296e8e9e8040df38e7740f7d'

# Convert dictionary keys into a comma-separated string for API request
variable_keys = ",".join(pop_var.keys())

# Initialize a list to store all data
all_data = []

# Function to clean and extract county and state from 'NAME' column
def parse_tract_name(name):
    # This regex assumes the pattern "Census Tract <tract_number>, <County Name>, <State Name>"
    match = re.search(r"Census Tract ([\d\.]+), (.+), (.+)", str(name), re.IGNORECASE)
    if match:
        # match.group(1) is the tract number as a string, group(2) is the county, group(3) is the state
        return match.group(1), match.group(2), match.group(3)
    return None, None, None

states = [
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15",
    "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27",
    "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
    "40", "41", "42", "44", "45", "46", "47", "48", "49", "50", "51", "53",
    "54", "55", "56"
]

for year in years:
    print(f"Fetching data for {year}...")
    for state in states:
        api_url = f"{BASE_URL.format(year=year)}?key={api_key}&get=NAME,{variable_keys}&for=tract:*&in=state:{state}"
        #print(api_url)
        response = requests.get(api_url)

        if response.status_code == 200:
            if response.text:
                data_json = response.json()
                df = pd.DataFrame(data_json[1:], columns=data_json[0])
                df.rename(columns=pop_var, inplace=True)
                df["Total_Population_Tract"] = pd.to_numeric(df["Total_Population_Tract"], errors="coerce")
                df["year"] = year
                df[["tract_number", "county_name", "state_name"]] = df["NAME"].apply(lambda x: pd.Series(parse_tract_name(x)))
                all_data.append(df)
            else:
                print(f"❌ Error fetching data for {year}, state {state}: Empty Response")
        else:
            print(f"❌ Error fetching data for {year}, state {state}: {response.status_code}")
            print("Response Text:", response.text)

final_df = pd.concat(all_data, ignore_index=True)
output_path = f"{tract_level}/acs5_tract_population.csv"
final_df.to_csv(output_path, index=False)
print(f"✅ Data saved as '{output_path}'")