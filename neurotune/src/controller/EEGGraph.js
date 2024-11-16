import React, { useEffect, useRef } from "react";
import io from "socket.io-client";
import ReactECharts from "echarts-for-react";

const SOCKET_SERVER_URL = "http://127.0.0.1:5000/";

const EEGGraph = () => {
  const socketRef = useRef();
  const chartRef = useRef();

  const channelNames = ["ch1 - AF7", "ch2 - AF8", "ch3 - TP9", "ch4 - TP10"];

  // Initialize data storage
  const dataBuffer = useRef({
    channels: {
      "ch1 - AF7": [],
      "ch2 - AF8": [],
      "ch3 - TP9": [],
      "ch4 - TP10": [],
    },
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
      eegDataArray.forEach((entry) => {
        const timestampMs = entry.timestamp * 1000;

        // Append channel data with timestamp
        channelNames.forEach((channel) => {
          dataBuffer.current.channels[channel].push([
            timestampMs,
            entry[channel],
          ]);
        });
      });

      // Maintain only the latest 600 data points (3 seconds at 200 Hz)
      const maxDataPoints = 600;
      channelNames.forEach((channel) => {
        if (dataBuffer.current.channels[channel].length > maxDataPoints) {
          const excess =
            dataBuffer.current.channels[channel].length - maxDataPoints;
          dataBuffer.current.channels[channel].splice(0, excess);
        }
      });

      // Throttle chart updates using requestAnimationFrame
      if (!updatePending.current) {
        updatePending.current = true;
        requestAnimationFrame(() => {
          if (chartRef.current) {
            const option = {
              series: channelNames.map((channel) => ({
                name: channel,
                data: dataBuffer.current.channels[channel],
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
      type: "time",
      boundaryGap: false,
    },
    yAxis: {
      type: "value",
    },
    series: channelNames.map((channel, idx) => ({
      name: channel,
      type: "line",
      data: dataBuffer.current.channels[channel],
      showSymbol: false,
      smooth: true,
      lineStyle: {
        width: 2,
        color: `hsl(${idx * 45}, 70%, 50%)`,
      },
      animation: false, // Disable per-series animation
    })),
    animation: {
      duration: 500, // Duration of the initial animation
      easing: "linear",
    },
  };

  return (
    <ReactECharts
      ref={chartRef}
      option={initialOption}
      notMerge={false} // Enable merging to allow smooth updates
      lazyUpdate={true}
      style={{ height: "500px", width: "100%" }}
    />
  );
};

export default EEGGraph;
