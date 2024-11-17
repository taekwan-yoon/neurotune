# main.py

import os
import time
import pandas as pd
from ml.processCSV import process_csv
from ml.preprocessData import extract_features_from_df
from ml.modelInference import model_inference

def inference(input_csv):
    """
    Processes the input CSV file, extracts features, and runs model inference
    to produce a prediction JSON file without generating intermediate CSV files.
    """
    # Check if input file exists
    if not os.path.isfile(input_csv):
        print(f"Error: The input file '{input_csv}' does not exist.")
        return

    base_name, ext = os.path.splitext(input_csv)
    if ext.lower() != '.csv':
        print("Error: The input file must be a CSV file with a '.csv' extension.")
        return

    output_json = f"{base_name}_predictions.json"

    # Define the period parameter
    period = 3.0  # You can change this value as needed

    overall_start_time = time.time()

    try:
        # Step 1: Process the CSV
        print("\n--- Step 1: Processing CSV ---")
        step_start_time = time.time()
        df_processed = process_csv(input_csv)
        step_duration = time.time() - step_start_time
        print(f"Step 1 completed in {step_duration:.2f} seconds.")

        # Step 2: Preprocess Data to Extract Features
        print("\n--- Step 2: Preprocessing Data ---")
        step_start_time = time.time()
        feature_vector, feature_names = extract_features_from_df(df_processed, period)
        step_duration = time.time() - step_start_time
        print(f"Step 2 completed in {step_duration:.2f} seconds.")

        # Check if any features were extracted
        if feature_vector is None or feature_names is None:
            print("No features were extracted. Cannot proceed to inference.")
            return

        # Create a DataFrame for features
        features_df = pd.DataFrame([feature_vector], columns=feature_names)

        # Step 3: Model Inference to Generate Predictions
        print("\n--- Step 3: Running Model Inference ---")
        step_start_time = time.time()
        predictions = model_inference(features_df)
        step_duration = time.time() - step_start_time
        print(f"Step 3 completed in {step_duration:.2f} seconds.")

        # Save predictions to JSON
        predictions.to_json(output_json, orient='records', indent=4)
        print(f"Predictions saved to {output_json}")

        overall_duration = time.time() - overall_start_time
        print("\nAll steps completed successfully.")
        print(f"Total time taken: {overall_duration:.2f} seconds.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

# Example usage
if __name__ == "__main__":
    # Replace 'your_input_file.csv' with your actual input CSV file path
    inference(r'User_temp_2.csv')

