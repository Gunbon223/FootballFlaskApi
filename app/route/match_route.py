from flask import Blueprint, request, jsonify

from app.service.match_service import MatchService
from app.utils.response import create_response

match_route_bp = Blueprint('match', __name__)
match_service = MatchService()

@match_route_bp.route('/matches', methods=['GET'])
def get_all_matches():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    order_by = request.args.get('order_by')
    sort_order = request.args.get('sort_order', 'asc')

    matches, total = match_service.get_all_matches_paginated(
        page=page,
        per_page=per_page,
        order_by=order_by,
        sort_order=sort_order
    )
    matches_dict = [match.to_dict() for match in matches]

    pagination = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'order_by': order_by,
        'sort_order': sort_order
    }

    return create_response(
        matches_dict,
        "Matches found",
        200,
        True,
        pagination=pagination
    )

@match_route_bp.route('/matches/<int:match_id>', methods=['GET'])
def get_match_by_id(match_id):
    match = match_service.get_match_by_id(match_id)
    if match:
        return create_response(match.to_dict(), "Match found", 200, True)
    return create_response(None, "Match not found", 404, False)

@match_route_bp.route('/matches', methods=['POST'])
def create_match():
    match_data = request.json
    new_match = match_service.create_match(match_data)
    if new_match:
        return create_response(data=new_match.to_dict(), status=201)
    return create_response(message="Error creating match", status=400)

@match_route_bp.route('/matches/<int:match_id>', methods=['PUT'])
def update_match(match_id):
    match_data = request.json
    updated_match = match_service.update_match(match_id, match_data)
    if updated_match:
        return create_response(data=updated_match.to_dict(), status=200)
    return create_response(message="Error updating match", status=400)

@match_route_bp.route('/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    deleted = match_service.delete_match(match_id)
    if deleted:
        return create_response(message="Match deleted", status=200)
    return create_response(message="Error deleting match", status=400)

@match_route_bp.route('/matches/team/season', methods=['GET'])
def get_recent_matches_team_season():
    team_id = request.args.get('team_id')
    season_id = request.args.get('season_id')
    sort_order = request.args.get('sort_order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    matches,total = match_service.get_recent_matches_of_team_season(
        team_id,
        season_id,
        sort_order,
        page,
        per_page
    )

    pagination = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'sort_order': sort_order
    }

    return create_response(
        matches,
        "Recent matches found",
        200,
        True,
        pagination=pagination
    )

@match_route_bp.route('/matches/team', methods=['GET'])
def get_recent_matches_team():
    team_id = request.args.get('team_id')
    sort_order = request.args.get('sort_order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    matches,total = match_service.get_recent_matches_of_team(
        team_id,
        sort_order,
        page,
        per_page
    )

    pagination = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'sort_order': sort_order
    }

    return create_response(
        matches,
        "Recent matches found",
        200,
        True,
        pagination=pagination
    )

@match_route_bp.route('/matches/round', methods=['GET'])
def get_matches_by_round():
    season_id = request.args.get('season_id')
    round_id = request.args.get('round_id')
    sort_order = request.args.get('sort_order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    matches, total = match_service.get_matches_by_round(
        season_id,
        round_id,
        sort_order,
        page,
        per_page
    )

    pagination = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'sort_order': sort_order
    }

    return create_response(
        matches,
        "Round matches found",
        200,
        True,
        pagination=pagination
    )


