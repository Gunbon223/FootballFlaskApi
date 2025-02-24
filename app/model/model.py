# from sqlalchemy import (
#     Column, Integer, String, ForeignKey, Date, DateTime, Boolean, Enum, Text
# )
# from sqlalchemy.orm import relationship, declarative_base
#
# Base = declarative_base()
#
#
# class Tournament(Base):
#     __tablename__ = "tournament"
#
#     tournament_id = Column(Integer, primary_key=True,autoincrement=True)
#     name = Column(String(255), nullable=False)
#     country = Column(String(100), nullable=False)
#
#     seasons = relationship("Season", back_populates="tournament")
#
#
# class Season(Base):
#     __tablename__ = "season"
#
#     season_id = Column(Integer, primary_key=True,autoincrement=True)
#     tournament_id = Column(Integer, ForeignKey("tournament.tournament_id"), nullable=False)
#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date, nullable=False)
#     description = Column(Text)
#     name = Column(String(255), nullable=False)
#     tournament = relationship("Tournament", back_populates="seasons")
#     teams = relationship("Team_Season", back_populates="season")
#
#
# class Team(Base):
#     __tablename__ = "team"
#
#     team_id = Column(Integer, primary_key=True,autoincrement=True)
#     name = Column(String(255), nullable=False)
#     national = Column(String(255), nullable=False)
#
#     players = relationship("Player", back_populates="team")
#
#
# class Coach(Base):
#     __tablename__ = "coach"
#
#     coach_id = Column(Integer, primary_key=True,autoincrement=True)
#     name = Column(String(255), nullable=False)
#     nationality = Column(String(100), nullable=False)
#     date_of_birth = Column(Date, nullable=False)
#     experience_years = Column(Integer, nullable=False)
#
#
# class Team_Coach(Base):
#     __tablename__ = "team_coach"
#
#     team_coach_id = Column(Integer, primary_key=True,autoincrement=True)
#     team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     coach_id = Column(Integer, ForeignKey("coach.coach_id"), nullable=False)
#     season_id = Column(Integer, ForeignKey("season.season_id"), nullable=False)
#
#
# class Player(Base):
#     __tablename__ = "player"
#
#     player_id = Column(Integer, primary_key=True,autoincrement=True)
#     team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     name = Column(String(255), nullable=False)
#     position = Column(String(50), nullable=False)
#     nationality = Column(String(100), nullable=False)
#     date_of_birth = Column(Date, nullable=False)
#
#     team = relationship("Team", back_populates="players")
#
#
# class Player_Season(Base):
#     __tablename__ = "player_season"
#
#     player_season_id = Column(Integer, primary_key=True,autoincrement=True)
#     player_id = Column(Integer, ForeignKey("player.player_id"), nullable=False)
#     season_id = Column(Integer, ForeignKey("season.season_id"), nullable=False)
#     team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     appearances = Column(Integer, default=0)
#     goals = Column(Integer, default=0)
#     assists = Column(Integer, default=0)
#     yellow_cards = Column(Integer, default=0)
#     red_cards = Column(Integer, default=0)
#
#
# class Match(Base):
#     __tablename__ = "match"
#
#     match_id = Column(Integer, primary_key=True,autoincrement=True)
#     season_id = Column(Integer, ForeignKey("season.season_id"), nullable=False)
#     home_team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     away_team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     match_date = Column(DateTime, nullable=False)
#     home_score = Column(Integer, default=0)
#     away_score = Column(Integer, default=0)
#     home_coach_id = Column(Integer, ForeignKey("team_coach.team_coach_id"), nullable=False)
#     away_coach_id = Column(Integer, ForeignKey("team_coach.team_coach_id"), nullable=False)
#
#
# class Lineup(Base):
#     __tablename__ = "lineup"
#
#     lineup_id = Column(Integer, primary_key=True,autoincrement=True)
#     match_id = Column(Integer, ForeignKey("match.match_id"), nullable=False)
#     player_id = Column(Integer, ForeignKey("player.player_id"), nullable=False)
#     team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     is_starting = Column(Boolean, default=False)
#
#
# class Goal(Base):
#     __tablename__ = "goal"
#
#     goal_id = Column(Integer, primary_key=True,autoincrement=True)
#     match_id = Column(Integer, ForeignKey("match.match_id"), nullable=False)
#     player_id = Column(Integer, ForeignKey("player.player_id"), nullable=False)
#     team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     goal_time = Column(Integer, nullable=False)
#
#
# class Card(Base):
#     __tablename__ = "card"
#
#     card_id = Column(Integer, primary_key=True,autoincrement=True)
#     match_id = Column(Integer, ForeignKey("match.match_id"), nullable=False)
#     player_id = Column(Integer, ForeignKey("player.player_id"), nullable=False)
#     team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     card_type = Column(Enum("Yellow", "Red"), nullable=False)
#     card_time = Column(Integer, nullable=False)
#
#
# class Transfer_History(Base):
#     __tablename__ = "transfer_history"
#
#     transfer_id = Column(Integer, primary_key=True,autoincrement=True)
#     player_id = Column(Integer, ForeignKey("player.player_id"), nullable=False)
#     from_team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     to_team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#     transfer_date = Column(Date, nullable=False)
#     season_id = Column(Integer, ForeignKey("season.season_id"), nullable=False)
#     detail = Column(Text)
#
#
# class Player_Achievement(Base):
#     __tablename__ = "player_achievement"
#
#     achievement_id = Column(Integer, primary_key=True,autoincrement=True)
#     player_id = Column(Integer, ForeignKey("player.player_id"), nullable=False)
#     season_id = Column(Integer, ForeignKey("season.season_id"), nullable=False)
#     match_id = Column(Integer, ForeignKey("match.match_id"), nullable=False)
#     award_name = Column(String(255), nullable=False)
#     description = Column(Text)
#
#
# class Season_Standings(Base):
#     __tablename__ = "season_standings"
#
#     standing_id = Column(Integer, primary_key=True,autoincrement=True)
#     matches_played = Column(Integer, default=0)
#     wins = Column(Integer, default=0)
#     draws = Column(Integer, default=0)
#     losses = Column(Integer, default=0)
#     goals_for = Column(Integer, default=0)
#     goals_against = Column(Integer, default=0)
#     goal_difference = Column(Integer, default=0)
#     points = Column(Integer, default=0)
#     ranking = Column(Integer, nullable=False)
#
#
# class Team_Season(Base):
#     __tablename__ = "team_season"
#
#     standing_id = Column(Integer, ForeignKey("season_standings.standing_id"), primary_key=True,autoincrement=True)
#     season_id = Column(Integer, ForeignKey("season.season_id"), nullable=False)
#     team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
#
