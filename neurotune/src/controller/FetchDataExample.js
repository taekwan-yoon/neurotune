import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";

function FetchDataExample() {
  const [sampleData, setSampleData] = useState(null);
  const [timeData1, setTimeData1] = useState(null);
  const [timeData2, setTimeData2] = useState(null);

  // Fetch sample data from the server
  useEffect(() => {
    // Fetch sample static json data
    fetch("http://127.0.0.1:5000/")
      .then((response) => response.json())
      .then((data) => setSampleData(data.sample_data))
      .catch((error) => console.error("Error fetching sample data: ", error));

    // Fetch dynamic data from the server
    const socket = io("http://127.0.0.1:5000");

    // Listen for incoming data1
    socket.on("time_data1", (msg) => {
      console.log("Received data:", msg);
      setTimeData1(msg.message);
    });

    // Listen for incoming data2
    socket.on("time_data2", (msg) => {
      console.log("Received data:", msg);
      setTimeData2(msg.message);
    });

    return () => socket.disconnect();
  }, []);

  return (
    <div>
      <h1>NeuroTune</h1>
      <p>{sampleData ? sampleData : "Loading..."}</p>
      <p>{timeData1 ? timeData1 : "Loading..."}</p>
      <p>{timeData2 ? timeData2 : "Loading..."}</p>
    </div>
  );
}
export default FetchDataExample;
