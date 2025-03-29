from app.repository.lineup_repository import LineupRepository


class LineupService:
    def __init__(self):
        self.lineup_repository = LineupRepository()

    def get_match_players(self, match_id, team_id=None):
        return self.lineup_repository.get_match_players(match_id, team_id)

    def get_match_substitutions(self, match_id):
        return self.lineup_repository.get_match_substitutions(match_id)
