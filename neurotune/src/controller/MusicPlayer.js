import { useYoutube } from "react-youtube-music-player";
import React, { useState } from "react";
import axios from "axios";
import "./MusicPlayer.css";

const MusicPlayer = () => {
  const [videoId, setVideoId] = useState("RDLbqzhXWl33U");
  const { playerDetails, actions } = useYoutube({
    id: videoId,
    type: "video",
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [thumbnailUrl, setThumbnailUrl] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false); // State to control modal visibility
  const API_KEY = process.env.REACT_APP_API_KEY;
  //const API_KEY = "AIzaSyDGFYVG-hBZH76H6L2OA6em0QFy6QEstz4"
  // Function to search for a song
  const searchSong = async () => {
    try {
      console.log("API Key:", API_KEY);
      const response = await axios.get(
        `https://www.googleapis.com/youtube/v3/search`,
        {
          params: {
            part: "snippet",
            q: searchQuery,
            type: "video",
            key: API_KEY,
            maxResults: 5,
            videoCategoryId: "10",
          },
        }
      );
      if (response.data.items && response.data.items.length > 0) {
        setSearchResults(response.data.items); // Store the search results
        setIsModalOpen(true); // Open modal when search results are available
      } else {
        alert("No results found");
        setSearchResults([]); // Clear previous results if no results found
      }
    } catch (error) {
      console.error("Error fetching video: ", error);
    }
  };

  // Function to play a selected video
  const selectVideo = (video) => {
    setVideoId(video.id.videoId);
    setThumbnailUrl(video.snippet.thumbnails.high.url);
    setIsModalOpen(false); // Close the modal when a video is selected
  };

  // Function to close the modal without selecting a video
  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="music-player-container">
      <input
        type="text"
        className="search-input"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Enter song name"
      />
      <button className="mac-button" onClick={searchSong}>
        Search
      </button>

      {/* Now Playing Section */}
      {thumbnailUrl && (
        <div className="now-playing">
          <img
            src={thumbnailUrl}
            alt="Song thumbnail"
            className="song-thumbnail"
          />
          <p>Now Playing: {playerDetails?.title}</p>
          <p>Channel: {playerDetails?.channel}</p>
        </div>
      )}

      {/* Player Action Buttons */}
      <div className="action-buttons">
        <button className="mac-button" onClick={actions.playVideo}>
          Play
        </button>
        <button className="mac-button" onClick={actions.pauseVideo}>
          Pause
        </button>
      </div>

      {/* Modal (Popup) to display search results */}
      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-button" onClick={closeModal}>
              ×
            </button>
            <h3>Search Results:</h3>
            <ul className="results-list">
              {searchResults.map((video) => (
                <li key={video.id.videoId} className="search-result-item">
                  <img
                    src={video.snippet.thumbnails.default.url}
                    alt="Thumbnail"
                    className="result-thumbnail"
                  />
                  <div className="result-details">
                    <p>{video.snippet.title}</p>
                    <button
                      className="mac-button select-button"
                      onClick={() => selectVideo(video)}
                    >
                      Select
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default MusicPlayer;
