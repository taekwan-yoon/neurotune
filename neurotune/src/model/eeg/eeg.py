import time
import os
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

        # For collecting training data
        self.name = "User"
        self.number = 1
        self.flavor = "final"

        # Set the recording duration to 3 minutes (180 seconds)
        self.duration = 180
        self.col_names = ["ch1 - AF7", "ch2 - AF8", "ch3 - TP9", "ch4 - TP10", "timestamp"]

    def init_params(self, serial_port="COM6"):
        """ Initialize parameters for the board connection """
        self.params = BrainFlowInputParams()
        self.board_id = BoardIds.GANGLION_BOARD.value
        self.params.serial_port = serial_port

    def init_board(self):
        """ Initialize the board using the set parameters """
        if self.params is None:
            raise ValueError("Parameters are not initialized. Call `init_params` first.")
        
        self.board = BoardShim(self.board_id, self.params)
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)
        self.timestamp = BoardShim.get_timestamp_channel(self.board_id)
        
    def init_stream(self):
        self.board.prepare_session()
        self.board.start_stream()

    def start_streaming(self, duration):
        """ Start streaming data from the EEG board for a specified duration in seconds """
        if self.board is None:
            raise ValueError("Board is not initialized. Call `init_board` first.")
        
        all_data = []
        try:
            # Prepare and start the session
            print("Streaming started successfully.")

            start_time = time.time()

            # Loop to collect data for the specified duration
            while time.time() - start_time < duration:
                # Wait until there are at least 200 data points available (about 1 second of data)
                while self.board.get_board_data_count() < 50:
                    time.sleep(0.005)

                data = self.board.get_board_data()  # Retrieve data

                # Process and store data
                eegdf = pd.DataFrame(np.transpose(data[self.eeg_channels]))
                timedf = pd.DataFrame(np.transpose(data[self.timestamp]))

                newdata = pd.concat([eegdf, timedf], axis=1)
                all_data.append(newdata)

            # Concatenate all collected data once
            if all_data:
                result_df = pd.concat(all_data, ignore_index=True)
                result_df.columns = self.col_names
                self.save_to_csv(result_df)
                return result_df.to_json(orient='records')
            else:
                print("No data collected during the session.")
                return None

        except BrainFlowError as e:
            print(f"BrainFlow error occurred: {e}")


    def save_to_csv(self, data_frame):
        """ Save the collected data to CSV """
        temp_file = f"input_file.csv"
        data_frame.to_csv(temp_file, index=True)

        final_file = f"{self.name}_{self.flavor}_{self.number}.csv"
        file_exists = os.path.isfile(final_file)
        data_frame.to_csv(final_file, mode='a', header=not file_exists, index=True)
        print(f"Data saved to {final_file}.")

    def stop_board(self):
        """ Stop streaming and release resources """
        try:
            if self.board is not None:
                self.board.stop_stream()
                self.board.release_session()
                print("Streaming stopped successfully.")
        except BrainFlowError as e:
            print(f"Error while stopping or releasing the session: {e}")

if __name__ == "__main__":
    eeg = EEG()
    eeg.init_params(serial_port="COM6")  # Initialize parameters
    eeg.init_board()  # Initialize the board
    eeg.start_streaming(duration=3)  # Start EEG streaming for 3 seconds
