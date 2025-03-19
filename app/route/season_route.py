from flask import Blueprint, request, jsonify
from app.service.season_service import SeasonService
from app.utils.response import create_response

season_route_bp = Blueprint('season', __name__)
season_service = SeasonService()

@season_route_bp.route('/seasons', methods=['GET'])
def get_all_seasons():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    order_by = request.args.get('order_by')
    sort_order = request.args.get('sort_order', 'asc')

    seasons, total = season_service.get_all_seasons_paginated(
        page=page,
        per_page=per_page,
        order_by=order_by,
        sort_order=sort_order
    )
    seasons_dict = [season.to_dict() for season in seasons]

    pagination = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'order_by': order_by,
        'sort_order': sort_order
    }

    return create_response(
        seasons_dict,
        "Seasons found",
        200,
        True,
        pagination=pagination
    )


@season_route_bp.route('/seasons/<int:season_id>', methods=['GET'])
def get_season_by_id(season_id):
    season = season_service.get_season_by_id(season_id)
    if season:
        return create_response(season.to_dict(), "Season found", 200, True)
    return create_response(None, "Season not found", 404, False)

@season_route_bp.route('/seasons', methods=['POST'])
def create_season():
    season_data = request.json
    new_season = season_service.create_season(season_data)
    if new_season:
        return create_response(data=new_season.to_dict(), status=201)
    return create_response(message="Error creating season", status=400)

@season_route_bp.route('/seasons/<int:season_id>', methods=['PUT'])
def update_season(season_id):
    season_data = request.json
    updated_season = season_service.update_season(season_id, season_data)
    if updated_season:
        return create_response(data=updated_season.to_dict(), status=200)
    return create_response(message="Error updating season", status=400)

@season_route_bp.route('/seasons/<int:season_id>', methods=['DELETE'])
def delete_season(season_id):
    success = season_service.delete_season(season_id)
    if success:
        return create_response(message="Season deleted", status=200)
    return create_response(message="Error deleting season", status=400)

