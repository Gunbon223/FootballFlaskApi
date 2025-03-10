from flask import current_app
from app.repository.base_repository import BaseRepository
from app.model.season import Season

class SeasonRepository(BaseRepository):
    def __init__(self):
        super().__init__(Season, "season")

    def get_all_seasons_paginated(self, page, per_page, order_by=None, sort_order="asc"):
        return super().get_all_paginated(page, per_page, order_by, sort_order)

