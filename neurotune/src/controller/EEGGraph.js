import React, { useEffect, useRef } from "react";
import io from "socket.io-client";
import ReactECharts from "echarts-for-react";

const SOCKET_SERVER_URL = "http://127.0.0.1:5000/"; // Update if different

const EEGGraph = () => {
  const socketRef = useRef();
  const chartRef = useRef();

  const channelNames = ["ch1 - AF7", "ch2 - AF8", "ch3 - TP9", "ch4 - TP10"];

  // Initialize data storage
  const dataBuffer = useRef({
    timestamps: [],
    channels: channelNames.reduce((acc, channelName) => {
      acc[channelName] = [];
      return acc;
    }, {}),
  });

  // Flag to control when to update the chart
  const updatePending = useRef(false);

  useEffect(() => {
    // Establish WebSocket connection
    socketRef.current = io(SOCKET_SERVER_URL);

    socketRef.current.on("connect", () => {
      console.log("Connected to WebSocket server");
    });

    socketRef.current.on("eeg_data", (eegDataArray) => {
      // Log the received data to inspect its structure
      console.log("Received EEG Data:", eegDataArray);

      // Ensure eegDataArray is an array
      if (Array.isArray(eegDataArray)) {
        eegDataArray.forEach((dataPoint) => {
          const { timestamp } = dataPoint;
          const timeString = new Date(timestamp * 1000).toLocaleTimeString();

          dataBuffer.current.timestamps.push(timeString);

          channelNames.forEach((channelName) => {
            dataBuffer.current.channels[channelName].push(dataPoint[channelName]);
          });
        });
      } else {
        // Handle case when eegDataArray is not an array
        console.error("Expected an array but received:", eegDataArray);
        // If it's an object with a single data point, handle it here:
        if (eegDataArray.timestamp) {
          const { timestamp } = eegDataArray;
          const timeString = new Date(timestamp * 1000).toLocaleTimeString();

          dataBuffer.current.timestamps.push(timeString);

          channelNames.forEach((channelName) => {
            dataBuffer.current.channels[channelName].push(eegDataArray[channelName]);
          });
        }
      }

      // Maintain only the latest 600 data points (3 seconds at 200 Hz)
      const maxDataPoints = 600;
      if (dataBuffer.current.timestamps.length > maxDataPoints) {
        const excess = dataBuffer.current.timestamps.length - maxDataPoints;
        dataBuffer.current.timestamps.splice(0, excess);
        for (let key in dataBuffer.current.channels) {
          if (dataBuffer.current.channels.hasOwnProperty(key)) {
            dataBuffer.current.channels[key].splice(0, excess);
          }
        }
      }

      // Throttle chart updates using requestAnimationFrame
      if (!updatePending.current) {
        updatePending.current = true;
        requestAnimationFrame(() => {
          if (chartRef.current) {
            const option = {
              xAxis: {
                data: dataBuffer.current.timestamps,
              },
              series: channelNames.map((channelName) => ({
                name: channelName,
                data: dataBuffer.current.channels[channelName],
              })),
            };
            chartRef.current.getEchartsInstance().setOption(option, {
              notMerge: false,
              lazyUpdate: true,
              silent: true,
            });
          }
          updatePending.current = false;
        });
      }
    });

    socketRef.current.on("disconnect", () => {
      console.log("Disconnected from WebSocket server");
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, []);

  // Initial chart options
  const initialOption = {
    title: {
      text: "Live EEG Data Visualization",
    },
    tooltip: {
      trigger: "axis",
    },
    legend: {
      data: channelNames,
    },
    grid: {
      left: "10%",
      right: "10%",
      top: "10%",
      bottom: "20%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: dataBuffer.current.timestamps,
    },
    yAxis: {
      type: "value",
    },
    series: channelNames.map((channelName, idx) => ({
      name: channelName,
      type: "line",
      data: dataBuffer.current.channels[channelName],
      showSymbol: false,
      smooth: true,
      lineStyle: {
        width: 2,
        color: `hsl(${idx * 45}, 70%, 50%)`,
      },
      animation: false,
    })),
    animation: {
      duration: 500,
      easing: "linear",
    },
  };

  return (
    <ReactECharts
      ref={chartRef}
      option={initialOption}
      notMerge={false}
      lazyUpdate={true}
      style={{ height: "500px", width: "100%" }}
    />
  );
};

export default EEGGraph;
