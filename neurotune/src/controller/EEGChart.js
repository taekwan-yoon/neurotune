// src/EegChart.js
import React, { useEffect, useRef } from "react";
import io from "socket.io-client";
import ReactECharts from "echarts-for-react";

const SOCKET_SERVER_URL = "http://127.0.0.1:5000/"; // Update if different

const EegChart = () => {
  const socketRef = useRef();
  const chartRef = useRef();

  // Initialize data storage
  const dataBuffer = useRef({
    timestamps: [],
    channels: {
      a: [],
      b: [],
      c: [],
      d: [],
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

    socketRef.current.on("eeg_data", (eegData) => {
      const { timestamp, values } = eegData;

      const baseTimestamp = timestamp; // Unix timestamp in seconds
      const interval = 1 / 200; // 0.005 seconds between data points

      for (let i = 0; i < 200; i++) {
        const pointTime = baseTimestamp + i * interval;
        const timeString = new Date(pointTime * 1000).toLocaleTimeString();

        // Append timestamps and channel data
        dataBuffer.current.timestamps.push(timeString);
        dataBuffer.current.channels.a.push(values.a[i]);
        dataBuffer.current.channels.b.push(values.b[i]);
        dataBuffer.current.channels.c.push(values.c[i]);
        dataBuffer.current.channels.d.push(values.d[i]);
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
              series: Object.keys(dataBuffer.current.channels).map(
                (channel, idx) => ({
                  name: `Channel ${String.fromCharCode(
                    97 + idx
                  ).toUpperCase()}`,
                  data: dataBuffer.current.channels[channel],
                })
              ),
            };
            chartRef.current.getEchartsInstance().setOption(option, {
              notMerge: false, // Enable merging to allow smooth animations
              lazyUpdate: true,
              silent: true, // Prevent triggering events during updates
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
      data: ["Channel A", "Channel B", "Channel C", "Channel D"],
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
    series: [
      {
        name: "Channel A",
        type: "line",
        data: dataBuffer.current.channels.a,
        showSymbol: false,
        smooth: true,
        lineStyle: {
          width: 2,
          color: "hsl(0, 70%, 50%)",
        },
        animation: false, // Disable per-series animation
      },
      {
        name: "Channel B",
        type: "line",
        data: dataBuffer.current.channels.b,
        showSymbol: false,
        smooth: true,
        lineStyle: {
          width: 2,
          color: "hsl(45, 70%, 50%)",
        },
        animation: false,
      },
      {
        name: "Channel C",
        type: "line",
        data: dataBuffer.current.channels.c,
        showSymbol: false,
        smooth: true,
        lineStyle: {
          width: 2,
          color: "hsl(90, 70%, 50%)",
        },
        animation: false,
      },
      {
        name: "Channel D",
        type: "line",
        data: dataBuffer.current.channels.d,
        showSymbol: false,
        smooth: true,
        lineStyle: {
          width: 2,
          color: "hsl(135, 70%, 50%)",
        },
        animation: false,
      },
    ],
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

export default EegChart;
