import pandas as pd
import json


# Function to convert CSV to JSON with validation (removes empty fields and excludes 'MoSCoW' field)
def csv_to_json(input_file, output_file):
    # Read the CSV file with appropriate encoding (try 'utf-8', fallback to 'ISO-8859-1')
    try:
        df = pd.read_csv(input_file, encoding='utf-8')  # First try utf-8
    except UnicodeDecodeError:
        df = pd.read_csv(input_file, encoding='ISO-8859-1')  # Fallback to ISO-8859-1
    
    # Initialize an empty list to hold the filtered records
    valid_data = []
    
    # Iterate through each row (record)
    for index, row in df.iterrows():
        # Create a dictionary, but only include non-empty fields, and exclude 'MoSCoW'
        record = {key: value for key, value in row.items() if pd.notna(value) and key != 'MoSCoW'}
        
        # Append the validated record to the valid_data list
        valid_data.append(record)
    
    # Write the filtered data to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(valid_data, json_file, indent=4)

    print(f"Validated JSON file has been saved to {output_file}")



input_file = './ESGDataPoints_Updated.csv'
output_file = 'output.json'


csv_to_json(input_file, output_file)
