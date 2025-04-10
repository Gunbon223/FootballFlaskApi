import logging

from flask import Flask

from app.route.goal_route import goal_route_bp
from app.route.lineup_route import lineup_route_bp
from app.route.match_route import match_route_bp
from app.route.player_route import player_route_bp
from app.utils.commands import register_commands
from appdb import db
import urllib

# Import all models
from app.service.redis_service import RedisService

# Import all routes
from app.route.team_route import team_route_bp
from app.route.season_route import season_route_bp
from app.route.tournament_route import tournament_route_bp
from app.route.coach_route import coach_route_bp
from app.route.team_ranking_route import team_ranking_route_bp


def create_app(import_name=__name__):
    app = Flask(import_name)
    # params = urllib.parse.quote_plus(
    #     'DRIVER={ODBC Driver 17 for SQL Server};SERVER=GBLAP;DATABASE=footballmng;UID=sa;PWD=123;')
    # app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params

    #  MySQL
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root@localhost:3306/footballmng?charset=utf8mb4"
    db.init_app(app)


    # Configure logging
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)


    with app.app_context():
        redis_service = RedisService.get_instance()
        redis_service.connect()
        db.create_all()

    app.register_blueprint(team_route_bp)
    app.register_blueprint(season_route_bp)
    app.register_blueprint(tournament_route_bp)
    app.register_blueprint(coach_route_bp)
    app.register_blueprint(team_ranking_route_bp)
    app.register_blueprint(player_route_bp)
    app.register_blueprint(match_route_bp)
    app.register_blueprint(lineup_route_bp)
    app.register_blueprint(goal_route_bp)
    register_commands(app)

    return app


