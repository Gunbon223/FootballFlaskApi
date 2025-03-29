from flask import current_app
from app.repository.match_repository import MatchRepository

class MatchService:
    def __init__(self):
        self.match_repository = MatchRepository()

    def get_all_matches_paginated(self, page=1, per_page=10, order_by='id', sort_order="asc"):
        return self.match_repository.get_all_matches_paginated(page, per_page, order_by, sort_order)

    def get_match_by_id(self, match_id):
        return self.match_repository.get_by_id(match_id)

    def create_match(self, match_data):
        try:
            return self.match_repository.save(match_data)
        except Exception as e:
            current_app.logger.error(f"Error creating match: {str(e)}")
            return None

    def update_match(self, match_id, match_data):
        try:
            return self.match_repository.update(match_id, match_data)
        except Exception as e:
            current_app.logger.error(f"Error updating match: {str(e)}")
            return None

    def delete_match(self, match_id):
        return self.match_repository.delete(match_id)

    def get_recent_matches_of_team_season(self, team_id, season_id, sort_order="asc", page=1, per_page=5):
        return self.match_repository.get_recent_matches_of_team_season(team_id, season_id, sort_order, page, per_page)

    def get_recent_matches_of_team(self, team_id, sort_order="asc", page=1, per_page=5):
        return self.match_repository.get_recent_matches_of_team(team_id, sort_order, page, per_page)

    def get_matches_by_round(self, season_id, round_id, sort_order="asc", page=1, per_page=5):
        return self.match_repository.get_matches_by_round(season_id, round_id, sort_order, page, per_page)

