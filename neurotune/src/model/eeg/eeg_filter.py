import json
import numpy as np
from scipy import signal

def apply_bandpass_filter(data, sampling_rate=250, lowcut=0.5, highcut=40.0, order=4):
    """
    Apply bandpass filter to EEG data in JSON format
    
    Parameters:
    data (str or list): JSON string or List of dictionaries containing EEG data
        Format: [{"ch1 - AF7": float, "ch2 - AF8": float, "ch3 - TP9": float, 
                 "ch4 - TP10": float, "timestamp": float}, ...]
    sampling_rate (float): Sampling rate in Hz, default 200 Hz
    lowcut (float): Lower frequency bound in Hz, default 0.5 Hz
    highcut (float): Upper frequency bound in Hz, default 40 Hz
    order (int): Filter order, default 4
    
    Returns:
    dict: Dictionary containing filtered data for each channel and timestamps
    """
    # If data is a JSON string, parse it
    if isinstance(data, str):
        data = json.loads(data)
    
    # Extract channel names (excluding timestamp)
    channel_names = [key for key in data[0].keys() if key != "timestamp"]
    
    # Extract timestamps
    timestamps = np.array([sample["timestamp"] for sample in data])
    
    # Create dictionary to store filtered data
    filtered_data = {
        "timestamps": timestamps.tolist()
    }
    
    # Calculate Nyquist frequency
    nyquist = sampling_rate / 2.0
    
    # Normalize frequencies
    low = lowcut / nyquist
    high = highcut / nyquist
    
    # Create Butterworth bandpass filter coefficients
    b, a = signal.butter(order, [low, high], btype='band')
    
    # Process each channel
    for channel in channel_names:
        # Extract raw channel data
        raw_channel = np.array([sample[channel] for sample in data])
        
        # Apply zero-phase bandpass filter
        filtered_channel = signal.filtfilt(b, a, raw_channel)
        
        # Store filtered data
        filtered_data[channel] = filtered_channel.tolist()
    
    # Convert to list of dictionaries format if needed
    filtered_json = []
    for i in range(len(timestamps)):
        sample_dict = {"timestamp": timestamps[i]}
        for channel in channel_names:
            sample_dict[channel] = filtered_data[channel][i]
        filtered_json.append(sample_dict)
    
    return filtered_json

# Example usage:
if __name__ == "__main__":
    # Example JSON data
    json_data = '[{"ch1 - AF7": 0.1, "ch2 - AF8": 0.2, "ch3 - TP9": 0.3, "ch4 - TP10": 0.4, "timestamp": 1.0}, {"ch1 - AF7": 0.2, "ch2 - AF8": 0.3, "ch3 - TP9": 0.4, "ch4 - TP10": 0.5, "timestamp": 2.0}]'
    
    # Apply filter
