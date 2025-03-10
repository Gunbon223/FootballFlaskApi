from flask import current_app
from app.repository.base_repository import BaseRepository
from app.model.team import Team


class TeamRepository(BaseRepository):
    def __init__(self):
        super().__init__(Team, "team")

    def get_all_teams_paginated(self, page, per_page, order_by=None, sort_order="asc"):
        return super().get_all_paginated(page, per_page, order_by, sort_order)
