import React from "react";
import MusicPlayer from "../controller/MusicPlayer";
import "./MusicContainer.css";

const MusicContainer = () => {
  return (
    <div className="mac-window">
      <div className="mac-title-bar">
        <div className="mac-title">Music Player</div>
      </div>
      <div className="mac-content">
        <MusicPlayer />
      </div>
    </div>
  );
};

export default MusicContainer;
