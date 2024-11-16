import { useEffect, useState } from "react";
import MusicUploader from "./MusicUploader";
import StartAnalysis from "./StartAnalysis";
import EndAnalysis from "./EndAnalysis";

const AnalysisManager = () => {
  const [musicFile, setMusicFile] = useState(null);
  const [musicURL, setMusicURL] = useState(null);
  const [music, setMusic] = useState(null);

  const handleFileUpload = (file) => {
    if (file) {
      setMusicFile(file);
      const url = URL.createObjectURL(file);
      setMusicURL(url);
      setMusic(new Audio(url));
    }
  };

  useEffect(() => {
    return () => {
      if (musicURL) {
        URL.revokeObjectURL(musicURL);
      }
    };
  }, [musicURL]);

  const playMusic = () => {
    if (music) {
      music.play();
    }
  };

  const stopMusic = () => {
    if (music) {
      music.pause();
      music.currentTime = 0;
    }
  };

  return (
    <div>
      <h1>Music Player</h1>
      <MusicUploader onFileUpload={handleFileUpload} />
      {musicURL && (
        <div>
          <audio controls src={musicURL}>
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
      <StartAnalysis startAnalysis={playMusic} />
      <EndAnalysis endAnalysis={stopMusic} />
    </div>
  );
};
export default AnalysisManager;
