import React from "react";
import EEGGraph from "../controller/EEGGraph";
import "./EEGContainer.css";

const EEGContainer = () => {
  return (
    <div className="mac-window">
      <div className="mac-title-bar">
        <div className="mac-title">EEG Data Visualization</div>
      </div>
      <div className="mac-content">
        <EEGGraph />
      </div>
    </div>
  );
};

export default EEGContainer;
