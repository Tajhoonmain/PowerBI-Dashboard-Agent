import { Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./components/home";
import { EvaluationDashboard } from "./components/dashboard/EvaluationDashboard";

function App() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/evaluation" element={<EvaluationDashboard />} />
        </Routes>
      </>
    </Suspense>
  );
}

export default App;
