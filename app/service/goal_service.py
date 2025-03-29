from app.repository.goal_repository import GoalRepository


class GoalService:
    def __init__(self):
        self.goal_repository = GoalRepository()

    def get_match_goals(self, match_id):
        return self.goal_repository.get_match_goals(match_id)

    def get_player_season_goals(self, player_id, season_id):
        return self.goal_repository.get_player_season_goals(player_id, season_id)

    def get_player_career_goals(self, player_id):
        return self.goal_repository.get_player_career_goals(player_id)

    def get_season_top_scorers(self, season_id, limit=10):
        return self.goal_repository.get_season_top_scorers(season_id, limit)