import pandas as pd
import sys
import os

def process_csv(file_path):
    """
    Processes the CSV file by:
    1. Deleting the first column.
    2. Rounding the 'timestamp' column to seven decimal places.
    3. Grouping rows with duplicate rounded 'timestamp' values.
    4. Calculating the mean for numerical columns.

    Parameters:
    - file_path (str): The path to the input CSV file.

    Returns:
    - None
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        print(f"Successfully loaded '{file_path}'.")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{file_path}' is empty.")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"Error: The file '{file_path}' does not appear to be in CSV format.")
        sys.exit(1)

    # Display original columns
    #print(f"Original columns: {df.columns.tolist()}")

    # Check if there are at least two columns to delete the first one
    if df.shape[1] < 2:
        print("Error: The CSV file does not have enough columns to delete the first one.")
        sys.exit(1)

    # Delete the first column (assuming it's unnamed or unnecessary)
    first_col = df.columns[0]
    df = df.drop(columns=[first_col]).copy()
    #print(f"First column '{first_col}' has been deleted.")
   # print(f"Remaining columns: {df.columns.tolist()}")

    # Check if 'timestamp' column exists after deletion
    if 'timestamp' not in df.columns:
        print("Error: The CSV file does not contain a 'timestamp' column after deleting the first column.")
        sys.exit(1)

    # Ensure 'timestamp' is treated as float
    try:
        df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
        if df['timestamp'].isnull().any():
            num_nulls = df['timestamp'].isnull().sum()
            print(f"Warning: {num_nulls} 'timestamp' entries could not be converted to numeric and will be dropped.")
            df = df.dropna(subset=['timestamp'])
        print("'timestamp' column successfully converted to numeric.")
    except Exception as e:
        print(f"Error: Unable to convert 'timestamp' to numeric. {e}")
        sys.exit(1)

    # Round 'timestamp' to seven decimal places
    df['timestamp'] = df['timestamp'].round(7)
    #print("'timestamp' column has been rounded to seven decimal places.")

    # Identify numerical columns (excluding 'timestamp')
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    if 'timestamp' in numerical_cols:
        numerical_cols.remove('timestamp')
        print("'timestamp' column removed from numerical columns.")

    #print(f"Numerical columns to be averaged: {numerical_cols}")

    if not numerical_cols:
        print("Warning: No numerical columns found to calculate means.")

    # Group by 'timestamp' and calculate mean for numerical columns
    try:
        df_processed = df.groupby('timestamp')[numerical_cols].mean().reset_index()
        print("Grouping and mean calculation successful.")
    except Exception as e:
        print(f"Error during grouping and mean calculation: {e}")
        sys.exit(1)

    # Define the output file name
    base, ext = os.path.splitext(file_path)
    output_file = f"{base}_processed{ext}"

    try:
        # Save the processed DataFrame to a new CSV file with specified float format
        df_processed.to_csv(output_file, index=False, float_format='%.7f')
        print(f"Processed data has been saved to '{output_file}'.")
    except Exception as e:
        print(f"Error: Could not write to '{output_file}'. {e}")
        sys.exit(1)

def main():
    """
    Main function to handle command-line arguments and initiate CSV processing.
    """
    if len(sys.argv) != 2:
        print("Usage: python model.py <input_file.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    process_csv(input_file)

if __name__ == "__main__":
    main()
