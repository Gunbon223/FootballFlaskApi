from flask import Blueprint, request, jsonify

from app.service.goal_service import GoalService
from app.utils.response import create_response

goal_route_bp = Blueprint('goal', __name__)
goal_service = GoalService()

@goal_route_bp.route('/match-goals', methods=['GET'])
def get_match_goals():
    match_id = request.args.get('match_id')

    if not match_id:
        return create_response(
            None,
            "Match ID is required",
            400,
            False
        )

    goals = goal_service.get_match_goals(match_id)

    return create_response(
        goals,
        "Match goals retrieved successfully",
        200,
        True
    )

@goal_route_bp.route('/player-season-goals', methods=['GET'])
def get_player_season_goals():
    player_id = request.args.get('player_id')
    season_id = request.args.get('season_id')

    if not player_id or not season_id:
        return create_response(
            None,
            "Player ID and Season ID are required",
            400,
            False
        )

    goals = goal_service.get_player_season_goals(player_id, season_id)

    return create_response(
        {"goals": goals},
        "Player season goals retrieved successfully",
        200,
        True
    )

@goal_route_bp.route('/player-career-goals', methods=['GET'])
def get_player_career_goals():
    player_id = request.args.get('player_id')

    if not player_id:
        return create_response(
            None,
            "Player ID is required",
            400,
            False
        )

    goals = goal_service.get_player_career_goals(player_id)

    return create_response(
        {"goals": goals},
        "Player career goals retrieved successfully",
        200,
        True
    )

@goal_route_bp.route('/season-top-scorers', methods=['GET'])
def get_season_top_scorers():
    season_id = request.args.get('season_id')
    limit = request.args.get('limit', 10, type=int)

    if not season_id:
        return create_response(
            None,
            "Season ID is required",
            400,
            False
        )

    top_scorers = goal_service.get_season_top_scorers(season_id, limit)

    return create_response(
        top_scorers,
        "Season top scorers retrieved successfully",
        200,
        True
    )