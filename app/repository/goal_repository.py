from flask import current_app

from app.model.goal import Goal
from app.repository.base_repository import BaseRepository
from app.service.redis_service import RedisService


class GoalRepository(BaseRepository):
    def __init__(self):
        super().__init__(Goal, "goal")

    def get_match_goals(self, match_id):
        """
        Get all goals in a match sorted by time
        """
        try:
            result = []
            redis_service = RedisService.get_instance()

            # Get match data
            match_data = redis_service.get(f"match:{match_id}")
            if not match_data:
                return []

            # Get goals from sorted set
            match_goals_key = f"match:{match_id}:goals"
            goals = redis_service.get_all_sorted_set_with_scores(match_goals_key)
            for player_key, goal_time in goals:
                player_data = redis_service.get(player_key)
                if not player_data:
                    continue

                # Find which team the player belongs to
                home_players_key = f"match:{match_id}:team:{match_data['home_team_id']}:players"
                away_players_key = f"match:{match_id}:team:{match_data['away_team_id']}:players"

                home_players = redis_service.get(home_players_key) or []
                away_players = redis_service.get(away_players_key) or []

                if player_key in home_players:
                    team_id = match_data['home_team_id']
                elif player_key in away_players:
                    team_id = match_data['away_team_id']
                else:
                    continue

                team_data = redis_service.get(f"team:{team_id}")

                result.append({
                    "minute": int(goal_time),
                    "team_name": team_data["name"],
                    "scorer": {
                        "id": player_data["id"],
                        "name": player_data["name"]
                    }
                })

            # Sort goals by minute
            result.sort(key=lambda x: x["minute"])
            return result

        except Exception as e:
            current_app.logger.error(f"Error getting match goals: {str(e)}")
            return []

    def get_player_season_goals(self, player_id, season_id):
        """
        Get a player's goals in a specific season
        """
        try:
            redis_service = RedisService.get_instance()
            goals_key = f"player:{player_id}:season:{season_id}:goals"
            return redis_service.get(goals_key) or 0
        except Exception as e:
            current_app.logger.error(f"Error getting player season goals: {str(e)}")
            return 0

    def get_player_career_goals(self, player_id):
        """
        Get a player's career goals
        """
        try:
            redis_service = RedisService.get_instance()
            goals_key = f"player:{player_id}:career:goals"
            return redis_service.get(goals_key) or 0
        except Exception as e:
            current_app.logger.error(f"Error getting player career goals: {str(e)}")
            return 0

    def get_season_top_scorers(self, season_id, limit=10):
        """
        Get top scorers in a season
        """
        try:
            result = []
            redis_service = RedisService.get_instance()

            # Get top scorers from sorted set (high to low)
            scorers_key = f"season:{season_id}:top_scorers"
            top_scorers = redis_service.get_all_sorted_set_with_scores(scorers_key)

            # Reverse to get highest scorers first
            top_scorers.sort(key=lambda x: x[1], reverse=True)

            # Limit the results
            top_scorers = top_scorers[:limit]

            for player_key, goals in top_scorers:
                player_data = redis_service.get(player_key)
                if not player_data:
                    continue

                result.append({
                    "player_id": player_data["id"],
                    "name": player_data["name"],
                    "goals": int(goals)
                })

            return result

        except Exception as e:
            current_app.logger.error(f"Error getting season top scorers: {str(e)}")
            return []