// App.js
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import MusicContainer from "./view/MusicContainer";
import EEGContainer from "./view/EEGContainer";
import OutputContainer from "./controller/obsolete/OutputContainer";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBrain } from "@fortawesome/free-solid-svg-icons";

function App() {
  return (
    <div className="app-container">
      <h1 className="neurotune-title">
        Neur
        <span className="brain-icon">
          <FontAwesomeIcon icon={faBrain} />
        </span>
        Tune ♪
      </h1>
      <h3 className="neurotune-subtitle">
        Think your music
        <span className="dots">
          <span>.</span>
          <span>.</span>
          <span>.</span>
        </span>
      </h3>
      <MusicContainer />
      <EEGContainer />
      <OutputContainer />
    </div>
  );
}

export default App;
