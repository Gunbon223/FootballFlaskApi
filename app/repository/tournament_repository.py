from datetime import datetime, date

from flask import current_app

from app.model.season import Season
from app.repository.base_repository import BaseRepository
from app.model.tournament import Tournament


class TournamentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Tournament, "tournament")

    def get_all_tournaments_paginated(self, page, per_page, order_by=None, sort_order="asc"):
        return super().get_all_paginated(page, per_page, order_by, sort_order)

    def get_tournament_seasons(self, tournament_id, page=1, per_page=None, order_by=None, sort_order="asc"):
        try:
            tournament_seasons_key = f"tournament:{tournament_id}:seasons"
            season_ids = self.redis_service.get(tournament_seasons_key)

            if season_ids is None:
                self._load_tournament_seasons_to_redis(tournament_id)
                season_ids = self.redis_service.get(tournament_seasons_key) or []

            total = len(season_ids)
            if per_page:
                offset = (page - 1) * per_page
                page_ids = season_ids[offset:offset+per_page]
            else:
                page_ids = season_ids

            seasons = []
            for season_id in page_ids:
                season_data = self.redis_service.get(f"season:{season_id}")
                if season_data:
                    seasons.append(season_data)
            return seasons, total
        except Exception as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            seasons, total = self._get_tournament_seasons_from_sql(tournament_id, page, per_page, order_by, sort_order)
            seasons_data = [self._serialize_model(season) for season in seasons]
            return seasons_data, total


    def _load_tournament_seasons_to_redis(self, tournament_id):
        """Load tournament-season relationships to Redis from SQL"""
        try:
            seasons = Season.query.filter_by(tournament_id=tournament_id).all()
            season_ids = [season.id for season in seasons]

            # Store relationship
            self.redis_service.set(f"tournament:{tournament_id}:seasons", season_ids)

            # Make sure individual seasons are cached
            for season in seasons:
                redis_key = f"season:{season.id}"
                if not self.redis_service.get(redis_key):
                    data = {c.name: getattr(season, c.name) for c in season.__table__.columns}
                    self.redis_service.set(redis_key, data)

            return True
        except Exception as e:
            current_app.logger.error(f"Error loading tournament seasons: {str(e)}")
            return False

    def _get_tournament_seasons_from_sql(self, tournament_id, page, per_page, order_by, sort_order):
        """SQL fallback for tournament seasons"""
        query = Season.query.filter_by(tournament_id=tournament_id)

        if order_by and hasattr(Season, order_by):
            column = getattr(Season, order_by)
            if sort_order == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

        total = query.count()

        if per_page:
            offset = (page - 1) * per_page
            seasons = query.limit(per_page).offset(offset).all()
        else:
            seasons = query.all()

        return seasons, total

    def get_recent_seasons(self, tournament_id, sort_order="desc", page=1, per_page=5):
        """Get most recent seasons for a tournament"""
        sorted_key = f"tournament:{tournament_id}:seasons_sorted"
        total = self.redis_service.get_sorted_set_length(sorted_key)

        if not total:
            self._load_tournament_seasons_to_redis(tournament_id)
            total = self.redis_service.get_sorted_set_length(sorted_key)
            if not total:
                return [], 0

        start = (page - 1) * per_page
        end = start + per_page - 1

        if sort_order == "asc":
            recent_ids = self.redis_service.get_from_sorted_set(sorted_key, start, end, desc=True)
        else:
            recent_ids = self.redis_service.get_from_sorted_set(sorted_key, start, end, desc=False)


        seasons = []
        for season_id in recent_ids:
            season_data = self.redis_service.get(f"season:{int(season_id)}")
            if season_data:
                seasons.append(season_data)

        return seasons, total
