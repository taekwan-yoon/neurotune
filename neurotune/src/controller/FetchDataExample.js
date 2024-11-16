import React, { useEffect, useState, useRef } from "react";
import { io } from "socket.io-client";
import StartRecordingButton from "./StartRecordingButton";
import StopRecordingButton from "./StopRecordingButton";

function FetchDataExample() {
  const [sampleData, setSampleData] = useState(null);
  const [EEG_data, setEEG] = useState(null);
  const [timeData2, setTimeData2] = useState(null);

  const socketRef = useRef(null); // Use useRef to store the socket

  // Function to start the EEG recording (connect to the socket)
  function startEEG() {
    if (!socketRef.current) {
      // Initialize the socket connection
      socketRef.current = io("http://127.0.0.1:5000");

      // Fetch sample static JSON data on connection
      fetch("http://127.0.0.1:5000/")
        .then((response) => response.json())
        .then((data) => setSampleData(data.sample_data))
        .catch((error) => console.error("Error fetching sample data: ", error));

      // Listen for incoming EEG data
      socketRef.current.on("eeg_data", (msg) => {
        console.log("Received data:", msg);
        setEEG(msg);
      });
    }
  }

  // Function to stop the EEG recording (disconnect the socket)
  function stopEEG() {
    if (socketRef.current) {
      socketRef.current.emit("stop_eeg");
      socketRef.current.disconnect();
      socketRef.current = null; // Reset the ref to null to allow reconnection
    }
  }

  return (
    <div>
      <h1>NeuroTune</h1>

      <p>{EEG_data ? EEG_data : "Loading..."}</p>
      <StartRecordingButton startEEG={startEEG} />
      <StopRecordingButton stopEEG={stopEEG} />
    </div>
  );
}

export default FetchDataExample;
