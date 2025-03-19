from flask import current_app
from app.repository.team_repository import TeamRepository
# from app.repository. import TeamCoachRepository
from app.model.team import Team

class TeamService:
    def __init__(self):
        self.team_repository = TeamRepository()
        # self.team_coach_repository = TeamCoachRepository()

    def get_all_teams_paginated(self, page=1, per_page=10, order_by='id', sort_order="asc"):

        return self.team_repository.get_all_teams_paginated(page, per_page,order_by, sort_order)

    def get_team_by_id(self, team_id):
        """Get a team by ID"""
        return self.team_repository.get_by_id(team_id)


    def create_team(self, team_data):
        """Create a new team"""
        try:
            new_team = Team(**team_data)
            return self.team_repository.save(new_team)
        except Exception as e:
            current_app.logger.error(f"Error creating team: {str(e)}")
            return None

    def update_team(self, team_id, team_data):
        """Update an existing team"""
        try:
            team = self.team_repository.get_by_id(team_id)
            if not team:
                return None

            # Update team attributes
            for key, value in team_data.items():
                if hasattr(team, key):
                    setattr(team, key, value)

            return self.team_repository.update(team)
        except Exception as e:
            current_app.logger.error(f"Error updating team: {str(e)}")
            return None

    def delete_team(self, team_id):
        """Delete a team"""
        try:
            return self.team_repository.delete(team_id)
        except Exception as e:
            current_app.logger.error(f"Error deleting team: {str(e)}")
            return False







