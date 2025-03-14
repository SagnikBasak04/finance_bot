import { Route, Routes } from "react-router-dom";

import Landing from "./pages/landing/Landing";
import Signup from "./pages/auth/Signup";
import Login from "./pages/auth/Login";
import Home from "./pages/home/Home";

function App() {
  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-blue-800 to-black">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login />} />
          <Route path="/home" element={<Home />} />
        </Routes>
      </div>
    </>
  )
}

export default App;
