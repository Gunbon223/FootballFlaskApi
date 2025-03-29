from flask import current_app

from app.model.lineup import Lineup
from app.repository.base_repository import BaseRepository
from app.service.redis_service import RedisService

class LineupRepository(BaseRepository):
    def __init__(self):
        super().__init__(Lineup,"lineup")

    def get_match_players(self, match_id, team_id=None):
        """
        Get all players who played in a match, optionally filtered by team

        Args:
            match_id: ID of the match
            team_id: Optional team ID to filter players

        Returns:
            Dictionary with team IDs as keys and lists of player data as values
        """
        try:
            result = {}

            if team_id:
                teams = [team_id]
            else:
                match_data = self.redis_service.get(f"match:{match_id}")
                if not match_data:
                    return {}
                teams = [match_data["home_team_id"], match_data["away_team_id"]]

            for current_team_id in teams:
                players_key = f"match:{match_id}:team:{current_team_id}:players"
                player_keys = self.redis_service.get(players_key) or []

                team_data = self.redis_service.get(f"team:{current_team_id}")
                team_name = team_data["name"]
                total_players = len(player_keys)


                players_data = []
                for player_key in player_keys:
                    player_data = self.redis_service.get(player_key)
                    if not player_data:
                        continue

                    starting_lineup_key = f"match:{match_id}:team:{current_team_id}:starting_lineup"
                    starting_lineup = self.redis_service.get(starting_lineup_key) or []

                    # Get minutes played if available

                    players_data.append({
                        "player_id": player_data["id"],
                        "name": player_data["name"],
                        "position": player_data.get("position", ""),
                        "is_starting": player_key in starting_lineup,
                    })

                result[team_name] = {
                    "total_players": total_players,
                    "players": players_data
                }

            return result
        except Exception as e:
            current_app.logger.error(f"Error getting match players: {str(e)}")
            return {}

    def get_match_substitutions(self, match_id):
        """
        Get all substitutions in a match sorted by time
        """
        try:
            result = []
            redis_service = RedisService.get_instance()

            # Get match data to find teams
            match_data = redis_service.get(f"match:{match_id}")
            if not match_data:
                return []

            teams = [match_data["home_team_id"], match_data["away_team_id"]]

            # Process substitutions for each team
            for team_id in teams:
                team_data = redis_service.get(f"team:{team_id}")
                if not team_data:
                    continue

                # Get entry times (players coming on)
                entry_times_key = f"match:{match_id}:team:{team_id}:entry_times"
                entry_players = redis_service.get_from_sorted_set(entry_times_key, 0, -1, False)

                # Get corresponding scores (times) for each player
                entry_times = []
                for player in entry_players:
                    score = redis_service._redis_client.zscore(entry_times_key, player)
                    if score is not None:
                        entry_times.append((player, score))

                # Get exit times (players going off)
                exit_times_key = f"match:{match_id}:team:{team_id}:exit_times"
                exit_players = redis_service.get_from_sorted_set(exit_times_key, 0, -1, False)

                # Get corresponding scores (times) for each player
                exit_times = []
                for player in exit_players:
                    score = redis_service._redis_client.zscore(exit_times_key, player)
                    if score is not None:
                        exit_times.append((player, score))

                # Get starting lineup
                starting_lineup_key = f"match:{match_id}:team:{team_id}:starting_lineup"
                starting_lineup = redis_service.get(starting_lineup_key) or []

                # Process players who exited but weren't in starting lineup (were substituted in, then out)
                for player_key, entry_time in entry_times:
                    # Skip starting players (they're handled separately below)
                    if player_key in starting_lineup:
                        continue

                    player_data = redis_service.get(player_key)
                    if not player_data:
                        continue

                    # Find closest exit time before this entry
                    closest_exit = None
                    closest_exit_player = None

                    for exit_player_key, exit_time in exit_times:
                        if exit_time <= entry_time and (closest_exit is None or exit_time > closest_exit):
                            exit_player_data = redis_service.get(exit_player_key)
                            if exit_player_data:
                                closest_exit = exit_time
                                closest_exit_player = exit_player_data

                    if closest_exit_player:
                        result.append({
                            "minute": int(entry_time // 60),
                            "team_name": team_data["name"],
                            "player_in": {
                                "id": player_data["id"],
                                "name": player_data["name"]
                            },
                            "player_out": {
                                "id": closest_exit_player["id"],
                                "name": closest_exit_player["name"]
                            }
                        })

                # Process starting lineup players who were substituted out
                for player_key in starting_lineup:
                    # Find if this starting player was substituted out
                    for exit_player_key, exit_time in exit_times:
                        if exit_player_key == player_key:
                            exit_player_data = redis_service.get(exit_player_key)
                            print(exit_player_data)

                            # Find who replaced this player (closest entry after this exit)
                            closest_entry = None
                            closest_entry_player = None

                            for entry_player_key, entry_time in entry_times:
                                if entry_player_key not in starting_lineup and entry_time >= exit_time and (closest_entry is None or entry_time < closest_entry):
                                    entry_player_data = redis_service.get(entry_player_key)
                                    if entry_player_data:
                                        closest_entry = entry_time
                                        closest_entry_player = entry_player_data

                            if closest_entry_player:
                                result.append({
                                    "minute": int(exit_time // 60),
                                    "team_name": team_data["name"],
                                    "player_in": {
                                        "id": closest_entry_player["id"],
                                        "name": closest_entry_player["name"]
                                    },
                                    "player_out": {
                                        "id": exit_player_data["id"],
                                        "name": exit_player_data["name"]
                                    }
                                })

            # Sort substitutions by minute
            result.sort(key=lambda x: x["minute"])
            return result

        except Exception as e:
            current_app.logger.error(f"Error getting match substitutions: {str(e)}")
            return []