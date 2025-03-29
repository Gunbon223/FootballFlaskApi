from flask import Blueprint, request, jsonify, current_app

from app.model.match import Match
from app.repository.base_repository import BaseRepository


class MatchRepository(BaseRepository):
    def __init__(self):
        super().__init__(Match,"match")

    def get_all_matches_paginated(self, page, per_page, order_by=None, sort_order="asc"):
        return super().get_all_paginated(page, per_page, order_by, sort_order)

    def get_match_by_id(self, match_id):
        return super().get_by_id(match_id)

    def create_match(self, match_data):
        super().save(match_data)


    def update_match(self, match_id, match_data):
        match = super().get_by_id(match_id)
        if not match:
            return None

        for key, value in match_data.items():
            if hasattr(match, key):
                setattr(match, key, value)

        return super().update(match)

    def delete_match(self, match_id):
        return super().delete(match_id)

    def get_recent_matches_of_team_season(self, team_id, season_id, sort_order="asc", page=1, per_page=5):
        try:
            match_keys = f'team:{team_id}:season:{season_id}:recent_matches'
            total = self.redis_service.get_sorted_set_length(match_keys)

            # Early return if no matches found
            if total == 0:
                return [], 0

            start = (page - 1) * per_page
            end = start + per_page - 1

            if sort_order == "asc":
                matches_list = self.redis_service.get_from_sorted_set(match_keys, start, end,True)
            else:
                matches_list = self.redis_service.get_from_sorted_set(match_keys, start, end,False)

            data = []
            for match in matches_list:
                match_data = self.redis_service.get(match)
                if not match_data:
                    current_app.logger.warning(f"No data found for match key: {match}")
                    continue

                home_team_data = self.redis_service.get(f"team:{match_data['home_team_id']}")
                away_team_data = self.redis_service.get(f"team:{match_data['away_team_id']}")

                if not home_team_data or not away_team_data:
                    current_app.logger.warning(f"Missing team data for match: {match}")
                    continue

                data.append({
                    "match_id": match_data["id"],
                    "home_team_name": home_team_data["name"],
                    "away_team_name": away_team_data["name"],
                    "home_score": match_data["home_score"],
                    "away_score": match_data["away_score"],
                    "match_start_date": match_data["match_start_date"],
                    "match_end_date": match_data["match_end_date"]

                })

            return data, total
        except Exception as e:
            current_app.logger.error(f"Error getting recent matches for team {team_id}, season {season_id}: {str(e)}")
            return [], 0

    def get_recent_matches_of_team(self, team_id, sort_order="asc", page=1, per_page=5):
        try:
            match_keys = f'team:{team_id}:recent_matches'
            total = self.redis_service.get_sorted_set_length(match_keys)

            # Early return if no matches found
            if total == 0:
                return [], 0

            start = (page - 1) * per_page
            end = start + per_page - 1

            if sort_order == "asc":
                matches_list = self.redis_service.get_from_sorted_set(match_keys, start, end, True)
            else:
                matches_list = self.redis_service.get_from_sorted_set(match_keys, start, end, False)

            data = []
            for match in matches_list:
                match_data = self.redis_service.get(match)
                if not match_data:
                    current_app.logger.warning(f"No data found for match key: {match}")
                    continue

                home_team_data = self.redis_service.get(f"team:{match_data['home_team_id']}")
                away_team_data = self.redis_service.get(f"team:{match_data['away_team_id']}")

                if not home_team_data or not away_team_data:
                    current_app.logger.warning(f"Missing team data for match: {match}")
                    continue

                data.append({
                    "match_id": match_data["id"],
                    "home_team_name": home_team_data["name"],
                    "away_team_name": away_team_data["name"],
                    "home_score": match_data["home_score"],
                    "away_score": match_data["away_score"],
                    "match_start_date": match_data["match_start_date"],
                    "match_end_date": match_data["match_end_date"]
                })

            return data, total
        except Exception as e:
            current_app.logger.error(f"Error getting recent matches for team {team_id}: {str(e)}")
            return [], 0

    def get_matches_by_round(self, season_id, round_id, sort_order="asc", page=1, per_page=5):
        try:
            match_keys = f'season:{season_id}:round:{round_id}:matches'
            total = self.redis_service.get_sorted_set_length(match_keys)

            if total == 0:
                return [], 0

            start = (page - 1) * per_page
            end = start + per_page - 1

            if sort_order == "asc":
                matches_list = self.redis_service.get_from_sorted_set(match_keys, start, end, True)
            else:
                matches_list = self.redis_service.get_from_sorted_set(match_keys, start, end, False)

            data = []
            for match in matches_list:
                match_data = self.redis_service.get(match)
                if not match_data:
                    current_app.logger.warning(f"No data found for match key: {match}")
                    continue

                home_team_data = self.redis_service.get(f"team:{match_data['home_team_id']}")
                away_team_data = self.redis_service.get(f"team:{match_data['away_team_id']}")
                round_data = self.redis_service.get(f"round:{round_id}")
                if not home_team_data or not away_team_data:
                    current_app.logger.warning(f"Missing team data for match: {match}")
                    continue

                data.append({
                    "match_id": match_data["id"],
                    "round_name": round_data["round_number"],
                    "round_finished": round_data["is_finished"],
                    "round_date": round_data["round_date"],
                    "home_team_name": home_team_data["name"],
                    "away_team_name": away_team_data["name"],
                    "home_score": match_data["home_score"],
                    "away_score": match_data["away_score"],
                    "match_start_date": match_data["match_start_date"],
                    "match_end_date": match_data["match_end_date"]
                })

            return data, total
        except Exception as e:
            current_app.logger.error(f"Error getting matches for season {season_id}, round {round_id}: {str(e)}")
            return [], 0
