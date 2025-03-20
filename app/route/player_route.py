from flask import Blueprint, request, jsonify

from app.service.player_service import Player_service
from app.utils.response import create_response

player_route_bp = Blueprint('player', __name__)
player_service = Player_service()

@player_route_bp.route('/players/team', methods=['GET'])
def get_player_by_team_season():
    team_id = request.args.get('team_id')
    season_id = request.args.get('season_id')
    players = player_service.get_player_by_team_season(team_id, season_id)
    if players:
        return create_response(players, "Players found", 200, True)
    return create_response(None, "Players not found", 404, False)
