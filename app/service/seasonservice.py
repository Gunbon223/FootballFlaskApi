from flask import current_app
from app.repository.season_repository import SeasonRepository
from app.model.season import Season


class SeasonService:
    def __init__(self):
        self.season_repository = SeasonRepository()

    def get_all_seasons_paginated(self, page=1, per_page=10, order_by='id', sort_order="asc"):

        return self.season_repository.get_all_seasons_paginated(page, per_page, order_by, sort_order)

    def get_season_by_id(self, season_id):
        return self.season_repository.get_by_id(season_id)

    def create_season(self, season_data):
        try:
            new_season = Season(**season_data)
            return self.season_repository.save(new_season)
        except Exception as e:
            current_app.logger.error(f"Error creating season: {str(e)}")
            return None

    def update_season(self, season_id, season_data):
        try:
            season = self.season_repository.get_by_id(season_id)
            if not season:
                return None

            # Update season attributes
            for key, value in season_data.items():
                if hasattr(season, key):
                    setattr(season, key, value)

            return self.season_repository.update(season)
        except Exception as e:
            current_app.logger.error(f"Error updating season: {str(e)}")
            return None

    def delete_season(self, season_id):
        try:
            return self.season_repository.delete(season_id)
        except Exception as e:
            current_app.logger.error(f"Error deleting season: {str(e)}")
            return False
