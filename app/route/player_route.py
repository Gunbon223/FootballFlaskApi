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

def create_player():
    player_data = request.json
    new_player = player_service.create_player(player_data)
    if new_player:
        return create_response(data=new_player.to_dict(), status=201)
    return create_response(message="Error creating player", status=400)

def add_player_to_team_season():
    player_data = request.json
    new_player = player_service.add_player_to_team(player_data)
    if new_player:
        return create_response(data=new_player.to_dict(), status=201)
    return create_response(message="Error adding player to team", status=400)

def update_player(player_id):
    player_data = request.json
    updated_player = player_service.update_player(player_id, player_data)
    if updated_player:
        return create_response(data=updated_player.to_dict(), status=200)
    return create_response(message="Error updating player", status=400)

def delete_player(player_id):
    deleted_player = player_service.delete_player(player_id)
    if deleted_player:
        return create_response(data=deleted_player.to_dict(), status=200)
    return create_response(message="Error deleting player", status=400)

def change_player_team_season():
    player_data = request.json
    new_player = player_service.change_player_team_season(player_data)
    if new_player:
        return create_response(data=new_player.to_dict(), status=201)
    return create_response(message="Error changing player team season", status=400)
