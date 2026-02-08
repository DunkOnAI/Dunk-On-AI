import React from 'react';
import './Homepage.css';
// Import only logo and background image, remove player.png related imports
import basketballLogo from './images/logo.png';
import backgroundImage from './images/bg.jpg';

// Fantasy Basketball App Homepage - Version without player images, logo scaled proportionally
const Homepage = () => {
  return (
    <div className="homepage-container" style={{ backgroundImage: `url(${backgroundImage})` }}>
      {/* Core login card - No player images displayed */}
      <div className="login-card">
        {/* Logo with proportional scaling to normal size */}
        <img src={basketballLogo} alt="App Logo" className="logo-img" />
        <h1 className="app-title">Fantasy Basketball app</h1>
        
        {/* Email input field */}
        <input type="email" className="input-box" placeholder="Email" required />
        {/* Password input field */}
        <input type="password" className="input-box" placeholder="Password" required />
        
        {/* Login button */}
        <button className="login-btn">Log In</button>
        
        {/* Functional links group (forgot password / sign up) */}
        <div className="link-group">
          <a href="/forgot">Forgot Password?</a>
          <a href="/signup">Sign Up</a>
        </div>
      </div>

      {/* Navigation bar */}
      <div className="nav-bar">
        <span>Home</span>
        <span>Teams</span>
        <span>Players</span>
        <span>Stats</span>
        <span>News</span>
      </div>

      {/* Notification card with match information */}
      <div className="notice-card">
        <p className="notice-text">Fantasy Basketball  7:30 PM Lakers vs Lakers</p>
        {/* Bottom tab bar */}
        <div className="bottom-tab">
          <div className="tab-text">Dashboard</div>
          <div className="tab-text">Search</div>
          <div className="tab-text">Profile</div>
        </div>
      </div>
    </div>
  );
};

export default Homepage;