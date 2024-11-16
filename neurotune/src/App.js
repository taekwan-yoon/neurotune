import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css"
import FetchDataExample from "./controller/FetchDataExample";
import MusicPlayer from "./controller/MusicPlayer";

function App() {
  return (
    <div className="App">
      <FetchDataExample/>

      <MusicPlayer/>
    </div>
  );
}

export default App;
