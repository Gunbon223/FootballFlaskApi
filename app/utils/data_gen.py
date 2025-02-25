import faker
from faker import Faker
from datetime import datetime, timedelta, time
from appdb import db
from app.model.tournament import Tournament
from app.model.season import Season
from app.model.team import Team, Team_Coach
from app.model.coach import Coach
from app.model.player import Player, player_team_season
from app.model.match import Match
from app.model.lineup import Lineup
from app.model.goal import Goal
from app.model.card import Card
from app.model.transfer_history import Transfer_History
from app.model.team_season_ranking import Team_Season_Ranking
from app.model.round import Round
from run_app import app
from random import choice, randint

fake = Faker()

team_json = {
    "England": ["Manchester United", "Liverpool", "Chelsea", "Arsenal", "Manchester City"],
    "Spain": ["Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla", "Valencia"],
    "Germany": ["Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen", "VfL Wolfsburg"],
    "Italy": ["Juventus", "AC Milan", "Inter Milan", "AS Roma", "Napoli"],
    "France": ["Paris Saint-Germain", "Marseille", "Lyon", "Monaco", "Lille"]
}

positions = ["GK", "CB", "LB", "RB", "CM", "CDM", "CAM", "LM", "RM", "LW", "RW", "ST"]
countries = ["England", "Spain", "Germany", "Italy", "France"]

def create_tournaments():
    tournaments = []
    tournament_names = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
    for name, country in zip(tournament_names, countries):
        tournament = Tournament(name=name, country=country)
        db.session.add(tournament)
        db.session.commit()
        tournaments.append(tournament)
    return tournaments

def create_seasons(tournaments):
    seasons = []
    for tournament in tournaments:
        for _ in range(2):
            start_date = fake.date_between(start_date='-2y', end_date='today')
            end_date = start_date + timedelta(days=fake.random_int(min=150, max=290))
            season = Season(
                name=f"{tournament.name} {start_date.year}/{end_date.year}",
                start_date=start_date,
                end_date=end_date,
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
            team = Team(name=club, country=country)
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
            date_of_birth=fake.date_of_birth(minimum_age=31, maximum_age=65),
            experience_years=fake.random_int(min=5, max=24)
        )
        db.session.add(coach)
        db.session.commit()
        coaches.append(coach)
    return coaches


def create_team_coaches():
    """ Assign coaches to teams for seasons. """
    teams = Team.query.all()
    coaches = Coach.query.all()
    seasons = Season.query.all()

    for _ in range(len(teams)):
        start_date = fake.date_between(start_date="-5y", end_date=datetime.now())
        end_date = None if randint(0, 1) else fake.date_between(start_date="today", end_date="+2y")

        # Convert dates to datetime
        start_datetime = datetime.combine(start_date, time(0, 0))
        end_datetime = datetime.combine(end_date, time(0, 0)) if end_date else None

        team_coach = Team_Coach(
            team_id=choice(teams).id,
            coach_id=choice(coaches).id,
            season_id=choice(seasons).id,
            start_date=start_datetime,
            end_date=end_datetime
        )
        db.session.add(team_coach)
    db.session.commit()
    print(f"{len(teams)} team-coach assignments added!")


def create_players(num=300):
    """ Create players. """
    for _ in range(num):
        player = Player(
            name=fake.name(),
            position=choice(positions),
            nationality=fake.country(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=40)
        )
        db.session.add(player)
    db.session.commit()
    print(f"{num} players added!")


def create_player_season_teams():
    """ Assign players to teams for seasons. """
    players = Player.query.all()
    teams = Team.query.all()
    seasons = Season.query.all()

    for _ in range(len(players)):
        player_team_season_r = player_team_season(
            player_id=choice(players).id,
            season_id=choice(seasons).id,
            team_id=choice(teams).id,
            goals=randint(0, 30),
            yellow_cards=randint(0, 10),
            red_cards=randint(0, 3)
        )
        db.session.add(player_team_season_r)
    db.session.commit()
    print(f"{len(players)} player-season-team records added!")


def create_rounds(num=15):
    """ Create rounds. """
    seasons = Season.query.all()
    for _ in range(num):
        round_instance = Round(
            season_id=choice(seasons).id,
            round_number=randint(1, 38),
            round_date=fake.date_between(start_date="-5y", end_date="today"),
            is_finished=bool(randint(0, 1))
        )
        db.session.add(round_instance)
    db.session.commit()
    print(f"{num} rounds added!")


def create_matches(num=150):
    """ Create matches. """
    seasons = Season.query.all()
    teams = Team.query.all()
    rounds = Round.query.all()
    coaches = Coach.query.all()

    for _ in range(num):
        home_team, away_team = choice(teams), choice(teams)
        while home_team.id == away_team.id:
            away_team = choice(teams)

        match = Match(
            season_id=choice(seasons).id,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            match_date=fake.date_time_between(start_date="-5y", end_date=datetime.now()),
            home_score=randint(0, 5),
            home_coach_id=choice(coaches).id,
            away_coach_id=choice(coaches).id,
            round_id=choice(rounds).id
        )
        db.session.add(match)
    db.session.commit()
    print(f"{num} matches added!")


def create_goals(num=50):
    """ Create goals. """
    matches = Match.query.all()
    players = Player.query.all()
    teams = Team.query.all()

    for _ in range(num):
        goal = Goal(
            match_id=choice(matches).id,
            player_id=choice(players).id,
            team_id=choice(teams).id,
            goal_time=randint(1, 90)
        )
        db.session.add(goal)
    db.session.commit()
    print(f"{num} goals added!")


def create_cards(num=40):
    """ Create yellow and red cards. """
    matches = Match.query.all()
    players = Player.query.all()
    teams = Team.query.all()
    seasons = Season.query.all()

    for _ in range(num):
        card = Card(
            match_id=choice(matches).id,
            player_id=choice(players).id,
            team_id=choice(teams).id,
            card_type=choice(["Yellow", "Red"]),
            card_time=randint(1, 90),
            season_id=choice(seasons).id
        )
        db.session.add(card)
    db.session.commit()
    print(f"{num} cards added!")


def create_lineups(num=50):
    """ Create lineups for matches. """
    matches = Match.query.all()
    players = Player.query.all()
    teams = Team.query.all()

    for _ in range(num):
        lineup = Lineup(
            match_id=choice(matches).id,
            player_id=choice(players).id,
            team_id=choice(teams).id,
            is_starting=bool(randint(0, 1))
        )
        db.session.add(lineup)
    db.session.commit()
    print(f"{num} lineups added!")

def create_transfer_histories():
    """ Create transfer histories for players. """
    players = Player.query.all()
    teams = Team.query.all()
    seasons = Season.query.all()

    for player in players:
        transfer = Transfer_History(
            player_id=player.id,
            from_team_id=choice(teams).id,
            to_team_id=choice(teams).id,
            season_id=choice(seasons).id,
            transfer_date=fake.date_between(start_date="-5y", end_date="today"),
            # transfer_fee=randint(100000, 10000000)
        )
        db.session.add(transfer)
    db.session.commit()
    print(f"{len(players)} transfer histories added!")

    def create_Team_Season_Ranking():
        """ Generate rankings for each team in each season based on match results. """
        seasons = Season.query.all()
        teams = Team.query.all()

        if not seasons or not teams:
            print("No seasons or teams found in the database.")
            return

        for season in seasons:
            rankings = []

            for team in teams:
                # Fetch matches where the team played
                matches = Match.query.filter(
                    (Match.season_id == season.id) &
                    ((Match.home_team_id == team.id) | (Match.away_team_id == team.id))
                ).all()

                matches_played = len(matches)
                wins, draws, losses = 0, 0, 0
                goals_for, goals_against = 0, 0

                for match in matches:
                    if match.home_team_id == team.id:
                        goals_for += match.home_score
                        goals_against += match.away_score
                        if match.home_score > match.away_score:
                            wins += 1
                        elif match.home_score < match.away_score:
                            losses += 1
                        else:
                            draws += 1
                    else:
                        goals_for += match.away_score
                        goals_against += match.home_score
                        if match.away_score > match.home_score:
                            wins += 1
                        elif match.away_score < match.home_score:
                            losses += 1
                        else:
                            draws += 1

                goal_difference = goals_for - goals_against
                points = wins * 3 + draws

                rankings.append({
                    "team_id": team.id,
                    "season_id": season.id,
                    "matches_played": matches_played,
                    "wins": wins,
                    "draws": draws,
                    "losses": losses,
                    "goals_for": goals_for,
                    "goals_against": goals_against,
                    "goal_difference": goal_difference,
                    "points": points
                })

            # Sort teams based on points, then goal difference
            rankings.sort(key=lambda x: (x["points"], x["goal_difference"]), reverse=True)

            # Assign ranking positions
            for rank, data in enumerate(rankings, start=1):
                ranking_entry = Team_Season_Ranking(
                    team_id=data["team_id"],
                    season_id=data["season_id"],
                    matches_played=data["matches_played"],
                    wins=data["wins"],
                    draws=data["draws"],
                    losses=data["losses"],
                    goals_for=data["goals_for"],
                    goals_against=data["goals_against"],
                    goal_difference=data["goal_difference"],
                    points=data["points"],
                    ranking=rank
                )
                db.session.add(ranking_entry)

        db.session.commit()
        print("Team season rankings have been calculated and saved!")


def create_Team_Season_Ranking():
    """ Generate rankings for each team in each season based on match results. """
    seasons = Season.query.all()
    teams = Team.query.all()

    if not seasons or not teams:
        print("No seasons or teams found in the database.")
        return

    for season in seasons:
        rankings = []

        for team in teams:
            # Fetch matches where the team played
            matches = Match.query.filter(
                (Match.season_id == season.id) &
                ((Match.home_team_id == team.id) | (Match.away_team_id == team.id))
            ).all()

            matches_played = len(matches)
            wins, draws, losses = 0, 0, 0
            goals_for, goals_against = 0, 0

            for match in matches:
                if match.home_team_id == team.id:
                    goals_for += match.home_score
                    goals_against += match.away_score
                    if match.home_score > match.away_score:
                        wins += 1
                    elif match.home_score < match.away_score:
                        losses += 1
                    else:
                        draws += 1
                else:
                    goals_for += match.away_score
                    goals_against += match.home_score
                    if match.away_score > match.home_score:
                        wins += 1
                    elif match.away_score < match.home_score:
                        losses += 1
                    else:
                        draws += 1

            goal_difference = goals_for - goals_against
            points = wins * 3 + draws

            rankings.append({
                "team_id": team.id,
                "season_id": season.id,
                "matches_played": matches_played,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_difference": goal_difference,
                "points": points
            })

        # Sort teams based on points, then goal difference
        rankings.sort(key=lambda x: (x["points"], x["goal_difference"]), reverse=True)

        # Assign ranking positions
        for rank, data in enumerate(rankings, start=1):
            ranking_entry = Team_Season_Ranking(
                team_id=data["team_id"],
                season_id=data["season_id"],
                matches_played=data["matches_played"],
                wins=data["wins"],
                draws=data["draws"],
                losses=data["losses"],
                goals_for=data["goals_for"],
                goals_against=data["goals_against"],
                goal_difference=data["goal_difference"],
                points=data["points"],
                ranking=rank
            )
            db.session.add(ranking_entry)

    db.session.commit()
    print("Team season rankings have been calculated and saved!")



def main():
    with app.app_context():
        db.create_all()
        tournaments = create_tournaments()
        seasons = create_seasons(tournaments)
        teams = create_teams()
        coaches = create_coaches()
        create_player_season_teams()
        create_team_coaches()
        create_players()
        create_rounds()
        create_matches()
        create_lineups()
        create_goals()
        create_cards()
        create_transfer_histories()
        create_Team_Season_Ranking()

if __name__ == "__main__":
    main()