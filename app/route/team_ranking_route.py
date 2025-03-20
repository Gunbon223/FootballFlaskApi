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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    total_leader = 'total_leader' in request.args

    if sort_order not in ['asc', 'desc']:
        return create_response(None, "Invalid sort_order. Must be 'asc' or 'desc'", 400, False)

    season_ranking, total = team_ranking_service.get_leaderboard(season_id, sort_order, page, per_page, total_leader)

    if season_ranking:
        pagination = {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'sort_order': sort_order

        }
        return create_response(season_ranking, "Season leaderboard found", 200, True, pagination=pagination)

    return create_response(None, "Season leaderboard not found", 404, False)

