from flask import Blueprint, request, jsonify
from app.service.team_service import TeamService
from app.utils.response import create_response

team_route_bp = Blueprint('team', __name__)
team_service = TeamService()

@team_route_bp.route('/teams', methods=['GET'])
def get_all_teams():
    # Get pagination parameters from request
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    order_by = request.args.get('order_by')
    sort_order = request.args.get('sort_order', 'asc')

    # Get paginated teams from service
    teams, total = team_service.get_all_teams_paginated(
        page=page,
        per_page=per_page,
        order_by=order_by,
        sort_order=sort_order
    )
    teams_dict = [team.to_dict() for team in teams]

    # Create metadata for pagination
    pagination = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'order_by': order_by,
        'sort_order': sort_order
    }

    return create_response(
        teams_dict,
        "Teams found",
        200,
        True,
        pagination=pagination
    )
@team_route_bp.route('/teams/<int:team_id>', methods=['GET'])
def get_team_by_id(team_id):
    team = team_service.get_team_by_id(team_id)
    if team:
        return create_response(team.to_dict(), "Team found", 200, True)
    return create_response( None, "Team not found", 404, False)

@team_route_bp.route('/teams', methods=['POST'])
def create_team():
    team_data = request.json
    new_team = team_service.create_team(team_data)
    if new_team:
        return create_response(data=new_team.to_dict(), status=201)
    return create_response(message="Error creating team", status=400)

@team_route_bp.route('/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    team_data = request.json
    updated_team = team_service.update_team(team_id, team_data)
    if updated_team:
        return create_response(data=updated_team.to_dict())
    return create_response(message="Error updating team", status=400)

@team_route_bp.route('/teams/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    success = team_service.delete_team(team_id)
    if success:
        return create_response(message="Team deleted")
    return create_response(message="Error deleting team", status=400)

# @team_route_bp.route('/teams/', methods=['GET'])


