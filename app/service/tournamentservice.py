from flask import current_app
from app.repository.tournament_repository import TournamentRepository
from app.model.tournament import Tournament

class Tournament_service:
    def __init__(self):
        self.tournament_repository = TournamentRepository()

    def get_all_tournaments_paginated(self, page=1, per_page=10, order_by='id', sort_order="asc"):
        return self.tournament_repository.get_all_tournaments_paginated(page, per_page, order_by, sort_order)

    def get_tournament_by_id(self, tournament_id):
        return self.tournament_repository.get_by_id(tournament_id)

    def create_tournament(self, tournament_data):
        try:
            new_tournament = Tournament(**tournament_data)
            return self.tournament_repository.save(new_tournament)
        except Exception as e:
            current_app.logger.error(f"Error creating tournament: {str(e)}")
            return None

    def update_tournament(self, tournament_id, tournament_data):
        try:
            tournament = self.tournament_repository.get_by_id(tournament_id)
            if not tournament:
                return None

            for key, value in tournament_data.items():
                if hasattr(tournament, key):
                    setattr(tournament, key, value)

            return self.tournament_repository.update(tournament)
        except Exception as e:
            current_app.logger.error(f"Error updating tournament: {str(e)}")
            return None

    def delete_tournament(self, tournament_id):
        try:
            return self.tournament_repository.delete(tournament_id)
        except Exception as e:
            current_app.logger.error(f"Error deleting tournament: {str(e)}")
            return False

    def get_tournament_seasons(self, tournament_id, page=1, per_page=5, sort_order="desc"):
        return self.tournament_repository.get_recent_seasons(
            tournament_id=tournament_id,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )

