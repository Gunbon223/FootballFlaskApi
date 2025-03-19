from flask import Blueprint, request, jsonify
from app.service.team_ranking_service import TeamRankingService
from app.utils.response import create_response

team_ranking_route_bp = Blueprint('team_ranking', __name__)
team_ranking_service = TeamRankingService()

@team_ranking_route_bp.route('/team/<int:team_id>/ranking', methods=['GET'])
def get_team_ranking(team_id):
    team_ranking = team_ranking_service.get_team_ranking(team_id)
    print(team_ranking)
    if team_ranking:
        return create_response(team_ranking, "Team ranking found", 200, True)
    return create_response(None, "Team ranking not found", 404, False)

@team_ranking_route_bp.route('/season/<int:season_id>/leaderboard', methods=['GET'])
def get_season_ranking(season_id):

    sort_order = request.args.get('sort_order', 'asc')

    if sort_order not in ['asc', 'desc']:
        return create_response(None, "Invalid sort_order. Must be 'asc' or 'desc'", 400, False)
    season_ranking = team_ranking_service.get_leaderboard(season_id,sort_order)
    if season_ranking:
        return create_response(season_ranking, "Season leaderboard found", 200, True)
    return create_response(None, "Season leaderboard not found", 404, False)


