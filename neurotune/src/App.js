import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import FetchDataExample from "./controller/FetchDataExample";
import MusicContainer from "./view/MusicContainer";
import EEGContainer from "./view/EEGContainer";
import OutputContainer from "./view/OutputContainer";
import StartAnalysis from "./controller/StartAnalysis";
import EndAnalysis from "./controller/EndAnalysis";

function App() {
  return (
    <div className="App">
      <MusicContainer />
      <EEGContainer />
      <OutputContainer />
      <FetchDataExample />
      <StartAnalysis />
      <EndAnalysis />
    </div>
  );
}

export default App;
