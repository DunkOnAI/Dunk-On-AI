import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './index.css';

const SESSION_STORAGE_KEY = 'dunk_on_ai_session';
const LAST_ACTIVITY_KEY = 'dunk_on_ai_last_activity';
const THEME_STORAGE_KEY = 'dunk_on_ai_theme';
const NOTIFICATIONS_STORAGE_KEY = 'dunk_on_ai_notifications';
const IDLE_TIMEOUT_MS = 10 * 60 * 1000;

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

const ROSTER_PLAYERS = [
  {
    id: 1,
    name: 'Ethan Knox',
    number: 10,
    pts: 28.5,
    reb: 7.2,
    ast: 5.8,
    position: 'SF',
    team: 'Your Team',
    sport: 'basketball',
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
    sport: 'basketball',
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
    sport: 'basketball',
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
    sport: 'basketball',
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
    sport: 'basketball',
    trend: 'up',
  },
  {
    id: 6,
    name: 'Noah Reed',
    number: 8,
    pts: 17.9,
    reb: 6.4,
    ast: 3.7,
    position: 'SG',
    team: 'Your Team',
    sport: 'basketball',
    trend: 'stable',
  },
  {
    id: 7,
    name: 'Luca Hayes',
    number: 41,
    pts: 12.6,
    reb: 11.1,
    ast: 2.9,
    position: 'C',
    team: 'Your Team',
    sport: 'basketball',
    trend: 'up',
  },
];

const getLineupSizeBySport = (sport) => {
  const normalized = (sport || '').toLowerCase();
  if (normalized === 'football') return 11;
  if (normalized === 'basketball') return 5;
  if (normalized === 'volleyball') return 6;
  return 5;
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
                  onClick={() => onNavigate('matchup')}
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
        <button className="nav-btn" onClick={() => onNavigate('matchup')}>
          <span className="icon">⚔️</span>
          <span>Match Up</span>
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
  const players = ROSTER_PLAYERS;

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

        <button className="compare-stats-btn" onClick={() => onNavigate('matchup')}>
          Open Match Up →
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
        <button className="nav-btn" onClick={() => onNavigate('matchup')}>
          <span className="icon">⚔️</span>
          <span>Match Up</span>
        </button>
        <button className="nav-btn" onClick={() => onNavigate('settings')}>
          <span className="icon">👤</span>
          <span>Profile</span>
        </button>
      </nav>
    </div>
  );
};

const MatchupPage = ({ onBack, onNavigate, authUser, onNewNotification }) => {
  const aiPool = [
    { id: 101, name: 'Orion Blaze', number: 2, position: 'PG', pts: 22.4, reb: 4.1, ast: 9.2 },
    { id: 102, name: 'Kai Mercer', number: 11, position: 'SG', pts: 26.8, reb: 5.0, ast: 4.9 },
    { id: 103, name: 'Darius Volt', number: 34, position: 'PF', pts: 18.6, reb: 10.4, ast: 2.8 },
    { id: 104, name: 'Zane Hollow', number: 25, position: 'SF', pts: 20.7, reb: 7.4, ast: 3.1 },
    { id: 105, name: 'Rex Carter', number: 55, position: 'C', pts: 15.2, reb: 12.0, ast: 1.5 },
    { id: 106, name: 'Mason Voss', number: 4, position: 'PG', pts: 18.1, reb: 3.6, ast: 8.5 },
    { id: 107, name: 'Ivy Sloan', number: 13, position: 'SF', pts: 21.3, reb: 6.8, ast: 4.2 },
    { id: 108, name: 'Jett Cross', number: 19, position: 'SG', pts: 17.4, reb: 4.0, ast: 3.9 },
    { id: 109, name: 'Axel Grant', number: 44, position: 'PF', pts: 16.8, reb: 9.6, ast: 2.3 },
    { id: 110, name: 'Nico Dunn', number: 31, position: 'C', pts: 14.1, reb: 11.5, ast: 1.9 },
  ];
  const teamSport = (ROSTER_PLAYERS[0]?.sport || 'basketball').toLowerCase();
  const lineupSizeBySport = getLineupSizeBySport(teamSport);
  const TEAM_SIZE = Math.min(lineupSizeBySport, ROSTER_PLAYERS.length, aiPool.length);

  const [selectedPlayerIds, setSelectedPlayerIds] = useState(() =>
    ROSTER_PLAYERS.slice(0, TEAM_SIZE).map((player) => player.id)
  );
  const generateAiTeam = () => {
    const shuffled = [...aiPool].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, TEAM_SIZE);
  };
  const [aiPlayers, setAiPlayers] = useState(() => generateAiTeam());
  const [simulation, setSimulation] = useState(null);
  const [matchupNotice, setMatchupNotice] = useState(`Build your ${TEAM_SIZE}-player team, then tap Simulate.`);
  const resultRef = useRef(null);

  const selectedTeam = ROSTER_PLAYERS.filter((player) => selectedPlayerIds.includes(player.id));

  const summarizeTeam = (teamPlayers) => {
    const totals = teamPlayers.reduce((acc, player) => ({
      pts: acc.pts + player.pts,
      reb: acc.reb + player.reb,
      ast: acc.ast + player.ast,
    }), { pts: 0, reb: 0, ast: 0 });
    const size = teamPlayers.length || 1;
    const avg = {
      pts: totals.pts / size,
      reb: totals.reb / size,
      ast: totals.ast / size,
    };
    const power = avg.pts * 1.45 + avg.reb * 1.15 + avg.ast * 1.35;
    return { ...avg, power };
  };

  const yourTeamStats = summarizeTeam(selectedTeam);
  const aiTeamStats = summarizeTeam(aiPlayers);
  const powerDiff = yourTeamStats.power - aiTeamStats.power;
  const winChance = Math.max(20, Math.min(80, Math.round(50 + powerDiff * 1.4)));

  const togglePlayerSelection = (playerId) => {
    setSimulation(null);
    setSelectedPlayerIds((current) => {
      if (current.includes(playerId)) {
        if (current.length <= TEAM_SIZE) {
          setMatchupNotice(`You must keep ${TEAM_SIZE} players in your team.`);
          return current;
        }
        setMatchupNotice('Player removed from lineup.');
        return current.filter((id) => id !== playerId);
      }
      if (current.length >= TEAM_SIZE) {
        setMatchupNotice(`Team size is fixed at ${TEAM_SIZE}.`);
        return current;
      }
      setMatchupNotice('Player added to lineup.');
      return [...current, playerId];
    });
  };

  const runSimulation = () => {
    if (selectedPlayerIds.length !== TEAM_SIZE) {
      setMatchupNotice(`You need exactly ${TEAM_SIZE} players to simulate.`);
      return;
    }
    const nextAiTeam = generateAiTeam();
    setAiPlayers(nextAiTeam);
    const nextAiStats = summarizeTeam(nextAiTeam);
    const nextPowerDiff = yourTeamStats.power - nextAiStats.power;
    const nextWinChance = Math.max(20, Math.min(80, Math.round(50 + nextPowerDiff * 1.4)));
    const userWinThreshold = nextWinChance / 100;
    const userWon = Math.random() <= userWinThreshold;
    const baseYourScore = Math.round(yourTeamStats.pts * 3.3 + yourTeamStats.ast * 1.6 + yourTeamStats.reb * 0.8);
    const baseAiScore = Math.round(nextAiStats.pts * 3.3 + nextAiStats.ast * 1.6 + nextAiStats.reb * 0.8);
    const yourScore = baseYourScore + Math.round((Math.random() - 0.5) * 16) + (userWon ? 4 : -2);
    const aiScore = baseAiScore + Math.round((Math.random() - 0.5) * 16) + (userWon ? -2 : 4);

    setSimulation({
      yourScore,
      aiScore,
      winner: yourScore >= aiScore ? 'you' : 'ai',
    });
    if (onNewNotification) {
      onNewNotification({
        id: `match-${Date.now()}`,
        type: 'match_result',
        title: yourScore >= aiScore ? 'Match Won' : 'Match Lost',
        message: `Final score: You ${yourScore} - ${aiScore} AI Titans`,
        createdAt: new Date().toISOString(),
      });
    }
    setMatchupNotice('Simulation completed.');
    setTimeout(() => {
      resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 20);
  };

  const refreshAiTeam = () => {
    setSimulation(null);
    setAiPlayers(generateAiTeam());
    setMatchupNotice('AI team refreshed.');
  };

  const statRows = [
    { label: 'PTS', your: yourTeamStats.pts, ai: aiTeamStats.pts },
    { label: 'REB', your: yourTeamStats.reb, ai: aiTeamStats.reb },
    { label: 'AST', your: yourTeamStats.ast, ai: aiTeamStats.ast },
    { label: 'POWER', your: yourTeamStats.power, ai: aiTeamStats.power },
  ];

  return (
    <div className="stats-page">
      <div className="stats-background">
        <div className="circuit-pattern"></div>
      </div>

      <header className="page-header">
        <div className="header-content">
          <button className="back-btn-new" onClick={onBack}>←</button>
          <h1 className="page-title">Players Match Up</h1>
          <div style={{ width: 40 }}></div>
        </div>
      </header>

      <main className="stats-main">
        {authUser ? <p className="signed-in-label">Signed in as {authUser.email}</p> : null}
        {TEAM_SIZE < lineupSizeBySport ? (
          <p className="signed-in-label">
            Team rule: {teamSport} needs {lineupSizeBySport}, available pool allows {TEAM_SIZE}.
          </p>
        ) : null}

        <section className="matchup-hero-card">
          <div className="matchup-teams-row">
            <div className="matchup-team-block">
              <div className="matchup-team-badge">YOU</div>
              <h3>Your Lineup</h3>
              <p>{selectedTeam.length} players selected</p>
            </div>
            <div className="matchup-vs">VS</div>
            <div className="matchup-team-block">
              <div className="matchup-team-badge ai">AI</div>
              <h3>AI Titans</h3>
              <p>{aiPlayers.length} players selected</p>
            </div>
          </div>
          <div className="matchup-chance">
            <span>Win Chance</span>
            <strong>{winChance}%</strong>
          </div>
          <div className="matchup-meter">
            <div className="matchup-meter-fill" style={{ width: `${winChance}%` }}></div>
          </div>
        </section>

        <section className="players-section">
          <div className="section-header">
            <h3 className="section-title">Build Your Team ({TEAM_SIZE} Players)</h3>
            <div className="matchup-actions">
              <button className="view-all-btn" onClick={refreshAiTeam}>New AI Team</button>
              <button className="view-all-btn" onClick={runSimulation}>Simulate</button>
            </div>
          </div>
          <p className="matchup-hint">{matchupNotice} Selected: {selectedPlayerIds.length}/{TEAM_SIZE}</p>
          <div className="players-list">
            {ROSTER_PLAYERS.map((player, index) => {
              const isSelected = selectedPlayerIds.includes(player.id);
              return (
                <motion.div
                  key={player.id}
                  className={`player-card matchup-select-card ${isSelected ? 'selected' : ''}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.08 }}
                  whileHover={{ scale: 1.02 }}
                  onClick={() => togglePlayerSelection(player.id)}
                >
                  <div className="player-avatar-section">
                    <div className="player-avatar-stats">
                      <div className="jersey-number">{player.number}</div>
                    </div>
                    <div className="player-info">
                      <div className="player-name">{player.name}</div>
                      <div className="player-position">{player.position} • {player.pts} PTS</div>
                    </div>
                    <div className="matchup-checkbox">{isSelected ? '✓' : '+'}</div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </section>

        <section className="team-stats-section">
          <h3 className="section-title">AI Selected Team</h3>
          <div className="matchup-ai-list">
            {aiPlayers.map((player) => (
              <div key={player.id} className="matchup-ai-item">
                <div className="matchup-ai-left">
                  <span className="matchup-ai-number">#{player.number}</span>
                  <div>
                    <div className="player-name">{player.name}</div>
                    <div className="player-position">{player.position}</div>
                  </div>
                </div>
                <div className="matchup-ai-right">
                  <span>{player.pts} PTS</span>
                  <span>{player.reb} REB</span>
                  <span>{player.ast} AST</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="team-stats-section">
          <h3 className="section-title">Head-to-Head Comparison</h3>
          <div className="matchup-stats-board">
            {statRows.map((row) => {
              const total = row.your + row.ai;
              const yourWidth = total ? Math.max(12, (row.your / total) * 100) : 50;
              const aiWidth = total ? Math.max(12, (row.ai / total) * 100) : 50;
              return (
                <div key={row.label} className="matchup-stat-row">
                  <div className="matchup-stat-values">
                    <span>{row.your.toFixed(1)}</span>
                    <span>{row.label}</span>
                    <span>{row.ai.toFixed(1)}</span>
                  </div>
                  <div className="matchup-bars">
                    <div className="matchup-bar your" style={{ width: `${yourWidth}%` }}></div>
                    <div className="matchup-bar ai" style={{ width: `${aiWidth}%` }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {simulation ? (
          <section className="matchup-result-card" ref={resultRef}>
            <h3>{simulation.winner === 'you' ? 'You Win the Simulation' : 'AI Wins the Simulation'}</h3>
            <p>Final Score: You {simulation.yourScore} - {simulation.aiScore} AI</p>
          </section>
        ) : null}
      </main>

      <nav className="bottom-nav">
        <button className="nav-btn" onClick={() => onNavigate('home')}>
          <span className="icon">🏠</span>
          <span>Home</span>
        </button>
        <button className="nav-btn" onClick={() => onNavigate('stats')}>
          <span className="icon">📊</span>
          <span>Stats</span>
        </button>
        <button className="nav-btn active">
          <span className="icon">⚔️</span>
          <span>Match Up</span>
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
const SettingsPage = ({ onBack, onLogout, authUser, themeMode, onChangeTheme, notifications }) => {
  const settings = [
    { id: 'account', label: 'Account', icon: '👤' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'privacy', label: 'Privacy', icon: '🔒' },
    { id: 'theme', label: 'Theme', icon: '🎨' },
    { id: 'help', label: 'Help', icon: '❓' },
  ];
  const [activeSetting, setActiveSetting] = useState(null);

  const renderSettingContent = () => {
    if (activeSetting === 'account') {
      return (
        <div className="settings-detail-card">
          <h3 className="settings-detail-title">Account Information</h3>
          <div className="settings-detail-row">
            <span>Email</span>
            <strong>{authUser?.email || 'Not available'}</strong>
          </div>
          <div className="settings-detail-row">
            <span>Username</span>
            <strong>{authUser?.username || 'Not set'}</strong>
          </div>
          <div className="settings-detail-row">
            <span>Account Status</span>
            <strong>Active</strong>
          </div>
        </div>
      );
    }

    if (activeSetting === 'notifications') {
      return (
        <div className="settings-detail-card">
          <h3 className="settings-detail-title">Notifications</h3>
          {notifications.length === 0 ? (
            <p className="settings-detail-empty">No notifications yet. Match updates will appear here.</p>
          ) : (
            <div className="settings-notification-list">
              {notifications.map((note) => (
                <div key={note.id} className="settings-notification-item">
                  <div>
                    <strong>{note.title}</strong>
                    <p>{note.message}</p>
                  </div>
                  <span>{new Date(note.createdAt).toLocaleString()}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    if (activeSetting === 'privacy') {
      return (
        <div className="settings-detail-card">
          <h3 className="settings-detail-title">Privacy</h3>
          <ul className="settings-detail-list">
            <li>Your login credentials are never shown in plain text.</li>
            <li>Only essential account data is stored for core app features.</li>
            <li>Session data expires after inactivity for additional safety.</li>
            <li>Sensitive keys are managed on backend environment variables.</li>
            <li>You can request account data updates or deletion from support.</li>
          </ul>
        </div>
      );
    }

    if (activeSetting === 'theme') {
      return (
        <div className="settings-detail-card">
          <h3 className="settings-detail-title">Theme</h3>
          <p className="settings-detail-empty">Choose your preferred app background style.</p>
          <div className="settings-theme-actions">
            <button
              className={`settings-theme-btn ${themeMode === 'dark' ? 'active' : ''}`}
              onClick={() => onChangeTheme('dark')}
            >
              Deep Navy
            </button>
            <button
              className={`settings-theme-btn ${themeMode === 'beige' ? 'active' : ''}`}
              onClick={() => onChangeTheme('beige')}
            >
              Warm Beige
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="settings-detail-card">
        <h3 className="settings-detail-title">Help</h3>
        <ul className="settings-detail-list">
          <li>Use Match Up to build your team and simulate game outcomes.</li>
          <li>Check Notifications for match results and important updates.</li>
          <li>If stats fail to load, refresh the page and verify your connection.</li>
          <li>For login issues, verify email and password, then retry.</li>
          <li>Contact support if an issue persists after retrying.</li>
        </ul>
      </div>
    );
  };

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
          {activeSetting ? (
            <>
              <button className="view-all-btn" onClick={() => setActiveSetting(null)}>
                ← Back to Settings
              </button>
              {renderSettingContent()}
            </>
          ) : (
            <>
              <div className="settings-menu">
                {settings.map((option, index) => (
                  <motion.div
                    key={option.id}
                    className="settings-item"
                    onClick={() => setActiveSetting(option.id)}
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
            </>
          )}
        </motion.div>
      </main>
    </div>
  );
};

function App() {
  const [page, setPage] = useState('login');
  const [themeMode, setThemeMode] = useState(() => localStorage.getItem(THEME_STORAGE_KEY) || 'dark');
  const [authState, setAuthState] = useState({
    user: null,
    accessToken: null,
  });
  const [notifications, setNotifications] = useState(() => {
    try {
      const raw = localStorage.getItem(NOTIFICATIONS_STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeMode);
    localStorage.setItem(THEME_STORAGE_KEY, themeMode);
  }, [themeMode]);

  useEffect(() => {
    const now = Date.now();
    const lastActivityRaw = localStorage.getItem(LAST_ACTIVITY_KEY);
    const lastActivity = lastActivityRaw ? Number(lastActivityRaw) : now;
    const isIdleTooLong = now - lastActivity > IDLE_TIMEOUT_MS;

    if (isIdleTooLong) {
      localStorage.removeItem(SESSION_STORAGE_KEY);
      localStorage.setItem(LAST_ACTIVITY_KEY, String(now));
      setPage('login');
      setAuthState({ user: null, accessToken: null });
      return;
    }

    const rawSession = localStorage.getItem(SESSION_STORAGE_KEY);
    if (!rawSession) {
      localStorage.setItem(LAST_ACTIVITY_KEY, String(now));
      return;
    }

    try {
      const parsed = JSON.parse(rawSession);
      const storedAuth = parsed?.authState || { user: null, accessToken: null };
      const storedPage = parsed?.page || 'home';

      if (storedAuth?.accessToken) {
        setAuthState(storedAuth);
        setPage(storedPage);
      }
    } catch {
      localStorage.removeItem(SESSION_STORAGE_KEY);
      setPage('login');
      setAuthState({ user: null, accessToken: null });
    }

    localStorage.setItem(LAST_ACTIVITY_KEY, String(now));
  }, []);

  useEffect(() => {
    const updateActivity = () => {
      localStorage.setItem(LAST_ACTIVITY_KEY, String(Date.now()));
    };

    const events = ['click', 'keydown', 'mousemove', 'scroll', 'touchstart'];
    events.forEach((eventName) => window.addEventListener(eventName, updateActivity, { passive: true }));
    updateActivity();

    return () => {
      events.forEach((eventName) => window.removeEventListener(eventName, updateActivity));
    };
  }, []);

  useEffect(() => {
    if (!authState?.accessToken) {
      localStorage.removeItem(SESSION_STORAGE_KEY);
      return;
    }

    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({ page, authState }));
  }, [page, authState]);

  useEffect(() => {
    localStorage.setItem(NOTIFICATIONS_STORAGE_KEY, JSON.stringify(notifications));
  }, [notifications]);

  const addNotification = (notification) => {
    setNotifications((current) => [notification, ...current].slice(0, 25));
  };

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
    localStorage.removeItem(SESSION_STORAGE_KEY);
    localStorage.setItem(LAST_ACTIVITY_KEY, String(Date.now()));
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
      {page === 'matchup' && (
        <MatchupPage
          key="matchup"
          onBack={() => setPage('stats')}
          onNavigate={setPage}
          authUser={authState.user}
          onNewNotification={addNotification}
        />
      )}
      {page === 'settings' && (
        <SettingsPage
          key="settings"
          onBack={() => setPage('home')}
          onLogout={handleLogout}
          authUser={authState.user}
          themeMode={themeMode}
          onChangeTheme={setThemeMode}
          notifications={notifications}
        />
      )}
    </AnimatePresence>
  );
}

export default App;
