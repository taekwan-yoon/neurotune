import sys
import subprocess
import os
import time

def run_script(script_name, args=None):
    """
    Runs a Python script with optional arguments.

    Parameters:
    - script_name (str): The name of the script to run.
    - args (list or None): List of arguments to pass to the script.

    Returns:
    - None

    Raises:
    - RuntimeError: If the script execution fails.
    """
    command = ['python', script_name]
    if args:
        command.extend(args)
    
    try:
        print(f"Executing: {' '.join(command)}")
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Script {script_name} failed with exit code {e.returncode}") from e

def main():
    """
    Main function to orchestrate the CSV processing, feature extraction,
    and model inference to produce prediction JSON with timing.
    """
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file.csv>")
        sys.exit(1)
    
    input_csv = sys.argv[1]

    if not os.path.isfile(input_csv):
        print(f"Error: The input file '{input_csv}' does not exist.")
        sys.exit(1)
    
    base_name, ext = os.path.splitext(input_csv)
    if ext.lower() != '.csv':
        print("Error: The input file must be a CSV file with a '.csv' extension.")
        sys.exit(1)
    
    # Define intermediate and output file paths
    processed_csv = f"{base_name}_processed{ext}"
    features_csv = f"{processed_csv.replace('.csv', '_processed')}.csv"
    output_json = f"{features_csv.replace('.csv', '_predictions.json')}"
    
    # Define the period parameter
    period = 3.0  # You can change this value as needed

    overall_start_time = time.time()
    
    try:
        # Step 1: Process the CSV
        #print("\n--- Step 1: Processing CSV ---")
        step_start_time = time.time()
        run_script('src/model/ml/processCSV.py', [input_csv])
        step_duration = time.time() - step_start_time
        print(f"Step 1 completed in {step_duration:.2f} seconds.")
        
        if not os.path.isfile(processed_csv):
            raise FileNotFoundError(f"Processed CSV '{processed_csv}' was not created.")
        #print(f"Processed CSV saved as '{processed_csv}'.")
        
        # Step 2: Preprocess Data to Extract Features
        print("\n--- Step 2: Preprocessing Data ---")
        step_start_time = time.time()
        run_script('src/model/ml/preprocessData.py', [processed_csv, str(period)])
        step_duration = time.time() - step_start_time
        print(f"Step 2 completed in {step_duration:.2f} seconds.")
        
        if not os.path.isfile(features_csv):
            raise FileNotFoundError(f"Features CSV '{features_csv}' was not created.")
        #print(f"Features CSV saved as '{features_csv}'.")
        
        # Step 3: Model Inference to Generate Predictions
        #print("\n--- Step 3: Running Model Inference ---")
        step_start_time = time.time()
        run_script('src/model/ml/modelInference.py', [features_csv])
        step_duration = time.time() - step_start_time
        print(f"Step 3 completed in {step_duration:.2f} seconds.")
        
        if not os.path.isfile(output_json):
            raise FileNotFoundError(f"Output JSON '{output_json}' was not created.")
        print(f"Predictions JSON saved as '{output_json}'.")
        
        overall_duration = time.time() - overall_start_time
        print("\nAll steps completed successfully.")
        print(f"Total time taken: {overall_duration:.2f} seconds.")
        print(f"Final predictions are available in '{output_json}'.")
    
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
