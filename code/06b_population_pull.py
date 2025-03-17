import pandas as pd
from pathlib import Path
import requests
import re

home = Path.home()
work_dir = home / 'medicaid_project'
data = work_dir / 'data'
clean_data = data / 'clean'
state_level = clean_data / 'state_level'

# Define Census API base URL
BASE_URL = "https://api.census.gov/data/{year}/acs/acs5"

# Define years to pull data for
years = list(range(2012, 2025)) 

# Define the variable for total county population
pop_var = {
    "B01003_001E": "Total_Population_County"
}

# Convert dictionary keys into a comma-separated string for API request
variable_keys = ",".join(pop_var.keys())

# Initialize a list to store all data
all_data = []

# Function to clean and extract county and state from 'NAME' column
def parse_county_state(name):
    """Extracts 'County' and 'State' from NAME field, handling edge cases."""
    match = re.match(r"(.+), (.+)", name)  # Match "County Name, State Name"
    if match:
        return match.group(1), match.group(2)  # Extract county & state
    return None, None  # Handle unexpected cases

# Loop over each year
for year in years:
    print(f"Fetching data for {year}...")
    
    # Construct API URL for the given year
    api_url = f"{BASE_URL.format(year=year)}?get=NAME,{variable_keys}&for=county:*&in=state:*"

    # Make request to Census API
    response = requests.get(api_url)

    if response.status_code == 200:
        data_json = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data_json[1:], columns=data_json[0])
        
        # Rename columns for clarity
        df.rename(columns=pop_var, inplace=True)
        df.rename(columns={"NAME": "County"}, inplace=True)

        # Convert population values to numeric
        df["Total_Population_County"] = pd.to_numeric(df["Total_Population_County"], errors="coerce")

        # Add year column
        df["Year"] = year

        # Extract 'county_name' and 'state' from 'County' column
        df[["county_name", "state_name"]] = df["County"].apply(lambda x: pd.Series(parse_county_state(x)))

        # Drop original 'County' column (optional)
        df.drop(columns=["County"], inplace=True)

        # Append to the list
        all_data.append(df)

    else:
        print(f"❌ Error fetching data for {year}: {response.status_code}")

# Concatenate all years into a single DataFrame
final_df = pd.concat(all_data, ignore_index=True)

# Save to CSV
output_path = f"{clean_data}/acs5_county_population.csv"
final_df.to_csv(output_path, index=False)

print(f"✅ Data saved as '{output_path}'")
