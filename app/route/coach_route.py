from flask import Blueprint, request, jsonify
from app.service.coachservice import Coachsevice
from app.utils.response import create_response

coach_route_bp = Blueprint('coach', __name__)
coach_service = Coachsevice()

@coach_route_bp.route('/coaches', methods=['GET'])
def get_all_coaches():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    order_by = request.args.get('order_by')
    sort_order = request.args.get('sort_order', 'asc')

    coaches, total = coach_service.get_all_coaches_paginated(
        page=page,
        per_page=per_page,
        order_by=order_by,
        sort_order=sort_order
    )
    coaches_dict = [coach.to_dict() for coach in coaches]

    pagination = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'order_by': order_by,
        'sort_order': sort_order
    }

    return create_response(
        coaches_dict,
        "Coaches found",
        200,
        True,
        pagination=pagination
    )


@coach_route_bp.route('/coaches/<int:coach_id>', methods=['GET'])
def get_coach_by_id(coach_id):
    coach = coach_service.get_coach_by_id(coach_id)
    if coach:
        return create_response(coach.to_dict(), "Coach found", 200, True)
    return create_response(None, "Coach not found", 404, False)

@coach_route_bp.route('/coaches', methods=['POST'])
def create_coach():
    coach_data = request.json
    new_coach = coach_service.create_coach(coach_data)
    if new_coach:
        return create_response(data=new_coach.to_dict(), status=201)
    return create_response(message="Error creating coach", status=400)

@coach_route_bp.route('/coaches/<int:coach_id>', methods=['PUT'])
def update_coach(coach_id):
    coach_data = request.json
    updated_coach = coach_service.update_coach(coach_id, coach_data)
    if updated_coach:
        return create_response(data=updated_coach.to_dict(), status=200)
    return create_response(message="Error updating coach", status=400)

@coach_route_bp.route('/coaches/<int:coach_id>', methods=['DELETE'])
def delete_coach(coach_id):
    deleted = coach_service.delete_coach(coach_id)
    if deleted:
        return create_response(message="Coach deleted", status=200)
    return create_response(message="Error deleting coach", status=400)

@coach_route_bp.route('/coaches/<int:coach_id>/coaches-of-team', methods=['GET'])
def get_coaches_teams(coach_id):
    teams = coach_service.get_coaches_team(coach_id)
    return create_response(teams, "Teams found", 200, True)

@coach_route_bp.route('/coaches/<int:coach_id>/teams/<int:team_id>', methods=['POST'])
def assign_coach_to_team(coach_id, team_id):
    success = coach_service.assign_coach_to_team(coach_id, team_id)
    if success:
        return create_response(message="Coach assigned to team", status=200)
    return create_response(message="Error assigning coach to team", status=400)

@coach_route_bp.route('/coaches/<int:coach_id>/teams/<int:team_id>', methods=['DELETE'])
def remove_coach_from_team(coach_id, team_id):
    success = coach_service.remove_coach_from_team(coach_id, team_id)
    if success:
        return create_response(message="Coach removed from team", status=200)
    return create_response(message="Error removing coach from team", status=400)

@coach_route_bp.route('/coaches/<int:coach_id>/seasons', methods=['GET'])
def get_coaches_seasons(coach_id):
    seasons = coach_service.get_coach_seasons(coach_id)
    return create_response(seasons, "Seasons found", 200, True)
