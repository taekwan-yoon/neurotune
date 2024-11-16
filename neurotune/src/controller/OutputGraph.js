import React, { useState, useRef, useEffect } from "react";
import { io } from "socket.io-client";
import { BarChart, Bar, XAxis, Tooltip, Legend } from "recharts";

const SOCKET_SERVER_URL = "http://127.0.0.1:5000/";

const OutputGraph = () => {
  const socketRef = useRef();
  const [data, setData] = useState([]);

  useEffect(() => {
    if (!socketRef.current) {
      socketRef.current = io(SOCKET_SERVER_URL);

      socketRef.current.on("connect", () => {
        console.log("Connected to WebSocket server");
      });

      socketRef.current.on("output_data", (msg) => {
        console.log("Received Output Data: ", msg);

        if (msg && msg.time && msg.status) {
          let formattedTime;
          try {
            formattedTime = new Date(msg.time).toLocaleTimeString();
          } catch (error) {
            console.error("Error parsing time:", error);
            formattedTime = "Invalid Time";
          }

          const dataPoint = { time: formattedTime, status: msg.status };
          setData((prevData) => {
            const newData = [...prevData, dataPoint];
            return newData.slice(-20);
          });
        } else {
          console.error("Invalid data format received:", msg);
        }
      });
      socketRef.current.on("disconnect", () => {
        console.log("Disconnected from WebSocket server");
      });
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  const getColor = (status) => {
    switch (status) {
      case "good":
        return "#00FF00"; // Green
      case "neutral":
        return "#FFFF00"; // Yellow
      case "bad":
        return "#FFA500"; // Orange
      default:
        return "#808080"; // Grey
    }
  };
  return (
    <div>
      <h1>Output Graph</h1>
      <BarChart
        width={800}
        height={400}
        data={data}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      >
        <XAxis dataKey="time" />
        <Tooltip />
        <Legend />
        <Bar
          dataKey="status"
          fill="#8884d8"
          isAnimationActive={false}
          label={{ position: "top" }}
          shape={(props) => {
            const { x, y, width, height, payload } = props;
            return (
              <rect
                x={x}
                y={y}
                width={width}
                height={height}
                fill={getColor(payload.status)}
              />
            );
          }}
        />
      </BarChart>
    </div>
  );
};
export default OutputGraph;
