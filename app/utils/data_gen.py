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


def create_players(num=1000):
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
    teams = Team.query.all()
    seasons = Season.query.all()

    for season in seasons:
        players = Player.query.all()
        if len(players) < 25 * len(teams):
            raise ValueError("Not enough players to assign 25 unique players per team.")

        for team in teams:
            selected_players = set(fake.random_elements(elements=players, length=25, unique=True))
            for player in selected_players:
                player_team_season_r = player_team_season(
                    player_id=player.id,
                    season_id=season.id,
                    team_id=team.id,
                    goals=randint(0, 30),
                    yellow_cards=randint(0, 10),
                    red_cards=randint(0, 3)
                )
                db.session.add(player_team_season_r)
                players.remove(player)
    db.session.commit()
    print('25 players per team per season added!')


def create_rounds(num=15):
    """ Create rounds. """
    seasons = Season.query.all()
    for seasons in seasons:
        for i in range(randint(5, num)):
            round = Round(
                round_number=i,
                season_id=seasons.id,
                round_date=fake.date_between(start_date='-2y', end_date='today'),
                is_finished=fake.boolean(chance_of_getting_true=80)
            )
            db.session.add(round)
    db.session.commit()
    print(f"{num} rounds added!")


def create_matches():
        matches = []
        seasons = Season.query.all()
        team_season = Team_Season_Ranking.query.all()
        team_ss = [t for t in team_season if t.season_id in [s.id for s in seasons]]
        team_coaches = Team_Coach.query.all()
        rounds = Round.query.all()

        for season in seasons:
            season_teams = [t for t in team_ss if t.season_id == season.id]
            if not season_teams:
                continue
            season_rounds = [r for r in rounds if r.season_id == season.id]
            for round in season_rounds:
                for home_team in season_teams:
                    away_team = fake.random_element(season_teams)
                    while home_team == away_team:
                        away_team = fake.random_element(season_teams)
                    match = Match(
                        season_id=season.id,
                        home_team_id=home_team.team_id,
                        away_team_id=away_team.team_id,
                        match_date=fake.date_time(),
                        home_score=fake.random_int(min=0, max=5),
                        away_score=fake.random_int(min=0, max=5),
                        home_coach_id=fake.random_element(team_coaches).coach_id,
                        away_coach_id=fake.random_element(team_coaches).coach_id,
                        round_id=round.id
                    )
                    db.session.add(match)
                    db.session.commit()
                    matches.append(match)
        print(f"{len(matches)} matches added!")

def create_lineups():
    matches = Match.query.all()
    for match in matches:
        # Retrieve home team's players for this season
        home_players = player_team_season.query.filter_by(
            season_id=match.season_id,
            team_id=match.home_team_id
        ).all()
        # Retrieve away team's players for this season
        away_players = player_team_season.query.filter_by(
            season_id=match.season_id,
            team_id=match.away_team_id
        ).all()

        # Pick 20 home players
        chosen_home = fake.random_elements(elements=home_players, length=20, unique=True)
        # Choose 11-13 of them to start
        home_starters_count = randint(11, 13)
        home_starters = set(fake.random_elements(chosen_home, length=home_starters_count, unique=True))

        # Insert home lineups
        for record in chosen_home:
            lineup = Lineup(
                match_id=match.id,
                player_id=record.player_id,
                team_id=record.team_id,
                is_starting=(record in home_starters)
            )
            db.session.add(lineup)

        # Pick 20 away players
        chosen_away = fake.random_elements(elements=away_players, length=20, unique=True)
        # Choose 11-13 of them to start
        away_starters_count = randint(11, 13)
        away_starters = set(fake.random_elements(chosen_away, length=away_starters_count, unique=True))

        # Insert away lineups
        for record in chosen_away:
            lineup = Lineup(
                match_id=match.id,
                player_id=record.player_id,
                team_id=record.team_id,
                is_starting=(record in away_starters)
            )
            db.session.add(lineup)

    db.session.commit()
    print(f"{len(matches) * 20} lineups added!")

def add_goals():
    matches = Match.query.all()
    for match in matches:
        # Home team starting players
        home_starting = Lineup.query.filter_by(
            match_id=match.id,
            team_id=match.home_team_id,
            is_starting=True
        ).all()

        # Away team starting players
        away_starting = Lineup.query.filter_by(
            match_id=match.id,
            team_id=match.away_team_id,
            is_starting=True
        ).all()

        home_goals_count = match.home_score
        for _ in range(home_goals_count):
            scorer = choice(home_starting)
            goal = Goal(
                match_id=match.id,
                player_id=scorer.player_id,
                team_id=scorer.team_id,
                goal_time=randint(1, 90)
            )
            db.session.add(goal)

        away_goals_count = match.away_score
        for _ in range(away_goals_count):
            scorer = choice(away_starting)
            goal = Goal(
                match_id=match.id,
                player_id=scorer.player_id,
                team_id=scorer.team_id,
                goal_time=randint(1, 90)
            )
            db.session.add(goal)

    db.session.commit()
    print(f"{sum([m.home_score + m.away_score for m in matches])} goals added!")


def create_cards(num=240):
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
        selected_teams = fake.random_elements(elements=teams, length=randint(15, 20), unique=True)
        index = 0
        for selected_team in selected_teams:
            index += 1
            rankings.append(selected_team)
            ranking = Team_Season_Ranking(
                team_id=selected_team.id,
                season_id=season.id,
                ranking=index,
                points=0,
                wins=0,
                draws=0,
                losses=0,
                goals_for=0,
                goals_against=0,
                matches_played=0
            )
            db.session.add(ranking)
        db.session.commit()
    print(f"{len(seasons)} seasons' rankings added!")


def update_team_season_rankings():
            seasons = Season.query.all()
            for season in seasons:
                rankings = Team_Season_Ranking.query.filter_by(season_id=season.id).all()
                for r in rankings:
                    r.points = 0
                    r.wins = 0
                    r.draws = 0
                    r.losses = 0
                    r.goals_for = 0
                    r.goals_against = 0
                    r.goal_difference = 0
                    r.matches_played = 0

                matches = Match.query.filter_by(season_id=season.id).all()
                for match in matches:
                    home_rank = next((x for x in rankings if x.team_id == match.home_team_id), None)
                    away_rank = next((x for x in rankings if x.team_id == match.away_team_id), None)
                    if not home_rank or not away_rank:
                        continue

                    home_rank.matches_played += 1
                    away_rank.matches_played += 1
                    home_rank.goals_for += match.home_score
                    home_rank.goals_against += match.away_score
                    away_rank.goals_for += match.away_score
                    away_rank.goals_against += match.home_score

                    if match.home_score > match.away_score:
                        home_rank.wins += 1
                        home_rank.points += 3
                        away_rank.losses += 1
                    elif match.home_score < match.away_score:
                        away_rank.wins += 1
                        away_rank.points += 3
                        home_rank.losses += 1
                    else:
                        home_rank.draws += 1
                        away_rank.draws += 1
                        home_rank.points += 1
                        away_rank.points += 1

                for r in rankings:
                    r.goal_difference = r.goals_for - r.goals_against

                rankings.sort(key=lambda x: (x.points, x.goal_difference), reverse=True)
                current_rank = 1
                for r in rankings:
                    r.ranking = current_rank
                    current_rank += 1

                db.session.commit()
                print(f"Rankings updated for {season.name}!")

def main():
    with app.app_context():
        db.create_all()
        tournaments = create_tournaments()
        seasons = create_seasons(tournaments)
        create_rounds()
        teams = create_teams()
        coaches = create_coaches()
        create_players()
        create_Team_Season_Ranking()
        create_player_season_teams()
        create_team_coaches()
        create_matches()
        create_lineups()
        add_goals()
        create_cards()
        create_transfer_histories()
        update_team_season_rankings()

if __name__ == "__main__":
    main()
