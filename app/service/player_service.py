from flask import current_app

from app.repository.player_repository import PlayerRepository
from app.repository.season_repository import SeasonRepository
from app.model.player import Player


class Player_service:
    def __init__(self):
        self.season_repository = SeasonRepository()
        self.player_repository = PlayerRepository()


    def get_player_by_id(self, player_id):
        return self.season_repository.get_by_id(player_id)

    def get_player_by_team_season(self, team_id, season_id):
        try:
            return self.player_repository.get_players_by_team_season(team_id, season_id)
        except Exception as e:
            current_app.logger.error(f"Error getting players by team and season: {str(e)}")
            return None

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

    def change_player_team_season(self, player_id, old_team_id, new_team_id, season_id):
        try:
            return self.player_repository.change_player_team_season(player_id, old_team_id, new_team_id, season_id)
        except Exception as e:
            current_app.logger.error(f"Error changing player team: {str(e)}")