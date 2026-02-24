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

const getApiErrorMessage = (payload, fallbackMessage) => {
  const baseMessage = payload?.error?.message || payload?.raw || fallbackMessage;
  const debugDetails = payload?.error?.debug;

  if (!debugDetails) {
    return baseMessage;
  }

  const debugMessage = typeof debugDetails === 'string'
    ? debugDetails
    : debugDetails.message || JSON.stringify(debugDetails);

  return `${baseMessage} (${debugMessage})`;
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
    event.preventDefault();
    if (!email || !password) {
      return;
    }

    setAuthError('');
    setIsSubmitting(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const payload = await parseApiPayload(response);

      if (!response.ok) {
        throw new Error(getApiErrorMessage(payload, `Login failed (${response.status})`));
      }

      onLogin(payload);
    } catch (error) {
      setAuthError(error.message || 'Login failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

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
    event.preventDefault();

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
        throw new Error(getApiErrorMessage(payload, `Signup failed (${response.status})`));
      }

      if (payload?.auth?.access_token) {
        onSignup(payload);
        return;
      }

      setAuthInfo('Signup successful. Check your email, then log in.');
    } catch (error) {
      setAuthError(error.message || 'Signup failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

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

// Enhanced home page with performance stats, upcoming games, and CTA.
const HomePage = ({ authUser, onLogout, onSettings, onNavigate }) => {
  const upcomingGames = [
    {
      id: 1,
      date: 'Today, 7:30 PM',
      userTeam: 'Your Team',
      aiTeam: 'AI Warriors',
      userScore: 105,
      aiScore: 112,
      status: 'Live',
      quarter: 'Q4',
    },
    {
      id: 2,
      date: 'Tomorrow, 8:00 PM',
      userTeam: 'Your Team',
      aiTeam: 'AI Champions',
      userScore: null,
      aiScore: null,
      status: 'Upcoming',
      quarter: null,
    },
    {
      id: 3,
      date: 'Feb 17, 6:00 PM',
      userTeam: 'Your Team',
      aiTeam: 'AI Legends',
      userScore: null,
      aiScore: null,
      status: 'Upcoming',
      quarter: null,
    },
  ];

  const userStats = {
    wins: 15,
    losses: 8,
    winRate: 65.2,
    totalPoints: 2547,
    avgPoints: 110.7,
    ranking: 3,
  };

  return (
    <div className="home-page">
      <div className="home-background">
        <div className="circuit-pattern"></div>
      </div>

      <header className="page-header">
        <div className="header-content">
          <h1 className="page-logo">DUNK ON AI</h1>
          <div className="header-actions">
            <button className="icon-btn" onClick={onSettings}>⚙️</button>
          </div>
        </div>
      </header>

      <main className="main-content">
        {authUser ? <p className="signed-in-label">Signed in as {authUser.email}</p> : null}

        {/* Performance Section */}
        <section className="performance-section">
          <div className="section-header">
            <h2 className="section-title">Your Performance</h2>
            <button className="view-all-btn" onClick={() => onNavigate('stats')}>
              View Details →
            </button>
          </div>

          <div className="stats-grid-large">
            <motion.div
              className="stat-card-large"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="stat-icon-large">🏆</div>
              <div className="stat-content-large">
                <div className="stat-value-large">{userStats.wins}-{userStats.losses}</div>
                <div className="stat-label-large">Win-Loss Record</div>
                <div className="stat-extra">{userStats.winRate}% Win Rate</div>
              </div>
            </motion.div>

            <motion.div
              className="stat-card-large"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="stat-icon-large">📊</div>
              <div className="stat-content-large">
                <div className="stat-value-large">{userStats.avgPoints}</div>
                <div className="stat-label-large">Avg Points/Game</div>
                <div className="stat-extra">{userStats.totalPoints} Total</div>
              </div>
            </motion.div>

            <motion.div
              className="stat-card-large"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="stat-icon-large">🎯</div>
              <div className="stat-content-large">
                <div className="stat-value-large">#{userStats.ranking}</div>
                <div className="stat-label-large">Global Ranking</div>
                <div className="stat-extra">Top 1% Players</div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Upcoming Games Section */}
        <section className="games-section">
          <div className="section-header">
            <h2 className="section-title">Upcoming Games</h2>
            <button className="view-all-btn">Schedule →</button>
          </div>

          <div className="games-list">
            {upcomingGames.map((game, index) => (
              <motion.div
                key={game.id}
                className={`game-card-enhanced ${game.status === 'Live' ? 'live' : ''}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
              >
                {game.status === 'Live' && (
                  <div className="live-indicator">
                    <span className="live-dot"></span>
                    LIVE
                  </div>
                )}

                <div className="game-info">
                  <div className="game-date">{game.date}</div>
                  {game.quarter && <div className="game-quarter">{game.quarter}</div>}
                </div>

                <div className="game-matchup-enhanced">
                  <div className="team-section">
                    <div className="team-avatar user-avatar">
                      <span>👤</span>
                    </div>
                    <div className="team-details">
                      <div className="team-name">{game.userTeam}</div>
                      <div className="team-label">YOU</div>
                    </div>
                    {game.userScore !== null && (
                      <div className="team-score">{game.userScore}</div>
                    )}
                  </div>

                  <div className="vs-divider">VS</div>

                  <div className="team-section">
                    {game.aiScore !== null && (
                      <div className="team-score">{game.aiScore}</div>
                    )}
                    <div className="team-details">
                      <div className="team-name">{game.aiTeam}</div>
                      <div className="team-label ai-label">AI</div>
                    </div>
                    <div className="team-avatar ai-avatar">
                      <span>🤖</span>
                    </div>
                  </div>
                </div>

                <button
                  className="game-action-btn"
                  onClick={() => onNavigate('stats')}
                >
                  {game.status === 'Live' ? 'Watch Live' : 'View Matchup'}
                </button>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Build Team CTA */}
        <motion.section
          className="cta-section"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <div className="cta-content">
            <h3 className="cta-title">Build Your Dream Team</h3>
            <p className="cta-text">Select top players and challenge AI opponents</p>
            <button className="cta-btn" onClick={() => onNavigate('stats')}>
              View Stats →
            </button>
          </div>
        </motion.section>
      </main>

      {/* Bottom Navigation */}
      <nav className="bottom-nav">
        <button className="nav-btn active">
          <span className="icon">🏠</span>
          <span>Home</span>
        </button>
        <button className="nav-btn" onClick={() => onNavigate('stats')}>
          <span className="icon">📊</span>
          <span>Stats</span>
        </button>
        <button className="nav-btn" onClick={onSettings}>
          <span className="icon">👤</span>
          <span>Profile</span>
        </button>
      </nav>
    </div>
  );
};

// Player stats page with roster, analytics, and year selector.
const StatsPage = ({ onBack, onNavigate, authUser }) => {
  const [selectedYear, setSelectedYear] = useState('2024');

  const players = [
    {
      id: 1,
      name: 'Ethan Knox',
      number: 10,
      pts: 28.5,
      reb: 7.2,
      ast: 5.8,
      position: 'SF',
      team: 'Your Team',
      trend: 'up',
    },
    {
      id: 2,
      name: 'Jalen Ford',
      number: 23,
      pts: 24.1,
      reb: 4.5,
      ast: 8.9,
      position: 'PG',
      team: 'Your Team',
      trend: 'up',
    },
    {
      id: 3,
      name: 'Marco Lane',
      number: 7,
      pts: 19.7,
      reb: 9.8,
      ast: 2.1,
      position: 'C',
      team: 'Your Team',
      trend: 'down',
    },
    {
      id: 4,
      name: 'Oliver Tate',
      number: 15,
      pts: 16.3,
      reb: 3.9,
      ast: 4.2,
      position: 'SG',
      team: 'Your Team',
      trend: 'stable',
    },
    {
      id: 5,
      name: 'Tyler Briggs',
      number: 32,
      pts: 14.8,
      reb: 8.1,
      ast: 1.7,
      position: 'PF',
      team: 'Your Team',
      trend: 'up',
    },
  ];

  const years = ['2024', '2023', '2022', '2021'];

  const getTrendIcon = (trend) => {
    if (trend === 'up') return '📈';
    if (trend === 'down') return '📉';
    return '➡️';
  };

  return (
    <div className="stats-page">
      <div className="stats-background">
        <div className="circuit-pattern"></div>
      </div>

      <header className="page-header">
        <div className="header-content">
          <button className="back-btn-new" onClick={onBack}>←</button>
          <h1 className="page-title">Player Stats</h1>
          <div style={{ width: 40 }}></div>
        </div>
      </header>

      <main className="stats-main">
        {/* Year Selector */}
        <div className="year-selector">
          <h3 className="selector-title">Season</h3>
          <div className="year-pills">
            {years.map((year) => (
              <button
                key={year}
                className={`year-pill ${selectedYear === year ? 'active' : ''}`}
                onClick={() => setSelectedYear(year)}
              >
                {year}
              </button>
            ))}
          </div>
        </div>

        {/* Players List */}
        <div className="players-section">
          <h3 className="section-title">Your Team Roster</h3>

          <div className="players-list">
            {players.map((player, index) => (
              <motion.div
                key={player.id}
                className="player-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="player-avatar-section">
                  <div className="player-avatar-stats">
                    <div className="jersey-number">{player.number}</div>
                  </div>
                  <div className="player-info">
                    <div className="player-name">{player.name}</div>
                    <div className="player-position">{player.position} • {player.team}</div>
                  </div>
                </div>

                <div className="player-stats-grid">
                  <div className="stat-item">
                    <div className="stat-value-small">{player.pts}</div>
                    <div className="stat-label-small">PTS</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value-small">{player.reb}</div>
                    <div className="stat-label-small">REB</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value-small">{player.ast}</div>
                    <div className="stat-label-small">AST</div>
                  </div>
                  <div className="stat-item">
                    <span className="trend-icon">{getTrendIcon(player.trend)}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Team Analytics */}
        <div className="team-stats-section">
          <h3 className="section-title">Team Analytics</h3>

          <div className="analytics-grid">
            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-icon">🎯</span>
                <span className="analytics-title">Offensive Rating</span>
              </div>
              <div className="analytics-value">118.5</div>
              <div className="analytics-change positive">+5.2% from last season</div>
            </div>

            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-icon">🛡️</span>
                <span className="analytics-title">Defensive Rating</span>
              </div>
              <div className="analytics-value">106.3</div>
              <div className="analytics-change positive">+3.8% from last season</div>
            </div>

            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-icon">⚡</span>
                <span className="analytics-title">Pace</span>
              </div>
              <div className="analytics-value">102.7</div>
              <div className="analytics-change negative">-1.5% from last season</div>
            </div>

            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-icon">🎲</span>
                <span className="analytics-title">Win Probability</span>
              </div>
              <div className="analytics-value">67%</div>
              <div className="analytics-change positive">vs AI Average</div>
            </div>
          </div>
        </div>

        <button className="compare-stats-btn" onClick={() => onNavigate('home')}>
          Back to Home →
        </button>
      </main>

      {/* Bottom Navigation */}
      <nav className="bottom-nav">
        <button className="nav-btn" onClick={() => onNavigate('home')}>
          <span className="icon">🏠</span>
          <span>Home</span>
        </button>
        <button className="nav-btn active">
          <span className="icon">📊</span>
          <span>Stats</span>
        </button>
        <button className="nav-btn" onClick={() => onNavigate('settings')}>
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
          onNavigate={setPage}
        />
      )}
      {page === 'stats' && (
        <StatsPage key="stats" onBack={() => setPage('home')} onNavigate={setPage} authUser={authState.user} />
      )}
      {page === 'settings' && (
        <SettingsPage key="settings" onBack={() => setPage('home')} onLogout={handleLogout} />
      )}
    </AnimatePresence>
  );
}

export default App;
