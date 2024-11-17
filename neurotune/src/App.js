import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import MusicContainer from "./view/MusicContainer";
import EEGContainer from "./view/EEGContainer";
import OutputContainer from "./view/OutputContainer";

function App() {
  return (
    <div className="app-container">
      <h1 className="neurotune-title">NeuroTune</h1>
      <MusicContainer />
      <EEGContainer />
      <OutputContainer />
    </div>
  );
}

export default App;
