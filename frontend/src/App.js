import React from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Login } from './components/login.jsx';
import { Register } from './components/register.jsx';
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path='/' element={ <Login/> }/>
          <Route path='/register' element={ <Register/> }/>
        </Routes>
      </div>
    </Router>

  );
}

export default App;
