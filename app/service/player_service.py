from flask import current_app
from app.repository.season_repository import SeasonRepository
from app.model.player import Player


class Playerservice:
    def __init__(self):
        self.season_repository = SeasonRepository()

    def get_all_players_paginated(self, page=1, per_page=10, order_by='id', sort_order="asc"):

        return self.season_repository.get_all_seasons_paginated(page, per_page, order_by, sort_order)

    def get_player_by_id(self, player_id):
        return self.season_repository.get_by_id(player_id)

    def create_player(self, player_data):
        try:
            new_player = Player(**player_data)
            return self.season_repository.save(new_player)
        except Exception as e:
            current_app.logger.error(f"Error creating player: {str(e)}")
            return None

    def update_player(self, player_id, player_data):
        try:
            player = self.season_repository.get_by_id(player_id)
            if not player:
                return None

            # Update player attributes
            for key, value in player_data.items():
                if hasattr(player, key):
                    setattr(player, key, value)

            return self.season_repository.update(player)
        except Exception as e:
            current_app.logger.error(f"Error updating player: {str(e)}")
            return None

    def delete_player(self, player_id):
        try:
            return self.season_repository.delete(player_id)
        except Exception as e:
            current_app.logger.error(f"Error deleting player: {str(e)}")
            return False