# processCSV.py

import pandas as pd
import sys

def process_csv(input_file):
    """
    Processes the CSV file by:
    1. Deleting the first column.
    2. Rounding the 'timestamp' column to seven decimal places.
    3. Grouping rows with duplicate rounded 'timestamp' values.
    4. Calculating the mean for numerical columns.

    Returns:
    - df_processed (pd.DataFrame): The processed DataFrame.
    """
    try:
        df = pd.read_csv(input_file)
        print(f"Successfully loaded '{input_file}'.")
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' does not exist.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{input_file}' is empty.")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"Error: The file '{input_file}' does not appear to be in CSV format.")
        sys.exit(1)

    # Delete the first column (assuming it's unnamed or unnecessary)
    first_col = df.columns[0]
    df = df.drop(columns=[first_col]).copy()

    # Check if 'timestamp' column exists after deletion
    if 'timestamp' not in df.columns:
        print("Error: The CSV file does not contain a 'timestamp' column after deleting the first column.")
        sys.exit(1)

    # Ensure 'timestamp' is treated as float
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    if df['timestamp'].isnull().any():
        num_nulls = df['timestamp'].isnull().sum()
        print(f"Warning: {num_nulls} 'timestamp' entries could not be converted to numeric and will be dropped.")
        df = df.dropna(subset=['timestamp'])
    print("'timestamp' column successfully converted to numeric.")

    # Round 'timestamp' to seven decimal places
    df['timestamp'] = df['timestamp'].round(7)

    # Identify numerical columns (excluding 'timestamp')
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    if 'timestamp' in numerical_cols:
        numerical_cols.remove('timestamp')
        print("'timestamp' column removed from numerical columns.")

    if not numerical_cols:
        print("Warning: No numerical columns found to calculate means.")

    # Group by 'timestamp' and calculate mean for numerical columns
    try:
        df_processed = df.groupby('timestamp')[numerical_cols].mean().reset_index()
        print("Grouping and mean calculation successful.")
    except Exception as e:
        print(f"Error during grouping and mean calculation: {e}")
        sys.exit(1)

    return df_processed
