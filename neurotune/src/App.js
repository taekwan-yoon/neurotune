import "./App.css";
import FetchDataExample from "./controller/FetchDataExample";
import AnalysisManager from "./controller/AnalysisManager";
import EEGContainer from "./view/EEGContainer";

function App() {
  return (
    <div className="App">
      <FetchDataExample />
      <AnalysisManager />
      <EEGContainer />
    </div>
  );
}

export default App;
