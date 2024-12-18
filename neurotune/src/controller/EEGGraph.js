import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";
import ReactECharts from "echarts-for-react";
import EmotionBars from "./StyleOutput";
import ImageSlider from "../view/ImageSlider"; // Import ImageSlider
import "./EEGGraph.css";

const SOCKET_SERVER_URL = "http://127.0.0.1:5000/";

const EEGGraph = () => {
  const [output, setOutput] = useState([]);
  const [isSaved, setisSaved] = useState(false);
  const socketRef = useRef();
  const [echartsInstance, setEchartsInstance] = useState(null);
  const [EEG_data, setEEGData] = useState(null); // To store incoming EEG data
  const [isModalOpen, setIsModalOpen] = useState(false); // Modal state
  const [ratio, setRatio] = useState({
    good: 0,
    neutral: 0,
    bad: 0,
  });

  const channelNames = ["ch1 - AF7", "ch2 - AF8", "ch3 - TP9", "ch4 - TP10"];

  const pieOption = {
    title: {
      text: "Emotion Ratio",
      left: "center",
    },
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b}: {c} ({d}%)",
    },
    legend: {
      orient: "vertical",
      left: "left",
    },
    series: [
      {
        name: "Emotions",
        type: "pie",
        radius: "50%",
        label: {
          formatter: "{b}: {d}%", // Display name and percentage
        },
        data: [
          {
            value: ratio.good || 0,
            name: "Liked",
            itemStyle: { color: "green" },
          },
          {
            value: ratio.neutral || 0,
            name: "Neutral",
            itemStyle: { color: "orange" },
          },
          {
            value: ratio.bad || 0,
            name: "Not Liked",
            itemStyle: { color: "red" },
          },
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.5)",
          },
        },
      },
    ],
  };

  const dataBuffer = useRef({
    timestamp: [],
    channels: channelNames.reduce((acc, channelName) => {
      acc[channelName] = [];
      return acc;
    }, {}),
  });

  const updatePending = useRef(false);

  // Function to start EEG recording (connect to the socket)
  const startEEG = () => {
    if (!socketRef.current) {
      socketRef.current = io(SOCKET_SERVER_URL);

      // Fetch initial static data (if necessary)
      fetch("http://127.0.0.1:5000/")
        .then((response) => response.json())
        .then((data) => {
          console.log("Sample data fetched:", data);
        })
        .catch((error) => console.error("Error fetching sample data: ", error));

      socketRef.current.on("connect", () => {
        console.log("Connected to WebSocket server");
      });

      socketRef.current.on("eeg_data", (msg) => {
        console.log("Received EEG Data:", msg);
        setEEGData(msg); // Store received EEG data
        processEEGData(msg); // Process the EEG data for chart update
      });

      socketRef.current.on("output_data", (result) => {
        setOutput(result);

        const prediction = result[0].prediction;
        if (prediction) {
          switch (prediction) {
            case "good":
              setRatio((prevData) => ({
                ...prevData,
                good: prevData.good + 1,
              }));
              break;
            case "neutral":
              setRatio((prevData) => ({
                ...prevData,
                neutral: prevData.neutral + 1,
              }));
              break;
            case "bad":
              setRatio((prevData) => ({
                ...prevData,
                bad: prevData.bad + 1,
              }));
              break;
            default:
              break;
          }
        }
      });

      socketRef.current.on("disconnect", () => {
        console.log("Disconnected from WebSocket server");
        setTimeout(() => {
          setIsModalOpen(true);
          if (!isSaved) {
            setisSaved(true);
          }
        }, 3000);
      });
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  // Function to stop EEG recording (disconnect the socket)
  const stopEEG = () => {
    if (socketRef.current) {
      socketRef.current.emit("stop_eeg");
      socketRef.current.disconnect();
      socketRef.current = null; // Reset the ref to null
    }
  };

  // Function to process EEG data for updating the chart
  const processEEGData = (eegDataArray) => {
    // Ensure eegDataArray is parsed if it's a string
    if (typeof eegDataArray === "string") {
      try {
        eegDataArray = JSON.parse(eegDataArray);
      } catch (error) {
        console.error("Failed to parse EEG data JSON:", error);
        return;
      }
    }

    if (Array.isArray(eegDataArray)) {
      eegDataArray.forEach((dataPoint) => {
        if (dataPoint && dataPoint.timestamp) {
          const timestamp = dataPoint.timestamp;
          const timeString = new Date(timestamp * 1000).toLocaleTimeString();

          dataBuffer.current.timestamp.push(timeString);

          channelNames.forEach((channelName) => {
            if (dataPoint.hasOwnProperty(channelName)) {
              dataBuffer.current.channels[channelName].push(
                dataPoint[channelName]
              );
            } else {
              console.warn(`Data point is missing channel ${channelName}`);
            }
          });
        } else {
          console.error("Data point is missing timestamp:", dataPoint);
        }
      });
    }

    const maxDataPoints = 2000;
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
            series: channelNames.map((channelName, idx) => ({
              name: channelName,
              type: "line",
              data: dataBuffer.current.channels[channelName],
              showSymbol: false,
              smooth: true,
              lineStyle: {
                width: 2,
                color: `hsl(${idx * 90}, 70%, 50%)`,
              },
              animation: false,
            })),
          };
          echartsInstance.setOption(option, {
            notMerge: false,
            lazyUpdate: true,
            silent: true,
          });
        }
        updatePending.current = false;
      });
    }
  };

  const initialOption = {
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
        color: `hsl(${idx * 90}, 70%, 50%)`,
      },
      animation: false,
    })),
    animation: false,
    animationDuration: 500,
    animationEasing: "linear",
  };

  return (
    <div>
      {/* Modal for Image Slider */}
      {isSaved && (
        <button
          className="show-image-button"
          onClick={() => setIsModalOpen(true)}
        >
          View Analysis
        </button>
      )}
      {isModalOpen && <ImageSlider closeModal={closeModal} />}{" "}
      {/* Show ImageSlider when modal is open */}
      <div className="eeg-graph-container">
        <div className="button-group">
          <button className="mac-button" onClick={startEEG}>
            Start Recording
          </button>
          <button className="mac-button" onClick={stopEEG}>
            Stop Recording
          </button>
        </div>
        {/* EEG Graph */}
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
        {/* Container for EmotionBars and Pie Chart */}
        <div className="emotion-charts-container">
          <div className="emotion-bars">
            <EmotionBars msg={output} />
          </div>
          <div className="pie-chart">
            <ReactECharts
              option={pieOption}
              notMerge={true}
              lazyUpdate={true}
              style={{ height: "400px", width: "100%" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default EEGGraph;
