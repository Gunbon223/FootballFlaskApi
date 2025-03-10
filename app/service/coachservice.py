from flask import current_app
from app.repository.coach_repository import CoachRepository
from app.model.coach import Coach

class Coachsevice:

    def __init__(self):
        self.coach_repository = CoachRepository()

    def get_all_coaches_paginated(self, page=1, per_page=10, order_by='id', sort_order="asc"):
        return self.coach_repository.get_all_coaches_paginated(page, per_page, order_by, sort_order)

    def get_coach_by_id(self, coach_id):
        return self.coach_repository.get_by_id(coach_id)

    def create_coach(self, coach_data):
        try:
            new_coach = Coach(**coach_data)
            return self.coach_repository.save(new_coach)
        except Exception as e:
            current_app.logger.error(f"Error creating coach: {str(e)}")
            return None

    def update_coach(self, coach_id, coach_data):
        try:
            coach = self.coach_repository.get_by_id(coach_id)
            if not coach:
                return None

            for key, value in coach_data.items():
                if hasattr(coach, key):
                    setattr(coach, key, value)

            return self.coach_repository.update(coach)
        except Exception as e:
            current_app.logger.error(f"Error updating coach: {str(e)}")
            return None

    def delete_coach(self, coach_id):
        return self.coach_repository.delete(coach_id)

    def get_coach_teams(self, coach_id):
        return self.coach_repository.get_coach_teams(coach_id)

    def get_coach_seasons(self, coach_id):
        return self.coach_repository.get_coaches_by_season(coach_id)

    def get_coaches_team(self, team_id):
        return self.coach_repository.get_coaches_team(team_id)

    def assign_coach_to_team(self, team_id, coach_id):
        return self.coach_repository.assign_coach_to_team(team_id, coach_id)


