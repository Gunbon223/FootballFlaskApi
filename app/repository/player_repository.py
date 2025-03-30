from flask import current_app
from app.repository.base_repository import BaseRepository
from app.model.player import Player, PlayerTeamSeason
from appdb import db


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

    def create_player(self, player_data):
        """Create a new player"""
        try:
            new_player = Player(**player_data)
            return self.save(new_player)
        except Exception as e:
            current_app.logger.error(f"Error creating player: {str(e)}")
            return None

    def update_player(self, player_id, player_data):
        """Update an existing player"""
        try:
            player = self.get_by_id(player_id)
            if not player:
                return None

            # Update player attributes
            for key, value in player_data.items():
                if hasattr(player, key):
                    setattr(player, key, value)

            return self.update(player)
        except Exception as e:
            current_app.logger.error(f"Error updating player: {str(e)}")
            return None



    def change_player_team_season(self, player_id, old_team_id, new_team_id, season_id):
        """Move a player from one team to another in a season"""
        try:
            # Format the key for Redis
            player_key = f"player:{player_id}"

            # 1. Remove player from old team in Redis
            old_team_key = f"team:{old_team_id}:season:{season_id}:players"
            self.redis_service.remove_from_sorted_set(old_team_key, player_key)

            # 2. Add player to new team in Redis
            new_team_key = f"team:{new_team_id}:season:{season_id}:players"
            self.redis_service.add_to_sorted_set(new_team_key, player_key, 0)

            # 3. Update SQL database
            player_team_season = PlayerTeamSeason.query.filter_by(
                player_id=player_id,
                team_id=old_team_id,
                season_id=season_id
            ).first()

            if player_team_season:
                # Update existing record
                player_team_season.team_id = new_team_id
                db.session.commit()
            else:
                # Create new record if not found
                new_record = PlayerTeamSeason(
                    player_id=player_id,
                    team_id=new_team_id,
                    season_id=season_id
                )
                db.session.add(new_record)
                db.session.commit()

            return True
        except Exception as e:
            current_app.logger.error(f"Error changing player team: {str(e)}")
            db.session.rollback()
            return False








