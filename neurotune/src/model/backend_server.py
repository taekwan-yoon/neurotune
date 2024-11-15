from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import time
import threading

class BackendServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # add paths for static data
        self.app.route("/")(self.hello_world)
    
    # example for sending static data to frontend
    def hello_world(self):
        return jsonify({'sample_data': 'Hello, World!'})
    
    # example for sending dynamic data to frontend
    def send_time_data1(self):
        while True:
            self.socketio.emit('time_data1', {'message': 'Hello from Flask at: ' + str(time.time())})
            time.sleep(1)
    
    # example for sending dynamic data to frontend
    def send_time_data2(self):
        while True:
            self.socketio.emit('time_data2', {'message': 'Hello from Flask at: ' + str(time.time())})
            time.sleep(5)

    def run(self):
        # example for threading multiple data streams
        # define functions for threading
        thread1 = threading.Thread(target=self.send_time_data1)
        thread2 = threading.Thread(target=self.send_time_data2)

        # set threads as daemon
        thread1.daemon = True
        thread2.daemon = True

        # start threads
        thread1.start()
        thread2.start()

        # run server
        self.socketio.run(self.app, port=5000)

if __name__ == '__main__':
    backend_server = BackendServer()
    backend_server.run()