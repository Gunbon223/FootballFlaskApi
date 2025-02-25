from flask import Flask
from appdb import db
import urllib

# Import all models
from app.model.tournament import Tournament
from app.model.season import Season
from app.model.team import Team
from app.model.coach import Coach
from app.model.team import Team_Coach
from app.model.player import Player
from app.model.player import player_team_season
from app.model.round import Round
from app.model.match import Match
from app.model.lineup import Lineup
from app.model.goal import Goal
from app.model.card import Card
from app.model.transfer_history import Transfer_History
from app.model.team_season_ranking import Team_Season_Ranking


def create_app():
    app = Flask(__name__)
    params = urllib.parse.quote_plus(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=GBLAP;DATABASE=footballmng;UID=sa;PWD=123;')
    app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app