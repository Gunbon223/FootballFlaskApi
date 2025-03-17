import click
from flask.cli import with_appcontext

from app.model.card import Card
from app.model.goal import Goal
from app.model.lineup import Lineup
from app.model.team_season_ranking import Team_Season_Ranking
from app.service.db_sync_service import DBSyncService
from app.model.team import Team, Team_Coach
from app.model.player import Player,player_team_season
from app.model.match import Match
from app.model.tournament import Tournament
from app.model.round import Round
from app.model.season import Season
from app.model.transfer_history import Transfer_History
# Import other models as needed

@click.command('sync-to-redis')
@with_appcontext
def sync_to_redis_command():
    """Sync all data from SQL database to Redis"""
    sync_service = DBSyncService()

    # (model class, redis prefix)
    models_to_sync = [
        (Tournament, 'tournament'),
        (Season, 'season'),
        (Team, 'team'),
        (Player, 'player'),
        (Match, 'match'),
        (Round, 'round'),
        (Card, 'card'),
        # (Goal, 'goal'),
        # (Lineup, 'lineup'),
        (Team_Season_Ranking, 'team_season_ranking'),
        (Transfer_History, 'transfer_history'),
        (Team_Coach, 'team_coach'),
        (player_team_season, 'player_team_season')

    ]

    total = sync_service.sync_all_models(models_to_sync)
    click.echo(f"Successfully synced {total} records to Redis")


def register_commands(app):
    app.cli.add_command(sync_to_redis_command)