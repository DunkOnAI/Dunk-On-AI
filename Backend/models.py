# This file defines the database models used in the application

from __future__ import annotations
from datetime import datetime
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from Backend import db
from sqlalchemy import String, Text, DateTime, Float, Integer, ForeignKey, UniqueConstraint, func

# Association table for Users and Players (favourite_players)
favourite_players = sa.Table(
    "favourite_players", #table name
    db.Model.metadata, #this attatches them to Flask-SQLAlchemy's metadata so we can use this anywhere
    sa.Column("id", Integer, primary_key=True),
    sa.Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True), #self explanatory, cascade means delete this row if player is deleted
    sa.Column("player_id", ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True),
    UniqueConstraint("user_id", "player_id", name="uq_favourite_players_user_player"), #this ensures a user cant favourite the same player twice
)

# Association table for Users and Teams (favourite_teams)
favourite_teams = sa.Table(
    "favourite_teams",
    db.Model.metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
    sa.Column("team_id", ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True),
    UniqueConstraint("user_id", "team_id", name="uq_favourite_teams_user_team"),
)

# Association table for AI teams and Players
ai_team_players = sa.Table(
    "ai_team_players",
    db.Model.metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("ai_team_id", ForeignKey("ai_teams.id", ondelete="CASCADE"), nullable=False, index=True),
    sa.Column("player_id", ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True),
    UniqueConstraint("ai_team_id", "player_id", name="uq_ai_team_players_ai_team_player"),
)


# Association object between User <-> Player with extra fields
class UserTeamPlayer(db.Model):
    __tablename__ = "user_team_players"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Player role: starter or bench (default: bench)
    role: so.Mapped[str] = so.mapped_column(String(50), nullable=False, default="bench")
    
    # Timestamp of when this player was added to the user's team, func.now() uses the current time
    added_at: so.Mapped[datetime] = so.mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    #table level constraints
    __table_args__ = (
        UniqueConstraint("user_id", "player_id", name="uq_user_team_players_user_player"),
        #users cant add the same player to their team twice
    )

    # Relationships
    user: so.Mapped["User"] = so.relationship(back_populates="team_player_links")
    #relationship back to the user model, back_populates creates the two way relationship
    player: so.Mapped["Player"] = so.relationship(back_populates="user_team_links")
    #relationship back to the player model


# User model
class User(db.Model):
    __tablename__ = "users" #table name

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    supabase_auth_id: so.Mapped[Optional[str]] = so.mapped_column(String(36), unique=True, nullable=True, index=True)
    username: so.Mapped[str] = so.mapped_column(String(80), unique=True, nullable=False, index=True)
    email: so.Mapped[str] = so.mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: so.Mapped[str] = so.mapped_column(String(200), nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # User -> UserTeamPlayer (1-many)
    team_player_links: so.Mapped[List["UserTeamPlayer"]] = so.relationship(
        back_populates="user",
        cascade="all, delete-orphan", #this means that if the user is deleted, delete all team players of the user
        passive_deletes=True,
    )

    # User -> Players (many-to-many, simplified access)
    #secondary: specifies the association table to use
    players: so.Mapped[List["Player"]] = so.relationship(
        secondary="user_team_players",
        viewonly=True, #the user can only read it
        back_populates="users",
    )

    # User -> Matchups (1-many)
    matchups: so.Mapped[List["Matchup"]] = so.relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Favourites: many-to-many
    favourite_players: so.Mapped[List["Player"]] = so.relationship(
        secondary=favourite_players,
        back_populates="favourited_by",
    )

    favourite_teams: so.Mapped[List["Team"]] = so.relationship(
        secondary=favourite_teams,
        back_populates="favourited_by",
    )

    #this method defines how to represent the User object as a string, useful for debugging 
    def __repr__(self) -> str:
        return f"<User {self.username}>"


# Team model
class Team(db.Model):
    __tablename__ = "teams"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(String(100), unique=True, nullable=False, index=True)
    city: so.Mapped[str] = so.mapped_column(String(100), nullable=False)
    abbreviation: so.Mapped[str] = so.mapped_column(String(10), unique=True, nullable=False, index=True)

    # Team -> Players (1-many)
    players: so.Mapped[List["Player"]] = so.relationship(
        back_populates="team",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    # Team -> News (1-many)
    news_items: so.Mapped[List["News"]] = so.relationship(
        back_populates="team",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Favourites: many-to-many
    favourited_by: so.Mapped[List["User"]] = so.relationship(
        secondary=favourite_teams,
        back_populates="favourite_teams",
    )

    def __repr__(self) -> str:
        return f"<Team {self.name}>"


# Player model
class Player(db.Model):
    __tablename__ = "players"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(String(120), nullable=False, index=True)
    team_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    position: so.Mapped[str] = so.mapped_column(String(10), nullable=False)
    height_weight: so.Mapped[Optional[str]] = so.mapped_column(String(50), nullable=True)

    # Player -> Team (many-to-one)
    team: so.Mapped[Optional["Team"]] = so.relationship(back_populates="players")

    # Player -> GameStats (1-many)
    game_stats: so.Mapped[List["GameStat"]] = so.relationship(
        back_populates="player",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Player -> News (1-many)
    news_items: so.Mapped[List["News"]] = so.relationship(
        back_populates="player",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Relationship through UserTeamPlayer association object
    user_team_links: so.Mapped[List["UserTeamPlayer"]] = so.relationship(
        back_populates="player",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Access to users (without extra fields)
    users: so.Mapped[List["User"]] = so.relationship(
        secondary="user_team_players",
        viewonly=True,
        back_populates="players",
    )

    # Favourites: many-to-many
    favourited_by: so.Mapped[List["User"]] = so.relationship(
        secondary=favourite_players,
        back_populates="favourite_players",
    )

    # AI teams (many-to-many)
    ai_teams: so.Mapped[List["AITeam"]] = so.relationship(
        secondary=ai_team_players,
        back_populates="players",
    )

    def __repr__(self) -> str:
        return f"<Player {self.name}>"


# GameStat model
class GameStat(db.Model):
    __tablename__ = "game_stats"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    player_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    game_date: so.Mapped[datetime] = so.mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    points: so.Mapped[int] = so.mapped_column(Integer, nullable=False, default=0)
    rebounds: so.Mapped[int] = so.mapped_column(Integer, nullable=False, default=0)
    assists: so.Mapped[int] = so.mapped_column(Integer, nullable=False, default=0)
    steals: so.Mapped[int] = so.mapped_column(Integer, nullable=False, default=0)
    blocks: so.Mapped[int] = so.mapped_column(Integer, nullable=False, default=0)
    turnovers: so.Mapped[int] = so.mapped_column(Integer, nullable=False, default=0)
    minutes_played: so.Mapped[float] = so.mapped_column(Float, nullable=False, default=0.0)

    # Many-to-one relationship
    player: so.Mapped["Player"] = so.relationship(back_populates="game_stats")

    def __repr__(self) -> str:
        return f"<GameStat player_id={self.player_id} date={self.game_date}>"


# News model
class News(db.Model):
    __tablename__ = "news"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(String(200), nullable=False)
    content: so.Mapped[str] = so.mapped_column(Text, nullable=False)
    
    # Optional: can be player news OR team news OR both/none
    player_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("players.id", ondelete="SET NULL"), nullable=True, index=True)
    team_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    
    source_url: so.Mapped[Optional[str]] = so.mapped_column(String(500), nullable=True)
    created_at: so.Mapped[datetime] = so.mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many-to-one relationships
    player: so.Mapped[Optional["Player"]] = so.relationship(back_populates="news_items")
    team: so.Mapped[Optional["Team"]] = so.relationship(back_populates="news_items")

    def __repr__(self) -> str:
        return f"<News {self.title}>"


# AITeam model
class AITeam(db.Model):
    __tablename__ = "ai_teams"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    week_number: so.Mapped[int] = so.mapped_column(Integer, nullable=False, index=True)
    created_at: so.Mapped[datetime] = so.mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # AI team roster (many-to-many)
    players: so.Mapped[List["Player"]] = so.relationship(
        secondary=ai_team_players,
        back_populates="ai_teams",
    )

    # AI Team -> Matchups (1-many)
    matchups: so.Mapped[List["Matchup"]] = so.relationship(
        back_populates="ai_team",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<AITeam week={self.week_number}>"


# Matchup model
class Matchup(db.Model):
    __tablename__ = "matchups"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ai_team_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("ai_teams.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Optional because matchup might not be completed yet
    result: so.Mapped[Optional[str]] = so.mapped_column(String(50), nullable=True)
    
    user_score: so.Mapped[float] = so.mapped_column(Float, nullable=False, default=0.0)
    ai_score: so.Mapped[float] = so.mapped_column(Float, nullable=False, default=0.0)
    played_on: so.Mapped[datetime] = so.mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Many-to-one relationships
    user: so.Mapped["User"] = so.relationship(back_populates="matchups")
    ai_team: so.Mapped["AITeam"] = so.relationship(back_populates="matchups")

    __table_args__ = (
        UniqueConstraint("user_id", "ai_team_id", name="uq_matchups_user_ai_team"),
    )

    def __repr__(self) -> str:
        return f"<Matchup user_id={self.user_id} vs ai_team_id={self.ai_team_id}>"
