import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './index.css';

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email && password) onLogin();
  };

  return (
    <div className="login-page">
      <div className="background-animation">
        <div className="grid-lines"></div>
        <div className="floating-orb orb-1"></div>
        <div className="floating-orb orb-2"></div>
        <div className="floating-orb orb-3"></div>
      </div>

      <motion.div 
        className="player-left"
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 1, delay: 0.2 }}
      >
        <div className="player-silhouette"></div>
      </motion.div>

      <motion.div 
        className="player-right"
        initial={{ x: 100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 1, delay: 0.2 }}
      >
        <div className="player-silhouette"></div>
      </motion.div>

      <motion.div 
        className="login-container"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div 
          className="logo"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <svg viewBox="0 0 200 80" className="basketball-wings">
            <path d="M 30,40 Q 20,30 10,35 Q 5,40 10,45 Q 20,50 30,40" fill="white" stroke="#00d4ff" strokeWidth="2"/>
            <path d="M 40,40 Q 30,25 15,28 Q 8,35 15,42 Q 30,45 40,40" fill="white" stroke="#00d4ff" strokeWidth="2"/>
            <path d="M 50,40 Q 38,20 18,22 Q 10,30 18,38 Q 38,40 50,40" fill="white" stroke="#00d4ff" strokeWidth="2"/>
            <circle cx="100" cy="40" r="22" fill="#ff8557" stroke="#d86744" strokeWidth="2"/>
            <path d="M 78,40 Q 100,35 122,40" stroke="#d86744" strokeWidth="1.5" fill="none"/>
            <path d="M 78,40 Q 100,45 122,40" stroke="#d86744" strokeWidth="1.5" fill="none"/>
            <path d="M 100,18 Q 95,40 100,62" stroke="#d86744" strokeWidth="1.5" fill="none"/>
            <path d="M 100,18 Q 105,40 100,62" stroke="#d86744" strokeWidth="1.5" fill="none"/>
            <path d="M 170,40 Q 180,30 190,35 Q 195,40 190,45 Q 180,50 170,40" fill="white" stroke="#00d4ff" strokeWidth="2"/>
            <path d="M 160,40 Q 170,25 185,28 Q 192,35 185,42 Q 170,45 160,40" fill="white" stroke="#00d4ff" strokeWidth="2"/>
            <path d="M 150,40 Q 162,20 182,22 Q 190,30 182,38 Q 162,40 150,40" fill="white" stroke="#00d4ff" strokeWidth="2"/>
          </svg>
        </motion.div>

        <motion.h1 
          className="app-title"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          Fantasy Basketball app
        </motion.h1>

        <form onSubmit={handleSubmit} className="login-form">
          <motion.input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.6 }}
            required
          />

          <motion.input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.7 }}
            required
          />

          <motion.button 
            type="submit" 
            className="login-btn"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.8 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Log In
          </motion.button>

          <motion.div 
            className="login-footer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.9 }}
          >
            <a href="#" className="forgot-password">Forgot Password?</a>
            <a href="#" className="sign-up">Sign Up</a>
          </motion.div>
        </form>
      </motion.div>

      <div className="data-viz left-viz">
        {[40, 70, 55, 80, 60, 90].map((height, i) => (
          <motion.div 
            key={i}
            className="bar"
            style={{ height: `${height}%` }}
            initial={{ height: 0 }}
            animate={{ height: `${height}%` }}
            transition={{ duration: 0.8, delay: 1 + i * 0.1 }}
          />
        ))}
      </div>

      <div className="data-viz right-viz">
        {[60, 85, 45, 75, 55, 95].map((height, i) => (
          <motion.div 
            key={i}
            className="bar"
            style={{ height: `${height}%` }}
            initial={{ height: 0 }}
            animate={{ height: `${height}%` }}
            transition={{ duration: 0.8, delay: 1 + i * 0.1 }}
          />
        ))}
      </div>
    </div>
  );
};


const HomePage = ({ onLogout, onSettings }) => {
  const [activeTab, setActiveTab] = useState('home');
  const tabs = ['Home', 'Teams', 'Players', 'Stats', 'News'];
  
  const games = [
    { id: 1, time: '7:30 PM', team1: 'Lakers', team2: 'Warriors', logo1: '🏀', logo2: '⚡' },
    { id: 2, time: '8:00 PM', team1: 'Celtics', team2: 'Heat', logo1: '🍀', logo2: '🔥' }
  ];

  return (
    <div className="home-page">
      <div className="home-background">
        <div className="circuit-pattern"></div>
      </div>

      <nav className="top-nav">
        {tabs.map((tab) => (
          <button
            key={tab}
            className={`nav-tab ${activeTab === tab.toLowerCase() ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.toLowerCase())}
          >
            {tab}
          </button>
        ))}
      </nav>

      <main className="main-content">
        <div className="section">
          <h2 className="section-title">Upcoming Games</h2>
          <div className="games-grid">
            {games.map((game, index) => (
              <motion.div
                key={game.id}
                className="game-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="game-header">
                  <div className="league-badge">
                    <span className="league-logo">🏀</span>
                    <span>Fantasy Basketball</span>
                  </div>
                  <div className="game-time">{game.time}</div>
                </div>
                <div className="game-matchup">
                  <div className="team">
                    <div className="team-logo">{game.logo1}</div>
                    <span>{game.team1}</span>
                  </div>
                  <div className="vs">vs</div>
                  <div className="team">
                    <div className="team-logo">{game.logo2}</div>
                    <span>{game.team2}</span>
                  </div>
                </div>
                <button className="watch-btn">View Details</button>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="section">
          <h2 className="section-title">Your Performance</h2>
          <div className="stats-grid">
            {[
              { icon: '📈', value: '1,247', label: 'Total Points' },
              { icon: '🏆', value: '15', label: 'Wins' },
              { icon: '👥', value: '23', label: 'Active Players' }
            ].map((stat, i) => (
              <motion.div 
                key={i}
                className="stat-card"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 + i * 0.1 }}
              >
                <div className="stat-icon">{stat.icon}</div>
                <div className="stat-content">
                  <div className="stat-value">{stat.value}</div>
                  <div className="stat-label">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </main>

      <nav className="bottom-nav">
        <button className="nav-btn">
          <span className="icon">📊</span>
          <span>Dashboard</span>
        </button>
        <button className="nav-btn">
          <span className="icon">🔍</span>
          <span>Search</span>
        </button>
        <button className="nav-btn" onClick={onSettings}>
          <span className="icon">👤</span>
          <span>Profile</span>
        </button>
      </nav>
    </div>
  );
};


const SettingsPage = ({ onBack, onLogout }) => {
  const settings = [
    { id: 'account', label: 'Account', icon: '👤' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'privacy', label: 'Privacy', icon: '🔒' },
    { id: 'theme', label: 'Theme', icon: '🎨' },
    { id: 'help', label: 'Help', icon: '❓' }
  ];

  return (
    <div className="settings-page">
      <div className="settings-background">
        <div className="circuit-pattern"></div>
      </div>

      <header className="settings-header">
        <button className="back-btn" onClick={onBack}>←</button>
        <h1 className="settings-title">Settings</h1>
        <div style={{ width: 40 }}></div>
      </header>

      <main className="settings-main">
        <motion.div 
          className="settings-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="settings-menu">
            {settings.map((option, index) => (
              <motion.div
                key={option.id}
                className="settings-item"
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.1 * index }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="settings-item-content">
                  <span className="settings-icon">{option.icon}</span>
                  <span className="settings-label">{option.label}</span>
                </div>
                <span className="settings-arrow">›</span>
              </motion.div>
            ))}
          </div>

          <motion.button
            className="logout-btn"
            onClick={onLogout}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            whileHover={{ scale: 1.02 }}
          >
            <span>🚪</span>
            <span>Log Out</span>
          </motion.button>
        </motion.div>
      </main>
    </div>
  );
};


function App() {
  const [page, setPage] = useState('login');

  return (
    <AnimatePresence mode="wait">
      {page === 'login' && <LoginPage onLogin={() => setPage('home')} />}
      {page === 'home' && <HomePage onSettings={() => setPage('settings')} onLogout={() => setPage('login')} />}
      {page === 'settings' && <SettingsPage onBack={() => setPage('home')} onLogout={() => setPage('login')} />}
    </AnimatePresence>
  );
}

export default App;