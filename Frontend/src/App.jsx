import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './index.css';

const parseApiPayload = async (response) => {
  const text = await response.text();
  if (!text) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
};

// Reusable animated auth screen wrapper for both login and signup.
const AuthScene = ({ title, subtitle, children }) => (
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
          <path d="M 30,40 Q 20,30 10,35 Q 5,40 10,45 Q 20,50 30,40" fill="white" stroke="#00d4ff" strokeWidth="2" />
          <path d="M 40,40 Q 30,25 15,28 Q 8,35 15,42 Q 30,45 40,40" fill="white" stroke="#00d4ff" strokeWidth="2" />
          <path d="M 50,40 Q 38,20 18,22 Q 10,30 18,38 Q 38,40 50,40" fill="white" stroke="#00d4ff" strokeWidth="2" />
          <circle cx="100" cy="40" r="22" fill="#ff8557" stroke="#d86744" strokeWidth="2" />
          <path d="M 78,40 Q 100,35 122,40" stroke="#d86744" strokeWidth="1.5" fill="none" />
          <path d="M 78,40 Q 100,45 122,40" stroke="#d86744" strokeWidth="1.5" fill="none" />
          <path d="M 100,18 Q 95,40 100,62" stroke="#d86744" strokeWidth="1.5" fill="none" />
          <path d="M 100,18 Q 105,40 100,62" stroke="#d86744" strokeWidth="1.5" fill="none" />
          <path d="M 170,40 Q 180,30 190,35 Q 195,40 190,45 Q 180,50 170,40" fill="white" stroke="#00d4ff" strokeWidth="2" />
          <path d="M 160,40 Q 170,25 185,28 Q 192,35 185,42 Q 170,45 160,40" fill="white" stroke="#00d4ff" strokeWidth="2" />
          <path d="M 150,40 Q 162,20 182,22 Q 190,30 182,38 Q 162,40 150,40" fill="white" stroke="#00d4ff" strokeWidth="2" />
        </svg>
      </motion.div>

      <motion.h1
        className="app-title"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        {title}
      </motion.h1>

      {subtitle ? <p className="auth-subtitle">{subtitle}</p> : null}

      {children}
    </motion.div>

    <div className="data-viz left-viz">
      {[40, 70, 55, 80, 60, 90].map((height, index) => (
        <motion.div
          key={`left-${index}`}
          className="bar"
          style={{ height: `${height}%` }}
          initial={{ height: 0 }}
          animate={{ height: `${height}%` }}
          transition={{ duration: 0.8, delay: 1 + index * 0.1 }}
        />
      ))}
    </div>

    <div className="data-viz right-viz">
      {[60, 85, 45, 75, 55, 95].map((height, index) => (
        <motion.div
          key={`right-${index}`}
          className="bar"
          style={{ height: `${height}%` }}
          initial={{ height: 0 }}
          animate={{ height: `${height}%` }}
          transition={{ duration: 0.8, delay: 1 + index * 0.1 }}
        />
      ))}
    </div>
  </div>
);

const LoginPage = ({ onLogin, onGoToSignup }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault(); // Prevent form submission from refreshing the page.
    if (!email || !password) {
      return;
    }

    setAuthError('');
    setIsSubmitting(true);

    // Login request to backend auth endpoint.
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const payload = await parseApiPayload(response);

      if (!response.ok) {
        throw new Error(payload?.error?.message || payload?.raw || `Login failed (${response.status})`);
      }

      // Pass auth payload back to App state.
      onLogin(payload);
    } catch (error) {
      setAuthError(error.message || 'Login failed.');
    } finally {
      // Re-enable submit button after request completes.
      setIsSubmitting(false);
    }
  };

  // Render the login form with animated inputs and buttons, and display any authentication errors.
  return (
    <AuthScene title="Fantasy Basketball App" subtitle="Log in to continue">
      <form onSubmit={handleSubmit} className="login-form">
        <motion.input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.6 }}
          required
        />

        <motion.input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.7 }}
          required
        />

        <motion.button
          type="submit"
          className="login-btn"
          disabled={isSubmitting}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.8 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isSubmitting ? 'Please wait...' : 'Log In'}
        </motion.button>

        <motion.div
          className="login-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.9 }}
        >
          <button type="button" className="link-button forgot-password">Forgot Password?</button>
          <button type="button" className="link-button sign-up" onClick={onGoToSignup}>Sign Up</button>
        </motion.div>

        {authError ? <p className="auth-feedback error">{authError}</p> : null}
      </form>
    </AuthScene>
  );
};

const SignupPage = ({ onSignup, onGoToLogin }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [authInfo, setAuthInfo] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault(); // Prevent form submission from refreshing the page.

    if (!email || !password || !confirmPassword) {
      setAuthError('Email, password, and confirm password are required.');
      return;
    }

    if (password !== confirmPassword) {
      setAuthError('Passwords do not match.');
      return;
    }

    setAuthError('');
    setAuthInfo('');
    setIsSubmitting(true);

    // Signup request to backend auth endpoint.
    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          username: username.trim() || undefined,
        }),
      });
      const payload = await parseApiPayload(response);

      if (!response.ok) {
        throw new Error(payload?.error?.message || payload?.raw || `Signup failed (${response.status})`);
      }

      // If signup includes a session token, log in immediately.
      if (payload?.auth?.access_token) {
        onSignup(payload);
        return;
      }

      // Otherwise, show informational message about checking email for confirmation.
      setAuthInfo('Signup successful. Check your email, then log in.');
    } catch (error) {
      setAuthError(error.message || 'Signup failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Render the signup form with animated inputs and buttons, and display any authentication errors or info messages.
  return (
    <AuthScene title="Create Account" subtitle="Set up your fantasy profile">
      <form onSubmit={handleSubmit} className="login-form">
        <motion.input
          type="text"
          placeholder="Username (optional)"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.6 }}
        />

        <motion.input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.7 }}
          required
        />

        <motion.input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.8 }}
          required
        />

        <motion.input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.9 }}
          required
        />

        <motion.button
          type="submit"
          className="login-btn"
          disabled={isSubmitting}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isSubmitting ? 'Please wait...' : 'Create Account'}
        </motion.button>

        <motion.div
          className="login-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 1.1 }}
        >
          <span className="auth-hint">Already have an account?</span>
          <button type="button" className="link-button sign-up" onClick={onGoToLogin}>Log In</button>
        </motion.div>

        {authError ? <p className="auth-feedback error">{authError}</p> : null}
        {authInfo ? <p className="auth-feedback info">{authInfo}</p> : null}
      </form>
    </AuthScene>
  );
};

// Main home page after logging in, with tabs for different sections and a settings/logout button.
const HomePage = ({ authUser, onLogout, onSettings }) => {
  const [activeTab, setActiveTab] = useState('home');
  const tabs = ['Home', 'Teams', 'Players', 'Stats', 'News'];

  const games = [
    { id: 1, time: '7:30 PM', team1: 'Lakers', team2: 'Warriors', logo1: '🏀', logo2: '⚡' },
    { id: 2, time: '8:00 PM', team1: 'Celtics', team2: 'Heat', logo1: '🍀', logo2: '🔥' },
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
        {authUser ? <p>Signed in as {authUser.email}</p> : null}
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
              { icon: '👥', value: '23', label: 'Active Players' },
            ].map((stat, index) => (
              <motion.div
                key={index}
                className="stat-card"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 + index * 0.1 }}
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

// Settings page with various options and a logout button, accessible from the home page.
const SettingsPage = ({ onBack, onLogout }) => {
  const settings = [
    { id: 'account', label: 'Account', icon: '👤' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'privacy', label: 'Privacy', icon: '🔒' },
    { id: 'theme', label: 'Theme', icon: '🎨' },
    { id: 'help', label: 'Help', icon: '❓' },
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
  const [authState, setAuthState] = useState({
    user: null,
    accessToken: null,
  });

  // On login/signup success, persist user + token and move to home screen.
  const handleLogin = (payload) => {
    setAuthState({
      user: payload?.user || null,
      accessToken: payload?.auth?.access_token || null,
    });
    setPage('home');
  };

  // On logout, clear auth state and return to login screen.
  const handleLogout = () => {
    setAuthState({
      user: null,
      accessToken: null,
    });
    setPage('login');
  };

  // Render one page at a time based on current app state.
  return (
    <AnimatePresence mode="wait">
      {page === 'login' && (
        <LoginPage key="login" onLogin={handleLogin} onGoToSignup={() => setPage('signup')} />
      )}
      {page === 'signup' && (
        <SignupPage key="signup" onSignup={handleLogin} onGoToLogin={() => setPage('login')} />
      )}
      {page === 'home' && (
        <HomePage
          key="home"
          authUser={authState.user}
          onSettings={() => setPage('settings')}
          onLogout={handleLogout}
        />
      )}
      {page === 'settings' && (
        <SettingsPage key="settings" onBack={() => setPage('home')} onLogout={handleLogout} />
      )}
    </AnimatePresence>
  );
}

export default App;
