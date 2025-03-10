from flask import Blueprint, request, jsonify
from app.service.tournamentservice import Tournament_service
from app.utils.response import create_response

tournament_route_bp = Blueprint('tournament', __name__)
tournament_service = Tournament_service()


@tournament_route_bp.route('/tournaments', methods=['GET'])
def get_all_tournaments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    order_by = request.args.get('order_by')
    sort_order = request.args.get('sort_order', 'asc')

    tournaments, total = tournament_service.get_all_tournaments_paginated(
        page=page,
        per_page=per_page,
        order_by=order_by,
        sort_order=sort_order
    )
    tournaments_dict = [tournament.to_dict() for tournament in tournaments]

    pagination = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'order_by': order_by,
        'sort_order': sort_order
    }

    return create_response(
        tournaments_dict,
        "Tournaments found",
        200,
        True,
        pagination=pagination
    )


@tournament_route_bp.route('/tournaments/<int:tournament_id>', methods=['GET'])
def get_tournament_by_id(tournament_id):
    tournament = tournament_service.get_tournament_by_id(tournament_id)
    if tournament:
        return create_response(tournament.to_dict(), "Tournament found", 200, True)
    return create_response(None, "Tournament not found", 404, False)


@tournament_route_bp.route('/tournaments', methods=['POST'])
def create_tournament():
    tournament_data = request.json
    new_tournament = tournament_service.create_tournament(tournament_data)
    if new_tournament:
        return create_response(data=new_tournament.to_dict(), status=201)
    return create_response(message="Error creating tournament", status=400)


@tournament_route_bp.route('/tournaments/<int:tournament_id>', methods=['PUT'])
def update_tournament(tournament_id):
    tournament_data = request.json
    updated_tournament = tournament_service.update_tournament(tournament_id, tournament_data)
    if updated_tournament:
        return create_response(data=updated_tournament.to_dict(), status=200)
    return create_response(message="Error updating tournament", status=400)


@tournament_route_bp.route('/tournaments/<int:tournament_id>', methods=['DELETE'])
def delete_tournament(tournament_id):
    deleted_tournament = tournament_service.delete_tournament(tournament_id)
    if deleted_tournament:
        return create_response(data=deleted_tournament.to_dict(), status=200)
    return create_response(message="Error deleting tournament", status=400)


@tournament_route_bp.route('/tournaments/<int:tournament_id>/seasons', methods=['GET'])
def get_tournament_seasons(tournament_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_order = request.args.get('sort_order', 'asc')
    seasons, total = tournament_service.get_tournament_seasons(tournament_id, page, per_page, sort_order)
    pagination = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'sort_order': sort_order
    }
    if seasons:
        return create_response(seasons, "Seasons found", 200, True,pagination)
    return create_response(None, "Seasons not found", 404, False)
