# modelInference.py

import numpy as np
import pandas as pd
import os
import json
import joblib
import sys
import xgboost as xgb

def model_inference(features_df):
    """
    Runs model inference on the extracted features DataFrame and returns predictions.

    Parameters:
    - features_df (pd.DataFrame): DataFrame containing extracted features.

    Returns:
    - predictions (pd.DataFrame): DataFrame containing predictions and probabilities.
    """
    # Load scaler and model
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scaler_path = os.path.join(script_dir, 'scaler.save')
    model_path = os.path.join(script_dir, 'best_xgb_model.json')

    try:
        scaler = load_scaler(scaler_path)
    except Exception as e:
        print(f"Failed to load scaler: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        model = load_trained_model(model_path)
    except Exception as e:
        print(f"Failed to load model: {e}", file=sys.stderr)
        sys.exit(1)

    # Preprocess data
    feature_columns = features_df.columns.tolist()
    X = features_df[feature_columns].values

    # Scale features
    X_scaled = scaler.transform(X)

    # Make predictions
    try:
        predicted_indices, probabilities = make_predictions(model, X_scaled)
    except Exception as e:
        print(f"Prediction failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Map numerical predictions to label names
    predicted_labels = map_predictions(predicted_indices)

    # Prepare predictions DataFrame
    label_names = ['bad', 'neutral', 'good']
    prob_df = pd.DataFrame(probabilities, columns=label_names)
    predictions = pd.DataFrame({
        "index": features_df.index,
        "prediction": predicted_labels
    })
    predictions = pd.concat([predictions, prob_df], axis=1)

    return predictions

# Include all necessary helper functions

def load_scaler(scaler_path):
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler file not found at {scaler_path}")
    scaler = joblib.load(scaler_path)
    return scaler

def load_trained_model(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    try:
        model = xgb.XGBClassifier()
        model.load_model(model_path)
    except Exception as e:
        raise RuntimeError(f"Error loading model: {e}")
    return model

def make_predictions(model, X):
    # Predict probabilities
    probabilities = model.predict_proba(X)
    # Get predicted class indices
    predicted_indices = np.argmax(probabilities, axis=1)
    return predicted_indices, probabilities

def map_predictions(predicted_indices):
    label_mapping = {0: 'bad', 1: 'neutral', 2: 'good'}
    predicted_labels = [label_mapping.get(idx, "unknown") for idx in predicted_indices]
    return predicted_labels
