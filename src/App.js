import React from 'react';
// Import the Homepage component (we'll create this next)
import Homepage from './Homepage';
// Import global styles (optional, can keep empty)
import './App.css';

function App() {
  // The root component of the app, renders the Homepage
  return (
    <div className="App">
      <Homepage />
    </div>
  );
}

export default App;