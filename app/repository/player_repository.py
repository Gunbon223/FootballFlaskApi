from flask import current_app
from app.repository.base_repository import BaseRepository
from app.model.player import Player, PlayerTeamSeason


class PlayerRepository(BaseRepository):
    def __init__(self):
        super().__init__(Player, "player")

    def get_player_by_id(self, player_id):
        """Get a player by their ID"""
        return self.get_by_id(player_id)

    def get_players_by_team_season(self, team_id, season_id):
        """Get all players for a team in a season"""
        try:
            player_keys = self.redis_service.get(f"team:{team_id}:season:{season_id}:players")
            if not player_keys:
                return []
            players = []
            for player_key in player_keys:
                    player = self.get(player_key)
                    if player:
                        player_dict = {
                            'id': player.id,
                            'name': player.name,
                            'nationality': player.nationality,
                            'position': player.position,
                        }
                        players.append(player_dict)

            return players
        except Exception as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            return []








