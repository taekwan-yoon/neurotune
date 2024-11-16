import numpy as np
import pandas as pd
import scipy
import scipy.signal
import scipy.fft
import scipy.stats
import scipy.linalg  # For logm function
import warnings
import matplotlib.pyplot as plt
import sys
import os

def matrix_from_csv_file(file_path):
    """
    Returns the data matrix given the path of a CSV file.

    Parameters:
        file_path (str): Path to the CSV file with signal data.

    Returns:
        numpy.ndarray: 2D matrix containing the data read from the CSV
    """
    # Read the CSV file using pandas to handle headers and non-numeric data
    df = pd.read_csv(file_path)

    # Ensure all required columns are present
    columns_to_check = ['ch1 - AF7', 'ch2 - AF8', 'ch3 - TP9', 'ch4 - TP10']
    missing_columns = [col for col in columns_to_check if col not in df.columns]
    if missing_columns:
        raise ValueError(f"The following required columns are missing from the CSV: {missing_columns}")

    original_row_count = len(df)
    # Remove rows where all specified channels are zero
    df = df[~(df[columns_to_check] == 0).all(axis=1)]
    filtered_row_count = len(df)
    #print(f"Removed {original_row_count - filtered_row_count} rows where all specified channels are zero.")

    # Extract variances for debugging
    variances = df[columns_to_check].var()
    #print("Signal variances after filtering:", variances.to_dict())

    # Reset timestamps to start from zero and increment accordingly
    sampling_rate = 100  # 100 Hz
    df['timestamp'] = np.arange(len(df)) / sampling_rate

    # Extract the timestamp and signal data
    # Assuming 'timestamp' is the time column and signals are 'ch1 - AF7', 'ch2 - AF8', 'ch3 - TP9', 'ch4 - TP10'
    time_column = df['timestamp'].values
    signal_columns = ['ch1 - AF7', 'ch2 - AF8', 'ch3 - TP9', 'ch4 - TP10']
    signal_data = df[signal_columns].values

    # Combine time and signal data
    full_matrix = np.column_stack((time_column, signal_data))

    return full_matrix

def feature_mean(matrix):
    ret = np.mean(matrix, axis=0).flatten()
    names = ['mean_' + str(i+1) for i in range(matrix.shape[1])]
    return ret, names

def feature_mean_d(matrix):
    # Difference between second half and first half
    half = matrix.shape[0] // 2
    h1, h2 = matrix[:half, :], matrix[half:, :]
    ret = (feature_mean(h2)[0] - feature_mean(h1)[0]).flatten()
    names = ['mean_d_h2h1_' + str(i+1) for i in range(h1.shape[1])]
    return ret, names

def feature_mean_q(matrix):
    # Split into four quarters
    quarter = matrix.shape[0] // 4
    if quarter == 0:
        # Handle cases with very few samples
        q1 = q2 = q3 = q4 = matrix
    else:
        q1, q2, q3, q4 = np.split(matrix, [quarter, 2*quarter, 3*quarter])
    v1 = feature_mean(q1)[0]
    v2 = feature_mean(q2)[0]
    v3 = feature_mean(q3)[0]
    v4 = feature_mean(q4)[0]
    ret = np.hstack([
        v1, v2, v3, v4,
        v1 - v2, v1 - v3, v1 - v4,
        v2 - v3, v2 - v4, v3 - v4
    ]).flatten()

    names = []
    for i in range(4):  # for all quarter-windows
        names.extend(['mean_q' + str(i + 1) + "_" + str(j+1) for j in range(len(v1))])

    for i in range(3):  # for quarter-windows 1-3
        for j in range((i + 1), 4):  # and quarter-windows (i+1)-4
            names.extend(['mean_d_q' + str(i + 1) + 'q' + str(j + 1) + "_" + str(k+1)
                          for k in range(len(v1))])

    return ret, names

def feature_stddev(matrix):
    ret = np.std(matrix, axis=0, ddof=1).flatten()
    names = ['std_' + str(i+1) for i in range(matrix.shape[1])]
    return ret, names

def feature_stddev_d(matrix):
    # Difference between second half and first half
    half = matrix.shape[0] // 2
    h1, h2 = matrix[:half, :], matrix[half:, :]
    ret = (feature_stddev(h2)[0] - feature_stddev(h1)[0]).flatten()
    names = ['std_d_h2h1_' + str(i+1) for i in range(h1.shape[1])]
    return ret, names

def feature_moments(matrix, epsilon=1e-6):
    """
    Computes the 3rd and 4th standardized moments about the mean (i.e., skewness
    and kurtosis) of each signal, for the full time window.
    """
    stddev = np.std(matrix, axis=0, ddof=1)
    low_variance = stddev < epsilon

    skw = np.zeros(matrix.shape[1])
    krt = np.zeros(matrix.shape[1])

    if not np.all(low_variance):
        skw_non_low = scipy.stats.skew(matrix[:, ~low_variance], axis=0, bias=False)
        krt_non_low = scipy.stats.kurtosis(matrix[:, ~low_variance], axis=0, bias=False)
        skw[~low_variance] = skw_non_low
        krt[~low_variance] = krt_non_low

    ret = np.append(skw, krt)

    names = ['skew_' + str(i+1) for i in range(matrix.shape[1])]
    names.extend(['kurt_' + str(i+1) for i in range(matrix.shape[1])])
    return ret, names

def feature_max(matrix):
    ret = np.max(matrix, axis=0).flatten()
    names = ['max_' + str(i+1) for i in range(matrix.shape[1])]
    return ret, names

def feature_max_d(matrix):
    # Difference between second half and first half
    half = matrix.shape[0] // 2
    h1, h2 = matrix[:half, :], matrix[half:, :]
    ret = (feature_max(h2)[0] - feature_max(h1)[0]).flatten()
    names = ['max_d_h2h1_' + str(i+1) for i in range(h1.shape[1])]
    return ret, names

def feature_max_q(matrix):
    # Split into four quarters
    quarter = matrix.shape[0] // 4
    if quarter == 0:
        # Handle cases with very few samples
        q1 = q2 = q3 = q4 = matrix
    else:
        q1, q2, q3, q4 = np.split(matrix, [quarter, 2*quarter, 3*quarter])
    v1 = feature_max(q1)[0]
    v2 = feature_max(q2)[0]
    v3 = feature_max(q3)[0]
    v4 = feature_max(q4)[0]
    ret = np.hstack([
        v1, v2, v3, v4,
        v1 - v2, v1 - v3, v1 - v4,
        v2 - v3, v2 - v4, v3 - v4
    ]).flatten()

    names = []
    for i in range(4):  # for all quarter-windows
        names.extend(['max_q' + str(i + 1) + "_" + str(j+1) for j in range(len(v1))])

    for i in range(3):  # for quarter-windows 1-3
        for j in range((i + 1), 4):  # and quarter-windows (i+1)-4
            names.extend(['max_d_q' + str(i + 1) + 'q' + str(j + 1) + "_" + str(k+1)
                          for k in range(len(v1))])

    return ret, names

def feature_min(matrix):
    ret = np.min(matrix, axis=0).flatten()
    names = ['min_' + str(i+1) for i in range(matrix.shape[1])]
    return ret, names

def feature_min_d(matrix):
    # Difference between second half and first half
    half = matrix.shape[0] // 2
    h1, h2 = matrix[:half, :], matrix[half:, :]
    ret = (feature_min(h2)[0] - feature_min(h1)[0]).flatten()
    names = ['min_d_h2h1_' + str(i+1) for i in range(h1.shape[1])]
    return ret, names

def feature_min_q(matrix):
    # Split into four quarters
    quarter = matrix.shape[0] // 4
    if quarter == 0:
        # Handle cases with very few samples
        q1 = q2 = q3 = q4 = matrix
    else:
        q1, q2, q3, q4 = np.split(matrix, [quarter, 2*quarter, 3*quarter])
    v1 = feature_min(q1)[0]
    v2 = feature_min(q2)[0]
    v3 = feature_min(q3)[0]
    v4 = feature_min(q4)[0]
    ret = np.hstack([
        v1, v2, v3, v4,
        v1 - v2, v1 - v3, v1 - v4,
        v2 - v3, v2 - v4, v3 - v4
    ]).flatten()

    names = []
    for i in range(4):  # for all quarter-windows
        names.extend(['min_q' + str(i + 1) + "_" + str(j+1) for j in range(len(v1))])

    for i in range(3):  # for quarter-windows 1-3
        for j in range((i + 1), 4):  # and quarter-windows (i+1)-4
            names.extend(['min_d_q' + str(i + 1) + 'q' + str(j + 1) + "_" + str(k+1)
                          for k in range(len(v1))])

    return ret, names

def feature_covariance_matrix(matrix):
    covM = np.cov(matrix.T)
    indx = np.triu_indices(covM.shape[0])
    ret = covM[indx]

    names = []
    for i in range(covM.shape[0]):
        for j in range(i, covM.shape[1]):
            names.append(f'covM_{i+1}_{j+1}')

    return ret, names, covM

def feature_eigenvalues(covM):
    ret = np.linalg.eigvals(covM).flatten()
    names = [f'eigenval_{i+1}' for i in range(covM.shape[0])]
    return ret, names

def feature_logcov(covM, epsilon=1e-6):
    """
    Computes the matrix logarithm of the covariance matrix of the signals,
    with regularization to handle singular matrices.

    Parameters:
        covM (numpy.ndarray): Covariance matrix.
        epsilon (float): Regularization parameter.

    Returns:
        numpy.ndarray: Flattened upper triangular part of the log covariance matrix.
        list: Feature names for log covariance matrix elements.
        numpy.ndarray: Regularized covariance matrix.
    """
    # Regularize the covariance matrix by adding epsilon to the diagonal
    covM_reg = covM + epsilon * np.eye(covM.shape[0])

    try:
        log_cov = scipy.linalg.logm(covM_reg)
        log_cov = log_cov.real  # Discard negligible imaginary parts
        indx = np.triu_indices(log_cov.shape[0])
        ret = log_cov[indx]

        names = []
        for i in range(log_cov.shape[0]):
            for j in range(i, log_cov.shape[1]):
                names.append(f'logcovM_{i+1}_{j+1}')

        return ret, names, covM_reg
    except Exception as e:
        print(f"Error computing logm: {e}")
        # Return zeros or another default value if logm fails
        ret = np.zeros(len(np.triu_indices(covM.shape[0])[0]))
        names = [f'logcovM_{i+1}_{j+1}' for i in range(covM.shape[0]) for j in range(i, covM.shape[1])]
        return ret, names, covM_reg

def feature_fft(matrix, period=2.0, mains_f=50.,
               filter_mains=True, filter_DC=True,
               normalise_signals=True,
               ntop=10, get_power_spectrum=True):
    """
    Computes the FFT of each signal.

    Parameters:
        matrix (numpy.ndarray): Signal matrix (samples x channels).
        period (float): Duration of the window in seconds.
        mains_f (float): Mains frequency to filter out (e.g., 50 Hz).
        filter_mains (bool): Whether to remove mains frequency components.
        filter_DC (bool): Whether to remove the DC component.
        normalise_signals (bool): Whether to normalize signals to [-1, 1].
        ntop (int): Number of top frequencies to extract.
        get_power_spectrum (bool): Whether to include the full power spectrum.

    Returns:
        numpy.ndarray: Feature array.
        list: Feature names.
    """
    # Signal properties
    N = matrix.shape[0]  # number of samples
    if N == 0:
        return np.array([]), []
    T = period / N        # Sampling period

    # Scale all signals to interval [-1, 1] (if requested)
    if normalise_signals:
        # Avoid division by zero by adding a small epsilon
        matrix_min = np.min(matrix, axis=0)
        matrix_ptp = np.ptp(matrix, axis=0) + 1e-8
        matrix = -1 + 2 * (matrix - matrix_min) / matrix_ptp

    # Compute the (absolute values of the) FFT
    fft_values = np.abs(scipy.fft.fft(matrix, axis=0))[0:N//2] * 2 / N

    # Compute the corresponding frequencies of the FFT components
    freqs = np.linspace(0.0, 1.0 / (2.0 * T), N//2)

    # Remove DC component (if requested)
    if filter_DC:
        fft_values = fft_values[1:]
        freqs = freqs[1:]

    # Remove mains frequency component(s) (if requested)
    if filter_mains:
        indx = np.where(np.abs(freqs - mains_f) <= 1)
        fft_values = np.delete(fft_values, indx, axis=0)
        freqs = np.delete(freqs, indx)

    # Extract top N frequencies for each signal
    available_freqs = fft_values.shape[0]
    if available_freqs < ntop:
        ntop = available_freqs
        warnings.warn(f"ntop ({ntop}) is greater than available frequencies after filtering. Adjusting ntop to {ntop}.")

    if ntop > 0:
        # Argsort in descending order
        indx = np.argsort(fft_values, axis=0)[::-1]
        top_freq_indices = indx[:ntop, :]

        top_freqs = freqs[top_freq_indices]
        ret = top_freqs.flatten(order='F')

        # Make feature names
        names = []
        for i in range(fft_values.shape[1]):
            for j in range(ntop):
                names.append(f'topFreq_{j+1}_{i+1}')

        if get_power_spectrum:
            ret = np.hstack([ret, fft_values.flatten(order='F')])

            for i in range(fft_values.shape[1]):
                for j, freq in enumerate(freqs):
                    freq_rounded = round(freq, 2)  # Use two decimal places for frequency
                    names.append(f'freq_{freq_rounded:.2f}_{i+1}')
    else:
        ret = np.array([])
        names = []

    return ret, names

def calc_feature_vector(matrix):
    """
    Calculates all previously defined features and concatenates everything into
    a single feature vector.

    Parameters:
        matrix (numpy.ndarray): Resampled signal matrix (samples x channels).

    Returns:
        numpy.ndarray: Feature vector.
        list: Feature names.
    """
    var_names = []
    var_values = np.array([])

    # Feature extraction steps
    features = [
        (feature_mean, [matrix]),
        (feature_mean_d, [matrix]),
        (feature_mean_q, [matrix]),
        (feature_stddev, [matrix]),
        (feature_stddev_d, [matrix]),
        (feature_moments, [matrix]),
        (feature_max, [matrix]),
        (feature_max_d, [matrix]),
        (feature_max_q, [matrix]),
        (feature_min, [matrix]),
        (feature_min_d, [matrix]),
        (feature_min_q, [matrix]),
        (feature_covariance_matrix, [matrix]),
    ]

    # Calculate features up to covariance matrix
    covM = None  # Initialize covM
    for func, args in features:
        result = func(*args)
        if func == feature_covariance_matrix:
            x, v, covM = result
        else:
            x, v = result
        var_names += v
        var_values = np.hstack([var_values, x])

    if covM is None:
        raise ValueError("Covariance matrix was not computed.")

    # Continue with features that depend on covariance matrix
    eigenvals, eigen_names = feature_eigenvalues(covM)
    var_names += eigen_names
    var_values = np.hstack([var_values, eigenvals])

    logcov, logcov_names, _ = feature_logcov(covM)
    var_names += logcov_names
    var_values = np.hstack([var_values, logcov])

    # FFT features
    fft_vals, fft_names = feature_fft(matrix)
    var_names += fft_names
    var_values = np.hstack([var_values, fft_vals])

    return var_values, var_names

def extract_features_from_csv(file_path, nsamples=100, period=2.0,
                              remove_redundant=True,
                              cols_to_ignore=None):
    """
    Reads data from a CSV file and extracts statistical features for the entire time window.

    Parameters:
        file_path (str): Path to the CSV file.
        nsamples (int): Number of samples for resampling.
        period (float): Duration of the time window in seconds.
        remove_redundant (bool): Whether to remove redundant features.
        cols_to_ignore (list or None): List of column indices to ignore.

    Returns:
        numpy.ndarray: Feature vector (1 x num_features).
        list: Feature names.
    """
    # Read the matrix from file
    full_matrix = matrix_from_csv_file(file_path)
    #print(f"Total samples after filtering: {full_matrix.shape[0]}")

    # Check duration
    if full_matrix.shape[0] == 0:
        print("Empty matrix after filtering. Skipping feature extraction.")
        return np.array([]), []

    duration = full_matrix[-1, 0] - full_matrix[0, 0]
    #print(f"Window duration: {duration:.6f} seconds.")
    if duration < 0.9 * period:
        print(f"Duration {duration:.6f} is less than 90% of period {period}. Processing with available data.")

    # Perform the resampling of the vector
    try:
        ry, rx = scipy.signal.resample(full_matrix[:, 1:], num=nsamples, t=full_matrix[:, 0], axis=0)
    except Exception as e:
        print(f"Resampling failed: {e}")
        return np.array([]), []

    # Compute the feature vector
    if ry.size == 0:
        print("Resampling resulted in empty data. Skipping this window.")
        return np.array([]), []

    r, headers = calc_feature_vector(ry)
    if r.size == 0:
        print("Feature vector is empty. Skipping this window.")
        return np.array([]), []

    feature_vector = r
    feature_names = headers

    # Remove redundant features if specified
    if remove_redundant and feature_names:
        # Define prefixes of features to remove
        to_rm = ["mean_q3_", "mean_q4_", "mean_d_q3q4_",
                 "max_q3_", "max_q4_", "max_d_q3q4_",
                 "min_q3_", "min_q4_", "min_d_q3q4_"]

        # Identify indices to remove
        indices_to_remove = []
        for rm_prefix in to_rm:
            for i, name in enumerate(feature_names):
                if name.startswith(rm_prefix):
                    indices_to_remove.append(i)

        # Remove duplicates and sort
        indices_to_remove = sorted(list(set(indices_to_remove)))

        # Remove from feature names and feature vector
        if indices_to_remove:
            feature_vector = np.delete(feature_vector, indices_to_remove)
            feature_names = [name for i, name in enumerate(feature_names) if i not in indices_to_remove]
            print(f"Removed {len(indices_to_remove)} redundant features.")

    # Reshape feature_vector to 2D array (1 x num_features)
    feature_vector = feature_vector.reshape(1, -1)

    #print(f"Feature extraction complete. Extracted {feature_vector.shape[1]} features.")

    return feature_vector, feature_names

def main():
    if len(sys.argv) != 2:
        print("Usage: python preprocessData.py <path_to_input_csv>")
        sys.exit(1)

    input_file_path = sys.argv[1]

    if not os.path.isfile(input_file_path):
        print(f"Error: File '{input_file_path}' does not exist.")
        sys.exit(1)

    # Define parameters
    nsamples = 100       # Number of samples for resampling
    period = 2.0         # 2-second time window
    remove_redundant = True
    cols_to_ignore = None  # List of column indices to ignore, if any

    # Extract features from the CSV
    features, feature_names = extract_features_from_csv(
        input_file_path, nsamples=nsamples, period=period,
        remove_redundant=remove_redundant, cols_to_ignore=cols_to_ignore)

    if features.size == 0:
        print("No features were extracted. Please check the input data and parameters.")
        sys.exit(1)
    else:
        # Convert features to DataFrame
        df_features = pd.DataFrame(features, columns=feature_names)

        # Determine output file path
        input_dir, input_filename = os.path.split(input_file_path)
        input_basename, _ = os.path.splitext(input_filename)
        output_filename = f"{input_basename}_processed.csv"
        output_features_path = os.path.join(input_dir, output_filename)

        # Save the features to a single CSV file
        df_features.to_csv(output_features_path, index=False)

        #print("Feature extraction complete. Features saved to:", output_features_path)

if __name__ == "__main__":
    main()
