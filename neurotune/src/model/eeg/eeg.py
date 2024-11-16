import time
import numpy as np
import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.exit_codes import BrainFlowError

class EEG:
    def __init__(self):
        self.params = None
        self.board_id = None
        self.board = None
        self.eeg_channels = None
        self.timestamp = None

        # for collecting training data
        self.name = "Sarah" # Sarah, Taekwan, ...
        self.number = 1 # 1, 2, 3, ...
        self.flavor = "good" # good / neutral / bad

        # Set the recording duration to 3 minutes (180 seconds)
        self.duration = 180

        self.col_names = ["ch1 - AF7", "ch2 - AF8", "ch3 - TP9", "ch4 - TP10", "timestamp"]

    def init_params(self):
        # Initialize parameters for the board connection
        self.params = BrainFlowInputParams()
        self.board_id = BoardIds.GANGLION_BOARD.value
        self.params.serial_port = "COM6" # IMPORTANT: Change this to the correct port for your device
    
    def init_board(self):
        # Initialize the board
        self.board = BoardShim(self.board_id, self.params)
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)
        self.timestamp = BoardShim.get_timestamp_channel(self.board_id)
    def get_final_result(self):
        pass
    def collect_training_data(self):
        self.init_params()
        self.init_board()

        try:
            # Prepare and start the session
            self.board.prepare_session()
            self.board.start_stream()

            # Print confirmation that streaming has started
            print("Streaming started successfully.")

            all_data = []
            start_time = time.time()

            # Loop to collect data for the specified duration
            while time.time() - start_time < self.duration:
                # Wait until there are at least 200 data points available (about 1 second of data)
                while self.board.get_board_data_count() < 200:
                    time.sleep(0.005)
                
                data = self.board.get_board_data(200) # Retrieve data

                print(time.time())
                eegdf = pd.DataFrame(np.transpose(data[self.eeg_channels]))
                timedf = pd.DataFrame(np.transpose(data[self.timestamp]))

                newdata = pd.concat([eegdf, timedf], axis=1)
                all_data.append(newdata)
            
            result_df = pd.concat(all_data, ignore_index=True)
            result_df.columns = self.col_names

            result_df.to_csv(f"{self.name}_{self.flavor}_{self.number}.csv", index=True)
        
        except BrainFlowError as e:
            print(f"BrainFlow error occurred: {e}")
        
        finally:
            # Ensure that the board stops streaming and releases resources
            self.board.stop_stream()
            print("Streaming stopped successfully.")
    
    def start_eeg(self, duration):
    
        all_data = []
        try:
            # Prepare and start the session
            self.board.prepare_session()
            self.board.start_stream()

            # Print confirmation that streaming has started
            print("Streaming started successfully.")
            start_time = time.time()

            # Loop to collect data for the specified duration
            while time.time() - start_time < duration:
                # Wait until there are at least 200 data points available (about 1 second of data)
                while self.board.get_board_data_count() < 200:
                    time.sleep(0.005)
                
                data = self.board.get_board_data(200)  # Retrieve data

                print(time.time())
                eegdf = pd.DataFrame(np.transpose(data[self.eeg_channels]))
                timedf = pd.DataFrame(np.transpose(data[self.timestamp]))

                newdata = pd.concat([eegdf, timedf], axis=1)
                all_data.append(newdata)
                print(all_data)
            
            # Concatenate all collected data once
            if all_data:
                result_df = pd.concat(all_data, ignore_index=True)
                result_df.columns = self.col_names
        
                # Save to CSV
                result_df.to_csv(f"{self.name}_{self.flavor}_{self.number}.csv", index=True)

            else:
                print("No data collected during the session.")
                return None  # Return if no data was collected
            
        except BrainFlowError as e:
            print(f"BrainFlow error occurred: {e}")
        
        finally:
            # Ensure that the board stops streaming and releases resources safely
            try:
                if self.board.is_prepared():
                    self.board.stop_stream()
                    self.board.release_session()
                    print("Streaming stopped successfully.")
            except BrainFlowError as e:
                print(f"Error while stopping or releasing the session: {e}")

        # Ensure columns are unique and convert to JSON
        print(all_data)
        if all_data:
            all_data_df = pd.concat(all_data, ignore_index=True)
            
            if all_data_df.columns.duplicated().any():
                print("Duplicate columns detected: ", all_data_df.columns[all_data_df.columns.duplicated()])
            all_data_df = all_data_df.loc[:, ~all_data_df.columns.duplicated()]

            all_data_json = all_data_df.to_json(orient='records')
            return all_data_json
        else:
            print("No data collected to convert to JSON.")
            return None


if __name__ == "__main__":
    
    eeg = EEG()
    # if we want to collect training data
    # else, comment this out

    eeg.collect_training_data()

    # if we want to start the EEG stream
    # else, comment this out

    # eeg.start_eeg()