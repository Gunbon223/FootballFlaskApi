from flask import current_app

from app.model.team import Team_Coach
from app.repository.base_repository import BaseRepository
from app.model.coach import Coach
from app.service.db_sync_service import DBSyncService


class CoachRepository(BaseRepository):
    def __init__(self):
        super().__init__(Coach, "coach")

    def get_all_coaches_paginated(self, page, per_page, order_by=None, sort_order="asc"):
        return super().get_all_paginated(page, per_page, order_by, sort_order)

    def assign_coach_to_team(self, team_id, coach_id):
        try:
            team_coach = Team_Coach(team_id=team_id, coach_id=coach_id)
            return super().save(team_coach)
        except Exception as e:
            current_app.logger.error(f"Error assigning coach to team: {str(e)}")
            return None

    def remove_coach_from_team(self, team_id, coach_id):
        try:
            team_coach = Team_Coach.query.filter_by(team_id=team_id, coach_id=coach_id).first()
            if team_coach:
                return super().delete(team_coach.id)
            return False
        except Exception as e:
            current_app.logger.error(f"Error removing coach from team: {str(e)}")
            return False




    def create_coach(self, coach_data):
        try:
            new_coach = Coach(**coach_data)
            return super().save(new_coach)
        except Exception as e:
            current_app.logger.error(f"Error creating coach: {str(e)}")
            return None

    def update_coach(self, coach_id, coach_data):
        try:
            coach = super().get_by_id(coach_id)
            if not coach:
                return None

            for key, value in coach_data.items():
                if hasattr(coach, key):
                    setattr(coach, key, value)

            return super().update(coach)
        except Exception as e:
            current_app.logger.error(f"Error updating coach: {str(e)}")
            return None

    def delete_coach(self, coach_id):
        try:
            return super().delete(coach_id)
        except Exception as e:
            current_app.logger.error(f"Error deleting coach: {str(e)}")
            return False

    # In TeamCoachRepository:
    def get_coaches_team(self, team_id):
        """Get all team_coach records for a specific team"""
        try:
            # Get team_coach IDs for this team
            team_coaches_key = f"team:{team_id}:team_coaches"
            coach_ids = self.redis_service.get(team_coaches_key)

            if coach_ids is None:
                # If relationship data not in Redis, load from SQL
                self._sync_team_coaches()
                coach_ids = self.redis_service.get(team_coaches_key) or []

            # Get team_coach data
            team_coaches = []
            for tc_id in coach_ids:
                tc_data = self.redis_service.get(f"team_coach:{tc_id}")
                if tc_data:
                    team_coaches.append(self._deserialize_model(tc_data))

            return team_coaches
        except Exception as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            # SQL fallback
            return Team_Coach.query.filter_by(team_id=team_id).all()

    def get_coach_teams(self, coach_id):
        """Get all team_coach records for a specific coach"""
        try:
            coach_teams_key = f"coach:{coach_id}:team_coaches"
            team_coach_ids = self.redis_service.get(coach_teams_key)

            if team_coach_ids is None:
                self._sync_team_coaches()
                team_coach_ids = self.redis_service.get(coach_teams_key) or []

            team_coaches = []
            for tc_id in team_coach_ids:
                tc_data = self.redis_service.get(f"team_coach:{tc_id}")
                if tc_data:
                    team_coaches.append(self._deserialize_model(tc_data))

            return team_coaches
        except Exception as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            return Team_Coach.query.filter_by(coach_id=coach_id).all()

    def get_coaches_by_season(self, season_id):
        """Get all team_coach records for a specific season"""
        try:
            season_teams_key = f"season:{season_id}:team_coaches"
            team_coach_ids = self.redis_service.get(season_teams_key)

            if team_coach_ids is None:
                self._sync_team_coaches()
                team_coach_ids = self.redis_service.get(season_teams_key) or []

            team_coaches = []
            for tc_id in team_coach_ids:
                tc_data = self.redis_service.get(f"team_coach:{tc_id}")
                if tc_data:
                    team_coaches.append(self._deserialize_model(tc_data))

            return team_coaches
        except Exception as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            return Team_Coach.query.filter_by(season_id=season_id).all()

    def _sync_team_coaches(self):
        """Sync all team_coach relationships to Redis"""
        sync_service = DBSyncService()
        sync_service.sync_model(Team_Coach, "team_coach")
