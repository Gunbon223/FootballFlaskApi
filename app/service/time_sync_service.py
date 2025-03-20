from flask import current_app
from app.service.team_ranking_service import TeamRankingService
from app.service.db_sync_service import DBSyncService
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.exc import SQLAlchemyError

# Import the models to sync
from app.model.card import Card
from app.model.goal import Goal
from app.model.lineup import Lineup
from app.model.team_season_ranking import Team_Season_Ranking
from app.model.team import Team, Team_Coach
from app.model.player import Player, PlayerTeamSeason
from app.model.match import Match
from app.model.tournament import Tournament
from app.model.round import Round
from app.model.season import Season
from app.model.transfer_history import Transfer_History
from appdb import db

class TimeSyncService:
    """Service to handle periodic sync operations for season rankings and Redis."""

    def __init__(self, sync_interval_seconds=3600):  # Default: 1 hour
        """Initialize the time sync service."""
        self.sync_interval_seconds = sync_interval_seconds
        self.team_ranking_service = TeamRankingService()
        self.db_sync_service = DBSyncService()
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.models_to_sync = [
            (Tournament, 'tournament'),
            (Season, 'season'),
            (Team, 'team'),
            (Player, 'player'),
            (Match, 'match'),
            (Round, 'round'),
            (Card, 'card'),
            (Goal, 'goal'),
            (Lineup, 'lineup'),
            (Team_Season_Ranking, 'team_season_ranking'),
            (Transfer_History, 'transfer_history'),
            (Team_Coach, 'team_coach'),
            (PlayerTeamSeason, 'player_team_season')
        ]

    def start(self):
        """Start the scheduled sync operations."""
        if not self.is_running:
            self.scheduler.add_job(
                self.perform_sync_operations,
                'interval',
                seconds=self.sync_interval_seconds
            )
            self.scheduler.start()
            self.is_running = True
            current_app.logger.info(f"TimeSyncService started. Sync interval: {self.sync_interval_seconds} seconds")

    def stop(self):
        """Stop the scheduled sync operations."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            current_app.logger.info("TimeSyncService stopped.")

    def perform_sync_operations(self):
        """Perform the sync operations - update all season rankings and sync to Redis."""
        try:
            # Update all season rankings
            self._update_all_season_rankings()

            # Sync all models to Redis
            self._sync_to_redis()

            current_app.logger.info("Sync operations completed successfully.")
        except Exception as e:
            current_app.logger.error(f"Error performing sync operations: {str(e)}")

    def _update_all_season_rankings(self):
        """Update rankings for all seasons."""
        try:
            # Query all seasons directly
            seasons = db.session.query(Season).all()

            for season in seasons:
                try:
                    self.team_ranking_service.update_season_ranking(season.id)
                    current_app.logger.info(f"Updated rankings for season ID: {season.id}")
                except Exception as e:
                    current_app.logger.error(f"Error updating rankings for season ID {season.id}: {str(e)}")
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error when fetching seasons: {str(e)}")

    def _sync_to_redis(self):
        """Sync all models to Redis."""
        try:
            total = self.db_sync_service.sync_all_models(self.models_to_sync)
            current_app.logger.info(f"Successfully synced {total} records to Redis")
        except Exception as e:
            current_app.logger.error(f"Error syncing to Redis: {str(e)}")

    def run_once(self):
        """Manually trigger a sync operation."""
        self.perform_sync_operations()

    def set_sync_interval(self, seconds):
        """Change the sync interval."""
        if not isinstance(seconds, int) or seconds <= 0:
            raise ValueError("Sync interval must be a positive integer")

        self.sync_interval_seconds = seconds

        # Restart scheduler with new interval if running
        if self.is_running:
            self.stop()
            self.start()