import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import WeekView from "./components/WeekView";
import AddEvent from "./components/AddEvent";


function App() {
  return (
      <Router>
          <Routes>
              <Route path="/" element={<WeekView />} />
              <Route path="/events/add" element={<AddEvent />} />
          </Routes>
      </Router>
  );
}
export default App;