import faker
from faker import Faker
from datetime import datetime, timedelta
from appdb import db
from app.model.tournament import Tournament
from app.model.season import Season
from app.model.team import Team, Team_Coach, Team_Season
from app.model.coach import Coach
from app.model.player import Player, Player_Season
from app.model.match import Match
from app.model.lineup import Lineup
from app.model.goal import Goal
from app.model.card import Card
from app.model.transfer_history import Transfer_History
from app.model.player_achievement import Player_Achievement
from app.model.season_standings import Season_Standings
from run_app import app
from random import choice

fake = Faker()

team_json = {
    "England": [
      "Manchester United",
      "Liverpool",
      "Chelsea",
      "Arsenal",
      "Manchester City"
    ],
    "Spain": [
      "Real Madrid",
      "Barcelona",
      "Atletico Madrid",
      "Sevilla",
      "Valencia"
    ],
    "Germany": [
      "Bayern Munich",
      "Borussia Dortmund",
      "RB Leipzig",
      "Bayer Leverkusen",
      "VfL Wolfsburg"
    ],
    "Italy": [
      "Juventus",
      "AC Milan",
      "Inter Milan",
      "AS Roma",
      "Napoli"
    ],
    "France": [
      "Paris Saint-Germain",
      "Marseille",
      "Lyon",
      "Monaco",
      "Lille"
    ]
}

position = {
    "GK", "CB", "LB", "RB", "CM", "CDM", "CAM", "LM", "RM", "LW", "RW", "ST"
}

country = { "England", "Spain", "Germany", "Italy", "France" }



def create_tournaments():
    tournaments = []
    tournament_name = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
    tournament_country = ["England", "Spain", "Italy", "Germany", "France"]
    for _ in range(5):
        tournament = Tournament(
            name=tournament_name[_],
            country=tournament_country[_],
        )
        db.session.add(tournament)
        db.session.commit()
        tournaments.append(tournament)
    return tournaments

def create_seasons(tournaments):
    seasons = []
    for tournament in tournaments:
        for _ in range(2):
            date = fake.date_between(start_date='-2y', end_date='today')
            rnd_time = fake.random_int(min=150, max=290)
            end_date = date + timedelta(days=rnd_time)

            season = Season(
                name=f"{tournament.name} {date.month}/{date.year} - {end_date.month}/{end_date.year}",
                start_date=date,
                end_date= end_date,
                tournament_id=tournament.id
            )
            db.session.add(season)
            db.session.commit()
            seasons.append(season)
    return seasons


def create_teams():
    teams = []
    for country, clubs in team_json.items():
        for club in clubs:
            team = Team(
                name=club,
                country=country
            )
            db.session.add(team)
            db.session.commit()
            teams.append(team)
    return teams

def create_coaches():
    coaches = []
    for _ in range(10):
        coach = Coach(
            name=fake.name(),
            nationality=fake.country(),
            date_of_birth=fake.date_of_birth(None,31,65),
            experience_years=fake.random_int(min=5, max=24)
        )
        db.session.add(coach)
        db.session.commit()
        coaches.append(coach)
    return coaches

def create_team_coaches(teams, coaches, seasons):
    team_coaches = []
    for team in teams:
        coach = fake.random_element(coaches)
        season = fake.random_element(seasons)
        team_coach = Team_Coach(
            team_id=team.id,
            coach_id=coach.id,
            season_id=season.id
        )
        db.session.add(team_coach)
        db.session.commit()
        team_coaches.append(team_coach)
    return team_coaches

def create_players(teams):
    players = []
    for team in teams:
        for _ in range(11):
            player = Player(
                team_id=team.id,
                name=fake.name(),
                position=fake.random_element(position),
                nationality=fake.random_element(country),
                date_of_birth=fake.date_of_birth(None,16,35)
            )
            db.session.add(player)
            db.session.commit()
            players.append(player)
    return players


def create_matches(seasons, team_coaches, team_ss):
    matches = []
    for season in seasons:
        season_teams = [t for t in team_ss if t.season_id == season.id]
        if not season_teams:
            continue
        for _ in range(5):
            home_team = fake.random_element(season_teams)
            away_team = fake.random_element(season_teams)
            if home_team == away_team:
                away_team = fake.random_element(season_teams)
            match = Match(
                season_id=season.id,
                home_team_id=home_team.team_id,
                away_team_id=away_team.team_id,
                match_date=fake.date_time(),
                home_score=fake.random_int(min=0, max=5),
                away_score=fake.random_int(min=0, max=5),
                home_coach_id= fake.random_element(team_coaches).coach_id,
                away_coach_id= fake.random_element(team_coaches).coach_id
            )
            db.session.add(match)
            db.session.commit()
            matches.append(match)
    return matches

def create_lineups(matches, players):
    lineups = []
    for match in matches:
        for team in [match.home_team_id, match.away_team_id]:
            team_players = [p for p in players if p.team_id == team]
            if not team_players:
                continue
            for _ in range(15):
                player = fake.random_element(team_players)
                lineup = Lineup(
                    match_id=match.id,
                    player_id=player.id,
                    team_id=team,
                    is_starting=fake.boolean()
                )
                db.session.add(lineup)
                db.session.commit()
                lineups.append(lineup)

    return lineups

def create_goals(matches, players, teams, lineups):
    for match in matches:
        team_home = [l for l in lineups if l.team_id == match.home_team_id and match.id == l.match_id]
        team_away = [l for l in lineups if l.team_id == match.away_team_id and match.id == l.match_id]
        if match.home_score == 0 and match.away_score == 0:
            continue
        if match.home_score > 0:
            for _ in range(match.home_score):
                goal = Goal(
                    match_id=match.id,
                    player_id=fake.random_element(team_home).player_id,
                    team_id=fake.random_element(team_home).team_id,
                    goal_time=fake.random_int(min=1, max=90)
                )
                db.session.add(goal)
                db.session.commit()
        if match.away_score > 0:
            for _ in range(match.away_score):
                goal = Goal(
                    match_id=match.id,
                    player_id=fake.random_element(team_away).player_id,
                    team_id=fake.random_element(team_away).team_id,
                    goal_time=fake.random_int(min=1, max=90)
                )
                db.session.add(goal)
                db.session.commit()

def create_cards(matches, lineups):
    for match in matches:
        team_lineups = [l for l in lineups if l.match_id == match.id]
        for _ in range(fake.random_int(min=0, max=6)):
            lineup = fake.random_element(team_lineups)
            card = Card(
                match_id=match.id,
                player_id=lineup.player_id,
                team_id=lineup.team_id,
                card_type=fake.random_element(elements=("Yellow", "Red")),
                card_time=fake.random_int(min=1, max=90)
            )
            db.session.add(card)
            db.session.commit()

def create_transfer_histories(players, teams, seasons):
    for _ in range(50):
        money = str(fake.random_int(min=10, max=100)) + "M$"
        transfer_history = Transfer_History(
            player_id=fake.random_element(players).id,
            from_team_id=fake.random_element(teams).id,
            to_team_id=fake.random_element(teams).id,
            transfer_date=fake.date(),
            season_id=fake.random_element(seasons).id,
            detail = money
        )
        db.session.add(transfer_history)
        db.session.commit()

def create_player_achievements(players, seasons, matches):
    for _ in range(50):
        player_achievement = Player_Achievement(
            player_id=fake.random_element(players).id,
            season_id=fake.random_element(seasons).id,
            match_id=fake.random_element(matches).id,
            award_name=fake.gemstone_name(),
            description=fake.text()
        )
        db.session.add(player_achievement)
        db.session.commit()


def create_season_standings(seasons, team_ss):
    standings = []
    for season in seasons:
        for team in team_ss:
            if team.season_id == season.id:
                standing = Season_Standings(
                    id = team.standing_id,
                    ranking=fake.random_int(min=1, max=20)
                )
                db.session.add(standing)
                db.session.commit()
                standings.append(standing)
    return standings

def create_team_seasons(teams, seasons):
    team_ss = []
    for season in seasons:
        selected_teams = fake.random_elements(teams, length=4, unique=True)
        for team in selected_teams:
            team_s = Team_Season(
                season_id=season.id,
                team_id=team.id
            )
            db.session.add(team_s)
            db.session.commit()
            team_ss.append(team_s)
    return team_ss

def create_player_season(players, seasons, teams):
    for p in players:
        for s in seasons:
            player_season = Player_Season(
                player_id=p.id,
                season_id=s.id,
                team_id=p.team_id,
                appearances=fake.random_int(min=0, max=20),
                goals=fake.random_int(min=0, max=10),
                assists=fake.random_int(min=0, max=10),
                yellow_cards=fake.random_int(min=0, max=5),
                red_cards=fake.random_int(min=0, max=2)
            )
            db.session.add(player_season)
            db.session.commit()


def main():
    with app.app_context():
        db.create_all()
        # create_tournaments()
        tournaments = Tournament.query.all()

        # create_seasons(tournaments)

        seasons = Season.query.all()
        #
        # create_teams()
        teams = Team.query.all()
        # create_team_seasons(teams, seasons)
        team_ss = Team_Season.query.all()
        #
        # create_coaches()
        # coaches = Coach.query.all()
        #
        # create_team_coaches(teams, coaches, seasons)
        team_coach = Team_Coach.query.all()
        #
        # create_players(teams)
        players = Player.query.all()
        #
        # standings = create_season_standings(seasons, team_ss)

        # matches = create_matches(seasons, team_coach, team_ss)
        # lineups = create_lineups(matches, players)
        # create_goals(matches, players, teams, lineups)
        # create_cards(matches, lineups)
        # create_transfer_histories(players, teams, seasons)
        # create_player_achievements(players, seasons, matches)
        create_player_season(players, seasons, teams)


if __name__ == "__main__":
    main()