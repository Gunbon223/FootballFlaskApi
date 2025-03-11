import sys
import os
# Add the root directory to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Continue with your existing imports
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
        for _ in range(3):
            start_date = fake.date_between(start_date='-10y', end_date='today')
            end_date = start_date + timedelta(days=fake.random_int(min=100, max=120))
            season = Season(
                name=f"{tournament.name} {start_date.month}/{start_date.year} - {end_date.month}/{end_date.year}",
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
    print(f"{len(teams)} teams added!")


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


def create_rounds():
    """Create rounds for each season with proper spacing and dates."""
    seasons = Season.query.all()
    rounds_created = 0

    for season in seasons:
        # Get teams participating in this season
        teams_in_season = Team_Season_Ranking.query.filter_by(season_id=season.id).all()
        teams_count = len(teams_in_season)

        if teams_count < 2:
            print(f"Skip creating rounds for {season.name}: not enough teams")
            continue

        # For a complete league season where each team plays all others twice
        required_rounds = (teams_count - 1) * 2

        # Calculate time between rounds (typically one week in real leagues)
        season_duration = (season.end_date - season.start_date).days
        days_between_rounds = min(7, max(3, season_duration // (required_rounds + 1)))

        for i in range(required_rounds):
            round_date = season.start_date + timedelta(days=(i * days_between_rounds))

            if round_date > season.end_date:
                round_date = season.end_date - timedelta(days=(required_rounds - i))

            # Convert date to datetime before comparison
            is_finished = datetime.combine(round_date, time()) < datetime.now()

            round = Round(
                round_number=i + 1,
                season_id=season.id,
                round_date=round_date,
                is_finished=is_finished
            )
            db.session.add(round)
            rounds_created += 1

    db.session.commit()
    print(f"{rounds_created} rounds created across all seasons!")


def create_matches():
    from datetime import datetime, date, time, timedelta

    matches = []
    seasons = Season.query.all()
    team_season = Team_Season_Ranking.query.all()

    for season in seasons:
        season_teams = [t for t in team_season if t.season_id == season.id]
        if len(season_teams) < 2:
            continue

        season_rounds = Round.query.filter_by(season_id=season.id).all()
        teams_count = len(season_teams)
        required_rounds = (teams_count - 1) * 2

        if len(season_rounds) < required_rounds:
            existing_count = len(season_rounds)
            for i in range(existing_count, required_rounds):
                round_date = season.start_date + timedelta(days=(i * 7))
                is_finished = datetime.combine(round_date, time()) < datetime.now()
                new_round = Round(
                    round_number=i + 1,
                    season_id=season.id,
                    round_date=round_date,
                    is_finished=is_finished
                )
                db.session.add(new_round)
            db.session.commit()
            season_rounds = Round.query.filter_by(season_id=season.id).all()[:required_rounds]

        first_half_rounds = season_rounds[:teams_count - 1]
        for round_idx, current_round in enumerate(first_half_rounds):
            team_indices = list(range(teams_count))
            for i in range(teams_count // 2):
                home_idx = 0 if i == 0 else team_indices[i]
                away_idx = team_indices[teams_count - 1 - i]

                home_team = season_teams[home_idx]
                away_team = season_teams[away_idx]

                round_date = current_round.round_date
                if isinstance(round_date, date) and not isinstance(round_date, datetime):
                    round_date = datetime.combine(round_date, time())

                match_date = round_date + timedelta(hours=randint(12, 20))
                match = Match(
                    season_id=season.id,
                    home_team_id=home_team.team_id,
                    away_team_id=away_team.team_id,
                    match_start_date=match_date,
                    match_end_date=match_date + timedelta(hours=2),
                    home_score=randint(0, 5),
                    away_score=randint(0, 5),
                    referee=fake.name(),
                    round_id=current_round.id
                )
                db.session.add(match)
                matches.append(match)

            team_indices = [team_indices[0]] + [team_indices[-1]] + team_indices[1:-1]

        second_half_rounds = season_rounds[teams_count - 1:required_rounds]
        first_half_matches = [m for m in matches if m.season_id == season.id]

        for idx, current_round in enumerate(second_half_rounds):
            for match in first_half_matches[idx * (teams_count // 2):(idx + 1) * (teams_count // 2)]:
                round_date = current_round.round_date
                if isinstance(round_date, date) and not isinstance(round_date, datetime):
                    round_date = datetime.combine(round_date, time())

                match_date = round_date + timedelta(hours=randint(12, 20))
                reverse_match = Match(
                    season_id=season.id,
                    home_team_id=match.away_team_id,
                    away_team_id=match.home_team_id,
                    match_start_date=match_date,
                    match_end_date=match_date + timedelta(hours=2),
                    home_score=randint(0, 5),
                    away_score=randint(0, 5),
                    referee=fake.name(),
                    round_id=current_round.id
                )
                db.session.add(reverse_match)
                matches.append(reverse_match)

        db.session.commit()

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
        home_starters_count = randint(11, 15)
        home_starters = set(fake.random_elements(chosen_home, length=home_starters_count, unique=True))

        # Insert home lineups
        for record in chosen_home:
            time_in = None
            if fake.random_int(min=1, max=100) > 95:
                time_in = randint(1, 75)
            time_out = None
            if 50 < fake.random_int(min=1, max=100) < 55:
                if time_in:
                    time_out = time_in + randint(1, 90 - time_in)
                    if time_out > 90:
                        time_out = 90 - randint(0, 15)
                else:
                    time_out = randint(45, 90)
            lineup = Lineup(
                match_id=match.id,
                player_id=record.player_id,
                team_id=record.team_id,
                is_starting=(record in home_starters),
                time_in=time_in,
                time_out=time_out if time_in else None
            )
            db.session.add(lineup)

        # Pick 20 away players
        chosen_away = fake.random_elements(elements=away_players, length=20, unique=True)
        # Choose 11-13 of them to start
        away_starters_count = randint(11, 13)
        away_starters = set(fake.random_elements(chosen_away, length=away_starters_count, unique=True))

        # Insert away lineups - FIX: Use away_starters instead of home_starters
        for record in chosen_away:
            time_in = None
            if fake.random_int(min=1, max=100) > 95:
                time_in = randint(1, 75)
            time_out = None
            if 50 < fake.random_int(min=1, max=100) < 55:
                if time_in:
                    time_out = time_in + randint(1, 90 - time_in)
                    if time_out > 90:
                        time_out = 90 - randint(0, 15)
                else:
                    time_out = randint(45, 90)
            lineup = Lineup(
                match_id=match.id,
                player_id=record.player_id,
                team_id=record.team_id,
                is_starting=(record in away_starters),  # Fixed: was using home_starters
                time_in=time_in,
                time_out=time_out if time_in else None
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

        # Get all players if no starters are found
        if not home_starting:
            home_starting = Lineup.query.filter_by(
                match_id=match.id,
                team_id=match.home_team_id
            ).all()

        if not away_starting:
            away_starting = Lineup.query.filter_by(
                match_id=match.id,
                team_id=match.away_team_id
            ).all()

        # Skip if still no players found
        if not home_starting or not away_starting:
            print(f"Skipping goals for match {match.id}: missing players")
            continue

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
            title=fake.sentence(),
            transfer_fee=randint(100000, 10000000)
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


def update_player_season_teams():
    # Get all player seasons and create a lookup dictionary
    player_seasons = player_team_season.query.all()
    player_season_lookup = {}
    for ps in player_seasons:
        key = (ps.player_id, ps.season_id, ps.team_id)
        player_season_lookup[key] = ps

    # Reset statistics
    for ps in player_seasons:
        ps.goals = 0
        ps.yellow_cards = 0
        ps.red_cards = 0

    # Update goals using modern SQLAlchemy syntax
    goals = db.session.query(Goal, Match).join(Match).all()
    for goal, match in goals:
        key = (goal.player_id, match.season_id, goal.team_id)
        player_season = player_season_lookup.get(key)
        if player_season:
            player_season.goals += 1

    # Update cards
    cards = Card.query.all()
    for card in cards:
        key = (card.player_id, card.season_id, card.team_id)
        player_season = player_season_lookup.get(key)
        if player_season:
            if card.card_type == "Yellow":
                player_season.yellow_cards += 1
            elif card.card_type == "Red":
                player_season.red_cards += 1

    db.session.commit()
    print("Player season statistics updated!")


def main():
    with app.app_context():
        db.create_all()
        tournaments = create_tournaments()
        seasons = create_seasons(tournaments)
        teams = create_teams()
        create_Team_Season_Ranking()
        create_rounds()
        coaches = create_coaches()
        create_players()
        create_players()
        create_player_season_teams()
        create_team_coaches()
        create_matches()
        create_lineups()
        add_goals()
        create_cards()
        create_transfer_histories()

        update_team_season_rankings()
        update_player_season_teams()
        print("Data completed!")


if __name__ == "__main__":
    main()
