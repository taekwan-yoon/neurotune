import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mne.time_frequency import tfr_multitaper



#Take CSV as input
def input_csv(dataframe):
    # Create a new data frame for a CSV file
    
    # Clean CSV accordingly 
    dataframe =  dataframe.drop(dataframe.columns[[0,5]], axis=1)


    # Specify the channels to keep
    ch_names = ['AF7', 'AF8', 'TP9', 'TP10']
    ch_types = ['eeg'] * 4

    # Measured in Hz
    sampling_freq = 200
    # Create info
    info = mne.create_info(ch_names=ch_names, ch_types=ch_types, sfreq=sampling_freq)

    dataframe = dataframe.transpose()

    raw = mne.io.RawArray(dataframe,info,verbose=True)

    # Display information on the raw file
    print(raw)
    print(raw.info)

    return raw

def process_raw(raw):

    ch_names = ['AF7', 'AF8', 'TP9', 'TP10']

    # Create a custom montage based on the channels 
    montage_org = mne.channels.make_standard_montage('standard_1020')
    channel_index = []
    for (index, channel) in enumerate(montage_org.ch_names):
        if channel in ch_names:
            channel_index.append(index)

    montage_proc = montage_org.copy()

    # Assign index and corresponding channel label
    dig_to_keep = []
    channels_to_keep = []
    for index in channel_index:
        channels_to_keep.append(montage_org.ch_names[index])
        dig_to_keep.append(montage_org.dig[index+3])

    montage_proc.ch_names = channels_to_keep

    # Include the 3 fiducials
    montage_proc.dig = montage_org.dig[0:3] + dig_to_keep

    # Set montage 
    raw = raw.set_montage(montage_proc)

    return raw

# 1st Visualization: Time-Frequency Analysis on EEG data
def time_frequency(raw, min, max, max_time):

    # Adding features to view the TFR for entire timeline or partial 
    # Adding features to view the TFR for entire frequency range or partial

    # Apply filter to select the common frequency bands
    raw.filter(0.1,99,fir_design='firwin')
    
    freqs = np.logspace(np.log10(min), np.log10(max), 10)

    n_cycles = freqs / 2  # Number of cycles for each frequency

    # Compute TFR using multitaper
    tfr = tfr_multitaper(raw, freqs=freqs, n_cycles=n_cycles, time_bandwidth=3.0, return_itc=False)

    # Plot the TFR
    # Specify the time range to view
    tmin = float(0)
    tmax = 20
    tfr_show = tfr.copy().crop(tmin=tmin, tmax=tmax)

    # Make sure to change the baseline mode to stay consistent with the time range
    tfr_fig = tfr_show.plot([0], baseline=(-0.5, tmin+0.1), mode= 'logratio', title= "Time-Frequency Representation (TFR)", show=False)
    tfr_fig[0].savefig("tfr_fig.png")
    plt.close(tfr_fig[0])

# 2nd Visualization: Average Power Spectral Density for EEG data
def average_psd(raw, min, max):

    # Adding features to view the average PSD for entire frequency range or partial
    freq_bands = {
        'Delta': (1, 4),       # Delta: 1-4 Hz
        'Theta': (4, 8),       # Theta: 4-8 Hz
        'Alpha': (8, 13),      # Alpha: 8-13 Hz
        'Beta': (13, 30),      # Beta: 13-30 Hz
        'Gamma': (30, 100)      # Gamma: 30-100 Hz
    }

    # Color code each frequency band 
    freq_colors = {
        'Delta': 'blue',
        'Theta': 'green',
        'Alpha': 'yellow',
        'Beta': 'red',
        'Gamma': 'purple'
    }

    if (min==0.1 and max==99):
        raw.compute_psd(n_fft=2048, picks='eeg', average='mean')
        avgpsd_fig = raw.compute_psd().plot(picks='eeg', average=True, show=False)

        ax = avgpsd_fig.axes[0]

        for band, (fmin, fmax) in freq_bands.items():
            band_color = freq_colors[band]
            ax.axvspan(fmin, fmax, color=band_color, alpha=0.3, label=band)

        ax.legend(loc='upper right')

        avgpsd_fig.savefig("avgpsd.png")
        plt.close(avgpsd_fig)
    
    else:
        raw.compute_psd(fmin=min, fmax=max, n_fft=2048, picks='eeg', average='mean')
        avgpsd_fig = raw.compute_psd(fmin=min, fmax=max).plot(picks='eeg', average=True, show=False)

        ax = avgpsd_fig.axes[0]

        for band, (fmin, fmax) in freq_bands.items():
            band_color = freq_colors[band]
            ax.axvspan(fmin, fmax, color=band_color, alpha=0.3, label=band)

        ax.legend(loc='upper right')

        avgpsd_fig.savefig("avgpsd.png")
        plt.close(avgpsd_fig)

# 3rd Visualization: Delta, Theta, Alpha, Beta, Gamma in Time-Frequency Analysis
def freq_bands(raw, max_time):

    freq_bands = {
        'Delta': np.arange(1, 5, 1),    # Delta (1-4 Hz)
        'Theta': np.arange(4, 9, 1),    # Theta (4-8 Hz)
        'Alpha': np.arange(8, 14, 1),   # Alpha (8-13 Hz)
        'Beta': np.arange(13, 31, 1),   # Beta (13-30 Hz)
        'Gamma': np.arange(30, 101,1)   # Gamma: 30-100 Hz
    }

    # Specify the time range to view
    tmin = 0
    tmax = 20

    print("max: " ,  max_time)
    # The number of cycles will vary depending on which frequency band to use 
    n_cycles = {'Delta': 4, 'Theta': 6, 'Alpha': 8, 'Beta': 10, 'Gamma': 12}

    fig, axes = plt.subplots(len(freq_bands), 1, figsize=(10, 15))

    for ax, (band, freqs) in zip(axes, freq_bands.items()):

        # Computing TFR for each frequency band range
        tfr = tfr_multitaper(raw, freqs=freqs, n_cycles=n_cycles[band], time_bandwidth=3.0, return_itc=False)
        tfr_show = tfr.copy().crop(tmin=tmin, tmax=tmax)

        # Plot the TFR
        # Make sure to change the baseline mode to stay consistent with the time range
        freqtfr_fig = tfr_show.plot([0], baseline=(-0.5, tmin+0.1), mode= 'logratio', title= "", axes= ax, show=False)

        ax.set_title(f"{band} Frequency Band")
    
    plt.tight_layout()

    freqtfr_fig[0].savefig("analysis.png")
    plt.close(freqtfr_fig[0])
    

def run_anlaysis(csv):
    # Bring CSV as input
    dataframe = pd.read_csv(csv)
    max_time = dataframe['timestamp'].iloc[-1] - dataframe['timestamp'].iloc[0]
    raw = input_csv(dataframe)
    
    # Process the raw file accordingly for MNE
    raw = process_raw(raw)

    fmin = float(0.1)
    fmax = float(99)

    # First visualization
    time_frequency(raw, fmin, fmax, max_time)

    # Second visualization
    average_psd(raw, fmin, fmax)

    # Third visualization
    freq_bands(raw,max_time)

if __name__ == "__main__":
    run_anlaysis("hello")