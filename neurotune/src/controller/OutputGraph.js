import React, { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

const OutputGraph = ({ msg }) => {
  const [data, setData] = useState([]);
  console.log(msg)
  useEffect(() => {
    if (msg && msg.length > 0) {
      const item = msg[0];
      const prediction = item.prediction; // "good", "neutral", or "bad"
      const formattedTime = new Date().toLocaleTimeString();
      const statusToValue = {
        good: 3,
        neutral: 2,
        bad: 1,
      };

      const dataPoint = {
        time: formattedTime,
        status: prediction,
        value: statusToValue[prediction] || 0, // Default to 0 if prediction is unrecognized
      };

      setData((prevData) => {
        const newData = [...prevData, dataPoint];
        return newData.slice(-20); // Keep only the last 20 entries
      });
    }
  }, [msg]); // Only run when msg changes

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
      {data.length > 0 ? (
        <BarChart
          width={800}
          height={400}
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <XAxis dataKey="time" />
          <YAxis
            type="number"
            domain={[0, 4]}
            ticks={[1, 2, 3]}
            tickFormatter={(value) => {
              const labelMap = { 1: "Bad", 2: "Neutral", 3: "Good" };
              return labelMap[value] || value;
            }}
          />
          <Tooltip
            formatter={(value, name, props) => {
              const labelMap = { 1: "Bad", 2: "Neutral", 3: "Good" };
              return [labelMap[value] || value, "Status"];
            }}
          />
          <Bar
            dataKey="value"
            isAnimationActive={false}
            label={{ position: "top" }}
            fillOpacity={1}
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
      ) : (
        <p>No data received yet.</p>
      )}
    </div>
  );
};

export default OutputGraph;
