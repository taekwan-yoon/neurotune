import numpy as np
import pandas as pd
import os
import json
import joblib
import argparse
import sys
from tensorflow.keras.models import load_model

def load_scaler(scaler_path):
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler file not found at {scaler_path}")
    scaler = joblib.load(scaler_path)
    #print(f"Scaler loaded from {scaler_path}")
    return scaler

def load_trained_model(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    try:
        model = load_model(model_path, compile=False)
        #print(f"Model loaded from {model_path}")
    except Exception as e:
        raise RuntimeError(f"Error loading model: {e}")
    return model

def preprocess_data(input_csv, scaler, feature_columns):
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV file not found at {input_csv}")
    
    data = pd.read_csv(input_csv)
    #print(f"Input data shape: {data.shape}")
    
    # Check if feature columns exist in the input data
    missing_features = [col for col in feature_columns if col not in data.columns]
    if missing_features:
        raise ValueError(f"The following required feature columns are missing in the input data: {missing_features}")
    
    # Select feature columns
    X = data[feature_columns].values
    
    # Scale features
    X_scaled = scaler.transform(X)
    #print("Data scaling completed.")
    
    # Reshape for CNN: (samples, timesteps, channels)
    X_scaled = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))
    #print(f"Data reshaped for CNN: {X_scaled.shape}")
    
    return X_scaled, data.index.tolist()

def make_predictions(model, X):
    # Predict probabilities
    probabilities = model.predict(X)
    #print("Probabilities predicted.")
    
    # Get predicted class indices
    predicted_indices = np.argmax(probabilities, axis=1)
    #print("Predicted class indices obtained.")
    
    return predicted_indices, probabilities

def map_predictions(predicted_indices):
    label_mapping = {0: 'bad', 1: 'neutral', 2: 'good'}
    predicted_labels = [label_mapping.get(idx, "unknown") for idx in predicted_indices]
    #print("Predicted labels mapped.")
    return predicted_labels

def save_predictions_to_json(output_path, indices, predicted_labels, probabilities):
    label_names = ['bad', 'neutral', 'good']
    predictions = []
    
    for idx, label, probs in zip(indices, predicted_labels, probabilities):
        prob_dict = {label_names[i]: float(probs[i]) for i in range(len(label_names))}
        prediction_entry = {
            "index": idx,
            "prediction": label,
            "probabilities": prob_dict
        }
        predictions.append(prediction_entry)
    
    with open(output_path, 'w') as f:
        json.dump(predictions, f, indent=4)
    
    #print(f"Predictions saved to {output_path}")

def parse_arguments(script_dir):
    parser = argparse.ArgumentParser(description="Run model inference on a CSV file.")
    parser.add_argument("input_csv", type=str, help="Path to the input CSV file for inference.")
    
    # Set default paths relative to the script's directory
    default_scaler = os.path.join(script_dir, 'scaler.save')
    default_model = os.path.join(script_dir, 'best_cnn_model_2sec.keras')
    
    parser.add_argument("--scaler", type=str, default=default_scaler,
                        help=f"Path to the scaler file (default: {default_scaler}).")
    parser.add_argument("--model", type=str, default=default_model,
                        help=f"Path to the trained model file (default: {default_model}).")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to save the output JSON file. Defaults to input CSV name with '_predictions.json' suffix.")
    return parser.parse_args()

def main():
    # Determine the directory where the script resides
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    args = parse_arguments(script_dir)
    
    scaler_path = args.scaler
    model_path = args.model
    input_csv = args.input_csv
    output_json = args.output if args.output else os.path.splitext(input_csv)[0] + '_predictions.json'
    
    #print("Starting model inference...")
    
    # Load scaler and model
    #print("Loading scaler...")
    try:
        scaler = load_scaler(scaler_path)
    except Exception as e:
        print(f"Failed to load scaler: {e}", file=sys.stderr)
        sys.exit(1)
    
    #print("Loading trained CNN model...")
    try:
        model = load_trained_model(model_path)
    except Exception as e:
        print(f"Failed to load model: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Define feature columns as per training
    #print("Determining feature columns...")
    try:
        data_sample = pd.read_csv(input_csv, nrows=0)
        if 'label' in data_sample.columns:
            feature_columns = [col for col in data_sample.columns if col != 'label']
        else:
            feature_columns = list(data_sample.columns)
        #print(f"Feature columns used for inference: {feature_columns}")
    except Exception as e:
        print(f"Failed to determine feature columns: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Preprocess data
    #print("Preprocessing input data...")
    try:
        X_scaled, indices = preprocess_data(input_csv, scaler, feature_columns)
    except Exception as e:
        print(f"Data preprocessing failed: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Make predictions
    #print("Making predictions...")
    try:
        predicted_indices, probabilities = make_predictions(model, X_scaled)
    except Exception as e:
        print(f"Prediction failed: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Map numerical predictions to label names
    #print("Mapping predictions to labels...")
    predicted_labels = map_predictions(predicted_indices)
    
    # Save predictions to JSON
    #print("Saving predictions to JSON...")
    try:
        save_predictions_to_json(output_json, indices, predicted_labels, probabilities)
    except Exception as e:
        print(f"Failed to save predictions: {e}", file=sys.stderr)
        sys.exit(1)
    
    #print("Inference completed successfully.")

if __name__ == "__main__":
    main()
