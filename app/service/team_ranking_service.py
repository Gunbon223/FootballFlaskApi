from flask import current_app
from app.repository.team_repository import TeamRepository
# from app.repository. import TeamCoachRepository
from app.repository.team_ss_ranking_repository import TeamSeasonRankingRepository
from app.model.team import Team

class TeamRankingService:
    def __init__(self):
        self.team_ss_ranking_repository = TeamSeasonRankingRepository()


    def get_team_ranking(self, team_id):
        """Get a team's ranking"""
        return self.team_ss_ranking_repository.get_team_rankings(team_id)

    def get_leaderboard(self, season_id,sort_order):
        """Get full leaderboard for a season"""
        return self.team_ss_ranking_repository.get_leaderboard(season_id,sort_order)
