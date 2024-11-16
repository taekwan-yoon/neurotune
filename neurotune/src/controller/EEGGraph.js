import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";
import ReactECharts from "echarts-for-react";

const SOCKET_SERVER_URL = "http://127.0.0.1:5000/";

const EEGGraph = () => {
  const socketRef = useRef();
  const [echartsInstance, setEchartsInstance] = useState(null);

  const channelNames = ["ch1 - AF7", "ch2 - AF8", "ch3 - TP9", "ch4 - TP10"];

  const dataBuffer = useRef({
    timestamp: [],
    channels: channelNames.reduce((acc, channelName) => {
      acc[channelName] = [];
      return acc;
    }, {}),
  });

  const updatePending = useRef(false);

  useEffect(() => {
    socketRef.current = io(SOCKET_SERVER_URL);

    socketRef.current.on("connect", () => {
      console.log("Connected to WebSocket server");
    });

    socketRef.current.on("eeg_data", (eegDataArray) => {
      console.log("Received EEG Data:", eegDataArray);

      if (Array.isArray(eegDataArray)) {
        eegDataArray.forEach((dataPoint) => {
          // Ensure timestamp and other properties exist before processing
          if (dataPoint && dataPoint.timestamp) {
            const { timestamp } = dataPoint;
            const timeString = new Date(timestamp * 1000).toLocaleTimeString();

            dataBuffer.current.timestamp.push(timeString);

            channelNames.forEach((channelName) => {
              if (dataPoint.hasOwnProperty(channelName)) {
                dataBuffer.current.channels[channelName].push(
                  dataPoint[channelName]
                );
              }
            });
          } else {
            console.error("Data point is missing timestamp:", dataPoint);
          }
        });
      } else {
        console.error("Expected an array but received:", eegDataArray);

        if (eegDataArray && eegDataArray.timestamp) {
          const { timestamp } = eegDataArray;
          const timeString = new Date(timestamp * 1000).toLocaleTimeString();

          dataBuffer.current.timestamp.push(timeString);

          channelNames.forEach((channelName) => {
            if (eegDataArray.hasOwnProperty(channelName)) {
              dataBuffer.current.channels[channelName].push(
                eegDataArray[channelName]
              );
            }
          });
        } else {
          console.error(
            "Received data is missing timestamp or is invalid:",
            eegDataArray
          );
        }
      }

      const maxDataPoints = 400;
      if (dataBuffer.current.timestamp.length > maxDataPoints) {
        const excess = dataBuffer.current.timestamp.length - maxDataPoints;
        dataBuffer.current.timestamp.splice(0, excess);
        for (let key in dataBuffer.current.channels) {
          if (dataBuffer.current.channels.hasOwnProperty(key)) {
            dataBuffer.current.channels[key].splice(0, excess);
          }
        }
      }

      if (!updatePending.current) {
        updatePending.current = true;
        requestAnimationFrame(() => {
          if (echartsInstance) {
            const option = {
              xAxis: {
                data: dataBuffer.current.timestamp,
              },
              series: channelNames.map((channelName) => ({
                name: channelName,
                data: dataBuffer.current.channels[channelName],
              })),
            };
            echartsInstance.setOption(option, {
              notMerge: false,
              lazyUpdate: true,
              silent: true,
            });
          } else {
            console.log("echartsInstance is null");
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
  }, []); // Dependency array corrected

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
      data: dataBuffer.current.timestamp,
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
    animation: false, // Corrected animation property
    animationDuration: 500,
    animationEasing: "linear",
  };

  return (
    <ReactECharts
      option={initialOption}
      notMerge={false}
      lazyUpdate={true}
      style={{ height: "500px", width: "100%" }}
      onChartReady={(instance) => {
        console.log("Chart is ready, instance:", instance);
        setEchartsInstance(instance);
      }}
    />
  );
};

export default EEGGraph;