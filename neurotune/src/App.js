import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import MusicContainer from "./view/MusicContainer";
import EEGContainer from "./view/EEGContainer";
import OutputContainer from "./view/OutputContainer";
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
      <MusicContainer />
      <EEGContainer />
      <OutputContainer />
    </div>
  );
}

export default App;
