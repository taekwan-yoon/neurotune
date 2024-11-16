import time
import numpy as np
import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.exit_codes import BrainFlowError

def init():
    # Initialize parameters for the board connection
    params = BrainFlowInputParams()
    board_id = BoardIds.GANGLION_BOARD.value  
    params.serial_port = "COM6"              

    # Initialize the board
    board = BoardShim(board_id, params)
    eeg_channels = BoardShim.get_eeg_channels(board_id)
    timestamp = BoardShim.get_timestamp_channel(board_id)
    
    name = "Sarah" # Sarah, Taekwan, ...
    number = 0 # 1, 2, 3, ...
    flavor = "test" # good / neutral / bad

    try:
        # Prepare and start the session
        board.prepare_session()
        board.start_stream()
        
        # Print confirmation that streaming has started
        print("Streaming started successfully.")
        
        # Set the recording duration to 3 minutes (180 seconds)
        duration = 10
        start_time = time.time()
        all_data = []

        # Loop to collect data for the specified duration
        while time.time() - start_time < duration:
            # Wait until there are at least 250 data points available (about 1 second of data)
            while board.get_board_data_count() < 200:
                time.sleep(0.005)
            data = board.get_board_data()  # Retrieve data
            print (time.time())
            eegdf = pd.DataFrame(np.transpose(data[eeg_channels]))
            timedf = pd.DataFrame(np.transpose(data[timestamp]))
        
            newdata = pd.concat([eegdf,timedf], axis = 1)
            all_data.append(newdata)

        result_df = pd.concat(all_data, ignore_index=True)    
        col_names = ["ch1 - AF7", "ch2 - AF8", "ch3 - TP9", "ch4 - TP10", "timestamp"]
        result_df.columns = col_names 

        result_df.to_csv(f"{name}_{flavor}_{number}.csv", index=True)

    except BrainFlowError as e:
        print(f"BrainFlow error occurred: {e}")
        
    finally:
        # Ensure that the board stops streaming and releases resources
        board.stop_stream()
        board.release_session()
        print("Session ended.")

if __name__ == "__main__":
    init()