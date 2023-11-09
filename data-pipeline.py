# Solution code
# SQL

# SELECT * FROM grocery_sales

# Python
import pandas as pd
import numpy as np
import logging
import os

# Create the extract() function with two parameters: one for the store data and the other one for the extra data
# Read the extra data from the parquet file and merge the DataFrames using "index" column
def extract(store_data, extra_data):
    extra_df = pd.read_parquet(extra_data)
    merged_df = store_data.merge(extra_df, on = "index")
    return merged_df
  
# Call the extract() function and store it as the "merged_df" variable
merged_df = extract(store_df, "extra_data.parquet")
# Use isnull() to check for null values in each column
null_columns = merged_df.columns[merged_df.isnull().any()]

# Now, 'null_columns' contains the names of columns with null values
print("Columns with null values:")
print(null_columns)

# Create the transform() function with one parameter: "raw_data"
def transform(raw_data):
  # Fill NaNs using mean since we are dealing with numeric columns
  # Set inplace = True to do the replacing on the current DataFrame
    raw_data.fillna(
      {
          'CPI': raw_data['CPI'].mean(),
          'Weekly_Sales': raw_data['Weekly_Sales'].mean(),
          'Unemployment': raw_data['Unemployment'].mean(),
      }, inplace = True
    )
    # Define the type of the "Date" column and its format
    raw_data["Date"] = pd.to_datetime(raw_data["Date"], format = "%Y-%m-%d")
    # Extract the month value from the "Date" column to calculate monthly sales later on
    raw_data["Month"] = raw_data["Date"].dt.month

    # Filter the entire DataFrame using the "Weekly_Sales" column. Use .loc to access a group of rows
    raw_data = raw_data.loc[raw_data["Weekly_Sales"] > 10000, :]
    
    # Drop unnecessary columns. Set axis = 1 to specify that the columns should be removed
    raw_data = raw_data.drop(["index", "Temperature", "Fuel_Price", "MarkDown1", "MarkDown2", "MarkDown3", "MarkDown4", "MarkDown5", "Type", "Size", "Date"], axis = 1)
    return raw_data

# Call the transform() function and pass the merged DataFrame
clean_data = transform(merged_df)

# Create the avg_monthly_sales function that takes in the cleaned data from the last step
def avg_monthly_sales(clean_data):
  	# Select the "Month" and "Weekly_Sales" columns as they are the only ones needed for this analysis
    holidays_sales = clean_data[["Month", "Weekly_Sales"]]
   	# Create a chain operation with groupby(), agg(), reset_index(), and round() functions
    # Group by the "Month" column and calculate the average monthly sales
    # Call reset_index() to start a new index order
    # Round the results to two decimal places
    
    holidays_sales = (holidays_sales.groupby("Month")
    .agg(Avg_Sales = ("Weekly_Sales", "mean"))
    .reset_index().round(2))
    return holidays_sales

# Call the avg_monthly_sales() function and pass the cleaned DataFrame
agg_data = avg_monthly_sales(clean_data)

# Create the load() function that takes in the cleaned DataFrame and the aggregated one with the paths where they are going to be stored
def load(full_data, full_data_file_path, agg_data, agg_data_file_path):
  	# Save both DataFrames as csv files. Set index = False to drop the index columns
    full_data.to_csv(full_data_file_path, index = False)
    agg_data.to_csv(agg_data_file_path, index = False)

# Call the load() function and pass the cleaned and aggregated DataFrames with their paths    
load(clean_data, "clean_data.csv", agg_data, "agg_data.csv")

# Create the validation() function with one parameter: file_path - to check whether the previous function was correctly executed
def validation(file_path):
  	# Use the "os" package to check whether a path exists
    file_exists = os.path.exists(file_path)
    # Raise an exception if the path doesn't exist, hence, if there is no file found on a given path
    if not file_exists:
        raise Exception(f"There is no file at the path {file_path}")

# Call the validation() function and pass first, the cleaned DataFrame path, and then the aggregated DataFrame path
validation("clean_data.csv")
validation("agg_data.csv")
