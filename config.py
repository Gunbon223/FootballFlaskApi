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
from app.model.player import Player_Season
from app.model.match import Match
from app.model.lineup import Lineup
from app.model.goal import Goal
from app.model.card import Card
from app.model.transfer_history import Transfer_History
from app.model.player_achievement import Player_Achievement
from app.model.season_standings import Season_Standings
from app.model.team import Team_Season


def create_app():
    app = Flask(__name__)
    params = urllib.parse.quote_plus(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=GBLAP;DATABASE=footballmng;UID=sa;PWD=123;')
    app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app