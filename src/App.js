import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './AppStyles.css';

// 登录页面组件
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
          <div className="logo-text">DUNK ON AI</div>
        </motion.div>

        <motion.p 
          className="app-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          Build Your Team, Challenge AI
        </motion.p>

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

// 主页组件 - 增强版
const HomePage = ({ onLogout, onSettings, onNavigate }) => {
  const [activeTab, setActiveTab] = useState('home');

  const upcomingGames = [
    {
      id: 1,
      date: 'Today, 7:30 PM',
      userTeam: 'Your Team',
      aiTeam: 'AI Warriors',
      userScore: 105,
      aiScore: 112,
      status: 'Live',
      quarter: 'Q4'
    },
    {
      id: 2,
      date: 'Tomorrow, 8:00 PM',
      userTeam: 'Your Team',
      aiTeam: 'AI Champions',
      userScore: null,
      aiScore: null,
      status: 'Upcoming',
      quarter: null
    },
    {
      id: 3,
      date: 'Feb 17, 6:00 PM',
      userTeam: 'Your Team',
      aiTeam: 'AI Legends',
      userScore: null,
      aiScore: null,
      status: 'Upcoming',
      quarter: null
    }
  ];

  const userStats = {
    wins: 15,
    losses: 8,
    winRate: 65.2,
    totalPoints: 2547,
    avgPoints: 110.7,
    ranking: 3
  };

  return (
    <div className="home-page">
      <div className="home-background">
        <div className="circuit-pattern"></div>
      </div>

      {/* Header */}
      <header className="page-header">
        <div className="header-content">
          <h1 className="page-logo">DUNK ON AI</h1>
          <div className="header-actions">
            <button className="icon-btn" onClick={onSettings}>⚙️</button>
          </div>
        </div>
      </header>

      <main className="main-content">
        {/* User Performance Section */}
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
            <button className="cta-btn" onClick={() => onNavigate('team')}>
              Pick Players →
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
        <button className="nav-btn" onClick={() => onNavigate('team')}>
          <span className="icon">👥</span>
          <span>Team</span>
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

// 球员统计页面 - 全新
const StatsPage = ({ onBack, onNavigate }) => {
  const [selectedYear, setSelectedYear] = useState('2024');
  const [selectedPlayer, setSelectedPlayer] = useState(null);

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
      trend: 'up'
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
      trend: 'up'
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
      trend: 'down'
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
      trend: 'stable'
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
      trend: 'up'
    }
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

      {/* Header */}
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
                onClick={() => setSelectedPlayer(player)}
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

        {/* Team Stats Overview */}
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

        {/* Compare Button */}
        <button className="compare-stats-btn" onClick={() => onNavigate('compare')}>
          Compare with AI Teams →
        </button>
      </main>

      {/* Bottom Navigation */}
      <nav className="bottom-nav">
        <button className="nav-btn" onClick={() => onNavigate('home')}>
          <span className="icon">🏠</span>
          <span>Home</span>
        </button>
        <button className="nav-btn" onClick={() => onNavigate('team')}>
          <span className="icon">👥</span>
          <span>Team</span>
        </button>
        <button className="nav-btn active">
          <span className="icon">📊</span>
          <span>Stats</span>
        </button>
        <button className="nav-btn">
          <span className="icon">👤</span>
          <span>Profile</span>
        </button>
      </nav>
    </div>
  );
};

// 设置页面组件
const SettingsPage = ({ onBack, onLogout }) => {
  const settings = [
    { id: 'account', label: 'Account Settings', icon: '👤' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'privacy', label: 'Privacy & Security', icon: '🔒' },
    { id: 'theme', label: 'Theme', icon: '🎨' },
    { id: 'help', label: 'Help & Support', icon: '❓' }
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

// 主应用
function App() {
  const [currentPage, setCurrentPage] = useState('login');

  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  return (
    <AnimatePresence mode="wait">
      {currentPage === 'login' && (
        <LoginPage onLogin={() => handleNavigate('home')} />
      )}
      {currentPage === 'home' && (
        <HomePage 
          onSettings={() => handleNavigate('settings')} 
          onLogout={() => handleNavigate('login')}
          onNavigate={handleNavigate}
        />
      )}
      {currentPage === 'stats' && (
        <StatsPage 
          onBack={() => handleNavigate('home')}
          onNavigate={handleNavigate}
        />
      )}
      {currentPage === 'settings' && (
        <SettingsPage 
          onBack={() => handleNavigate('home')}
          onLogout={() => handleNavigate('login')}
        />
      )}
    </AnimatePresence>
  );
}

export default App;
