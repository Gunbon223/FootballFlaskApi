from flask import current_app
from app.repository.base_repository import BaseRepository
from app.model.team_season_ranking import Team_Season_Ranking
from app.service.db_sync_service import DBSyncService


class TeamSeasonRankingRepository(BaseRepository):
    def  __init__(self):
        super().__init__(Team_Season_Ranking, "team_season_ranking")

    def get_leaderboard(self, season_id, sort_by="ranking"):
        """Get full leaderboard for a season from Redis"""
        try:
            # Choose the appropriate sorted list key based on sort preference
            if sort_by == "points":
                sorted_key = f"season:{season_id}:leaderboard_by_points"
            else:
                sorted_key = f"season:{season_id}:sorted_leaderboard"

            # Get sorted ranking IDs
            ranking_ids = self.redis_service.get(sorted_key)

            if ranking_ids is None:
                # If sorted list doesn't exist in Redis, sync from SQL
                sync_service = DBSyncService()
                sync_service.sync_model(Team_Season_Ranking, "team_season_ranking")
                self.update_leaderboard_sorted_list(season_id)
                ranking_ids = self.redis_service.get(sorted_key) or []

            # Get full ranking data with team information
            leaderboard = []
            for ranking_id in ranking_ids:
                ranking_data = self.redis_service.get(f"team_season_ranking:{ranking_id}")
                if ranking_data:
                    # Get associated team data
                    team_data = self.redis_service.get(f"team:{ranking_data.get('team_id')}")
                    if team_data:
                        # Combine ranking data with team data
                        entry = ranking_data.copy()
                        entry['team_name'] = team_data.get('name')
                        entry['team_country'] = team_data.get('country')
                        leaderboard.append(entry)

            return leaderboard

        except Exception as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            # Fall back to SQL
            return self._get_leaderboard_from_sql(season_id, sort_by)

    def get_team_rankings(self, team_id):
        """Get all rankings for a specific team"""
        try:
            team_rankings_key = f"team:{team_id}:rankings"
            ranking_ids = self.redis_service.get(team_rankings_key)

            if ranking_ids is None:
                # If relationship data not in Redis, sync from SQL
                sync_service = DBSyncService()
                sync_service.sync_model(Team_Season_Ranking, "team_season_ranking")
                ranking_ids = self.redis_service.get(team_rankings_key) or []

            # Get ranking data
            rankings = []
            for ranking_id in ranking_ids:
                ranking_data = self.redis_service.get(f"team_season_ranking:{ranking_id}")
                if ranking_data:
                    # Get associated season data
                    season_data = self.redis_service.get(f"season:{ranking_data.get('season_id')}")
                    if season_data:
                        # Combine ranking data with season info
                        entry = ranking_data.copy()
                        entry['season_name'] = season_data.get('name')
                        rankings.append(entry)

            return rankings

        except Exception as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            return Team_Season_Ranking.query.filter_by(team_id=team_id).all()

    def _get_leaderboard_from_sql(self, season_id, sort_by="ranking"):
        """SQL fallback for leaderboard"""
        query = Team_Season_Ranking.query.filter_by(season_id=season_id)

        if sort_by == "points":
            query = query.order_by(
                Team_Season_Ranking.points.desc(),
                Team_Season_Ranking.goal_difference.desc(),
                Team_Season_Ranking.goals_for.desc()
            )
        else:
            query = query.order_by(Team_Season_Ranking.ranking)

        return query.all()

    def update_leaderboard_sorted_list(self, season_id):
        """Create a sorted leaderboard in Redis"""
        try:
            # Get all ranking IDs for this season
            rankings_key = f"season:{season_id}:rankings"
            ranking_ids = self.redis_service.get(rankings_key) or []

            # Get the actual ranking records
            rankings_data = []
            for ranking_id in ranking_ids:
                data = self.redis_service.get(f"team_season_ranking:{ranking_id}")
                if data:
                    rankings_data.append(data)

            # Sort by ranking field (lower number is better)
            sorted_rankings = sorted(rankings_data, key=lambda x: x.get('ranking', 999))
            sorted_ids = [r.get('id') for r in sorted_rankings]

            # Store sorted list
            self.redis_service.set(f"season:{season_id}:sorted_leaderboard", sorted_ids)

            # Also sort by points (higher is better)
            sorted_by_points = sorted(rankings_data,
                                      key=lambda x: (x.get('points', 0),
                                                     x.get('goal_difference', 0),
                                                     x.get('goals_for', 0)),
                                      reverse=True)
            sorted_points_ids = [r.get('id') for r in sorted_by_points]

            # Store points-based leaderboard
            self.redis_service.set(f"season:{season_id}:leaderboard_by_points", sorted_points_ids)

            return True
        except Exception as e:
            current_app.logger.error(f"Error updating leaderboard list: {str(e)}")
            return False