from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import time
import threading
import subprocess
import json
import os

from eeg.eeg import EEG
from eeg.eeg_analysis import run_anlaysis
from eeg.eeg_filter import apply_bandpass_filter
from ml.main import inference

class BackendServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.stop = False
        self.is_done = False
        self.client_connected = False
        self.eeg_thread = None  # Track the EEG data thread
        # Add routes
        self.app.route("/")(self.hello_world)

        # Listen for stop_eeg event from frontend
        self.socketio.on_event('stop_eeg', self.stop_eeg_data)

        # Listen for client connection and disconnection
        self.socketio.on_event('connect', self.client_connected_event)
        self.socketio.on_event('disconnect', self.client_disconnected_event)

    # Example for sending static data to frontend
    def hello_world(self):
        return jsonify({'sample_data': 'Hello, World!'})

    # Method to stop EEG data collection
    def stop_eeg_data(self):
        self.stop = True  # Set stop flag to True to exit the loop in get_EEG_data
        self.is_done = True  # Mark the result as ready
        print("EEG collection stopped.")

    # Method to start EEG data collection when the client is connected
    def client_connected_event(self):
        self.client_connected = True  # Set client connection flag to True
        self.stop = False  # Reset stop flag in case it's been set
        print("Client connected, starting EEG data collection.")

        # Start a new EEG data collection thread if not already running
        if not self.eeg_thread or not self.eeg_thread.is_alive():
            self.eeg_thread = threading.Thread(target=self.get_EEG_data)
            self.eeg_thread.daemon = True  # Set as daemon to exit when the main program exits
            self.eeg_thread.start()

    # Method to handle client disconnection
    def client_disconnected_event(self):
        self.client_connected = False  # Reset client connection flag
        self.stop = True  # Stop EEG data collection
        print("Client disconnected, stopping EEG data collection.")

    # Method to collect EEG data and emit it via SocketIO
    def get_EEG_data(self):
        if not self.client_connected:
            print("Client not connected, not starting EEG data collection.")
            return

        eeg_object = EEG()
        eeg_object.init_params()
        eeg_object.init_board()
        eeg_object.init_stream()
        togle = True
        while not self.stop:
            data = eeg_object.start_streaming(3)  
            if(data != None):
                data = apply_bandpass_filter(data)
            # file_path = f"{"User"}_{"temp"}_{1}.csv"
            self.socketio.emit('eeg_data', data)
            self.get_output_data()
            time.sleep(0.5)

            '''
            // [{"ch1 - AF7":325.9210614385,"ch2 - AF8":422.8817076897,"ch3 - TP9":35.1251403838,"ch4 - TP10":197.6649323581,"timestamp":1731732867.2994301319},
            '''
        eeg_object.stop_board()
        final_file_path = f"{"User"}_{"final"}_{1}.csv"
        run_anlaysis(final_file_path)
        final_file_path
        if os.path.exists(final_file_path):
            os.remove(final_file_path)
        self.socketio.emit('disconnected', "done")
        
    def run(self):
        # Run the Flask server with SocketIO
        self.socketio.run(self.app, port=5000)

    def get_output_data(self):
        # make json file that contains ML output from csv file
        print("getting output data...")
        inference('input_file.csv')
        # read json file
        with open('input_file_predictions.json') as f:
            data = json.load(f)
        # emit data to frontend
        self.socketio.emit('output_data', data)
        time.sleep(0.5)
            

if __name__ == '__main__':
    backend_server = BackendServer()
    backend_server.run()
