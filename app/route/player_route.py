from flask import Blueprint, request, jsonify

from app.service.player_service import Playerservice
from app.service.season_service import SeasonService
from app.utils.response import create_response

season_route_bp = Blueprint('player', __name__)
Playerservice = Playerservice()