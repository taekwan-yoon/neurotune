# backend.py
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import time
import threading
import random  # Correct module for random data generation

class BackendServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Add routes
        self.app.route("/")(self.hello_world)

    # Static route for testing
    def hello_world(self):
        return jsonify({'sample_data': 'Hello, World!'})

    # Emit time_data1 every second
    def send_time_data1(self):
        while True:
            message = {'message': f'Hello from Flask at: {time.time()}'}
            self.socketio.emit('time_data1', message)
            time.sleep(1)

    # Emit time_data2 every 5 seconds
    def send_time_data2(self):
        while True:
            message = {'message': f'Hello from Flask at: {time.time()}'}
            self.socketio.emit('time_data2', message)
            time.sleep(5)

    # Emit fake EEG data every second
    def send_fake_eeg_data(self):
        while True:
            eeg_data = {
                'timestamp': time.time(),
                'values': {
                    'a': [random.uniform(-100, 100) for _ in range(200)],
                    'b': [random.uniform(-100, 100) for _ in range(200)],
                    'c': [random.uniform(-100, 100) for _ in range(200)],
                    'd': [random.uniform(-100, 100) for _ in range(200)]
                }
            }

            self.socketio.emit("eeg_data", eeg_data)
            time.sleep(2)

    def run(self):
        # Create threads for emitting data
        thread_time1 = threading.Thread(target=self.send_time_data1)
        thread_time2 = threading.Thread(target=self.send_time_data2)
        thread_eeg = threading.Thread(target=self.send_fake_eeg_data)

        # Set threads as daemon so they exit when the main thread does
        thread_time1.daemon = True
        thread_time2.daemon = True
        thread_eeg.daemon = True

        # Start threads
        thread_time1.start()
        thread_time2.start()
        thread_eeg.start()

        # Run the SocketIO server
        self.socketio.run(self.app, port=5000)

if __name__ == '__main__':
    backend_server = BackendServer()
    backend_server.run()