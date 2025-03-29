from flask import Blueprint, request, jsonify

from app.service.lineup_service import LineupService
from app.utils.response import create_response

lineup_route_bp = Blueprint('lineup', __name__)
lineup_service = LineupService()

@lineup_route_bp.route('/match-players', methods=['GET'])
def get_match_players():
    match_id = request.args.get('match_id')
    team_id = request.args.get('team_id')

    if not match_id:
        return create_response(
            None,
            "Match ID is required",
            400,
            False
        )

    players = lineup_service.get_match_players(match_id, team_id)

    return create_response(
        players,
        "Match players retrieved successfully",
        200,
        True
    )

@lineup_route_bp.route('/match-substitutions', methods=['GET'])
def get_match_substitutions():
    match_id = request.args.get('match_id')

    if not match_id:
        return create_response(
            None,
            "Match ID is required",
            400,
            False
        )

    substitutions = lineup_service.get_match_substitutions(match_id)

    return create_response(
        substitutions,
        "Match substitutions retrieved successfully",
        200,
        True
    )