from flask import current_app
from app.service.redis_service import RedisService
from appdb import db
import time
import json
from datetime import date, datetime


class DBSyncService:
    def __init__(self):
        self.redis_service = RedisService.get_instance()
        # Register model handlers in a dictionary
        self.model_handlers = {
            "Season": self._handle_season,
            "Team_Coach": self._handle_team_coach,
            "Team_Season_Ranking": self._handle_team_season_ranking,
            "Player_Team": self._handle_player_team,
            "Match": self._handle_match,
            "Lineup": self._handle_lineup,  # Changed from Match_Player to Lineup
            "Goal": self._handle_goal,
            "Card": self._handle_card,
            "Substitution": self._handle_substitution,
            "Transfer": self._handle_transfer,
            "Round": self._handle_round

        }

    def sync_model(self, model_class, redis_prefix):
        try:
            records = model_class.query.all()
            count = 0
            model_name = model_class.__name__

            # Store all IDs for this model
            all_ids = [record.id for record in records]
            self.redis_service.set(f"{redis_prefix}:ids", all_ids)

            # Store total count
            self.redis_service.set(f"{redis_prefix}:count", len(all_ids))

            for record in records:
                # Model:id
                redis_key = f"{redis_prefix}:{record.id}"

                # Serialize datetime and date fields
                data = {}
                for c in record.__table__.columns:
                    value = getattr(record, c.name)
                    if isinstance(value, (datetime, date)):
                        value = value.isoformat()
                    data[c.name] = value

                # Store in Redis
                if self.redis_service.set(redis_key, data):
                    count += 1

                # Handle special cases using the handler dictionary
                if model_name in self.model_handlers:
                    self.model_handlers[model_name](record, redis_prefix)

            current_app.logger.info(f"Synced {count} {model_name} records to Redis")
            return count
        except Exception as e:
            current_app.logger.error(f"Error syncing {model_class.__name__}: {str(e)}")
            return 0

    def sync_all_models(self, models_to_sync):
        total = 0
        for model_class, redis_prefix in models_to_sync:
            count = self.sync_model(model_class, redis_prefix)
            total += count
        return total

    # Handler methods for different model types
    def _handle_season(self, record, redis_prefix):
        """Handle Season special relationships"""
        if hasattr(record, "tournament_id"):
            sorted_key = f"tournament:{record.tournament_id}:seasons_sorted"
            if hasattr(record, "start_date") and record.start_date:
                score = time.mktime(record.start_date.timetuple()) if isinstance(record.start_date,
                                                                                 (date, datetime)) else 0
                full_key = f"season:{record.id}"
                self.redis_service.add_to_sorted_set(sorted_key, full_key, score)

    def _handle_round(self, record, redis_prefix):
        """Handle Round special relationships"""
        # Get the full round key
        full_key = f"round:{record.id}"

        # Add round to season:id:all_rounds sorted set using round_number as score
        season_rounds_key = f"season:{record.season_id}:all_rounds"
        self.redis_service.add_to_sorted_set(season_rounds_key, full_key, record.round_number)

        # Track if round is finished
        if record.is_finished:
            finished_rounds_key = f"season:{record.season_id}:finished_rounds"
            finished_rounds = self.redis_service.get(finished_rounds_key) or []

            if isinstance(finished_rounds, str):
                finished_rounds = [finished_rounds]

            if full_key not in finished_rounds:
                finished_rounds.append(full_key)
                self.redis_service.set(finished_rounds_key, finished_rounds)

        # Get matches for this round if they exist
        from app.model.match import Match
        try:
            # Match using round_id which is the foreign key in the Match model
            matches = Match.query.filter(
                Match.season_id == record.season_id,
                Match.round_id == record.id
            ).all()

            # Create list of match keys
            match_keys = [f"match:{match.id}" for match in matches]

            # Store list of match keys for this round
            round_matches_key = f"round:{record.id}:matches"
            self.redis_service.set(round_matches_key, match_keys)

            # Also store reference in alternative format
            round_number_matches_key = f"season:{record.season_id}:round:{record.round_number}:matches"
            self.redis_service.set(round_number_matches_key, match_keys)

        except Exception as e:
            current_app.logger.error(f"Error handling round matches for round {record.id}: {str(e)}")

    def _handle_team_coach(self, record, redis_prefix):
        """Handle Team_Coach special relationships"""
        # Calculate score based on start_date
        if hasattr(record, "start_date") and record.start_date:
            if isinstance(record.start_date, str):
                start_date = datetime.fromisoformat(record.start_date)
            else:
                start_date = record.start_date
            score = time.mktime(start_date.timetuple())
        else:
            score = 0

        # Store full key name instead of just ID
        full_key = f"team_coach:{record.id}"

        # Team:id:team_coaches_sorted
        team_coaches_key = f"team:{record.team_id}:team_coaches_sorted"
        self.redis_service.add_to_sorted_set(team_coaches_key, full_key, score)

        # Coach:id:team_coaches_sorted
        coach_teams_key = f"coach:{record.coach_id}:team_coaches_sorted"
        self.redis_service.add_to_sorted_set(coach_teams_key, full_key, score)

        # Season:id:team_coaches_sorted
        season_teams_key = f"season:{record.season_id}:team_coaches_sorted"
        self.redis_service.add_to_sorted_set(season_teams_key, full_key, score)

    def _handle_team_season_ranking(self, record, redis_prefix):
        """Handle Team_Season_Ranking special relationships"""
        # Store the actual ranking record with a consistent key
        full_key = f"team_season_ranking:{record.team_id}:{record.season_id}"

        # Create data dictionary with all record fields
        ranking_data = {}
        for c in record.__table__.columns:
            value = getattr(record, c.name)
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
            ranking_data[c.name] = value

        # Store the full ranking data in Redis
        self.redis_service.set(full_key, ranking_data)

        # Team:id:rankings - track all rankings for this team
        team_rankings_key = f"team:{record.team_id}:rankings"
        team_rankings = self.redis_service.get(team_rankings_key) or []
        # Convert string to list if needed
        if isinstance(team_rankings, str):
            team_rankings = [team_rankings]

        if full_key not in team_rankings:
            team_rankings.append(full_key)
            self.redis_service.set(team_rankings_key, team_rankings)

        # Season:id:rankings_sorted - for leaderboard sorting
        season_rankings_key = f"season:{record.season_id}:rankings_sorted"
        score = record.ranking  # Get ranking directly from record
        self.redis_service.add_to_sorted_set(season_rankings_key, full_key, score)

        # Season:id:leaderboard_by_points - alternative sorting by points
        points_key = f"season:{record.season_id}:leaderboard_by_points"
        self.redis_service.add_to_sorted_set(points_key, full_key, record.points)

        # Season:id:teams - track all teams in this season
        season_team_key = f"season:{record.season_id}:all_team"
        full_team_key = f"team:{record.team_id}"
        season_teams = self.redis_service.get(season_team_key) or []
        # Convert string to list if needed
        if isinstance(season_teams, str):
            season_teams = [season_teams]

        if full_team_key not in season_teams:
            season_teams.append(full_team_key)
            self.redis_service.set(season_team_key, season_teams)

    def _handle_player_team(self, record, redis_prefix):
        """Handle Player_Team special relationships"""
        # Team:{team.id}:{season:id}:players
        team_players_key = f"team:{record.team_id}:{record.season_id}:players"
        player_key = f"player:{record.player_id}"

        team_players = self.redis_service.get(team_players_key) or []
        if player_key not in team_players:
            team_players.append(player_key)
            self.redis_service.set(team_players_key, team_players)

    def _handle_match(self, record, redis_prefix):
        """Handle Match special relationships"""
        match_key = f"match:{record.id}"
        match_date = 0

        # Get score based on match date
        if hasattr(record, "match_date") and record.match_date:
            if isinstance(record.match_date, str):
                match_date = time.mktime(datetime.fromisoformat(record.match_date).timetuple())
            else:
                match_date = time.mktime(record.match_date.timetuple())

        # Recent matches by team and season
        for team_id in [record.home_team_id, record.away_team_id]:
            # team:{team_id}:season:{season_id}:recent_matches
            recent_matches_key = f"team:{team_id}:season:{record.season_id}:recent_matches"
            self.redis_service.add_to_sorted_set(recent_matches_key, match_key, match_date)

            # team:{team_id}:recent_matches
            all_matches_key = f"team:{team_id}:recent_matches"
            self.redis_service.add_to_sorted_set(all_matches_key, match_key, match_date)

        # Matches by round
        if hasattr(record, "round") and record.round:
            round_matches_key = f"season:{record.season_id}:round:{record.round}:matches"
            round_matches = self.redis_service.get(round_matches_key) or []
            if match_key not in round_matches:
                round_matches.append(match_key)
                self.redis_service.set(round_matches_key, round_matches)

    def _handle_lineup(self, record, redis_prefix):
        """Handle Lineup (Match_Player) special relationships"""
        # match:{match.id}:team:{team.id}:players
        match_players_key = f"match:{record.match_id}:team:{record.team_id}:players"
        player_key = f"player:{record.player_id}"

        # Add to set of players in the match
        match_players = self.redis_service.get(match_players_key) or []
        if player_key not in match_players:
            match_players.append(player_key)
            self.redis_service.set(match_players_key, match_players)

        # Additional handling for starting lineup vs substitutes
        if record.is_starting:
            # Track starting lineup separately
            starting_lineup_key = f"match:{record.match_id}:team:{record.team_id}:starting_lineup"
            starting_lineup = self.redis_service.get(starting_lineup_key) or []
            if player_key not in starting_lineup:
                starting_lineup.append(player_key)
                self.redis_service.set(starting_lineup_key, starting_lineup)

        # Track player entry time
        if record.time_in is not None:
            entry_times_key = f"match:{record.match_id}:team:{record.team_id}:entry_times"
            self.redis_service.add_to_sorted_set(entry_times_key, player_key, record.time_in)

        # Track player exit time
        if record.time_out is not None:
            exit_times_key = f"match:{record.match_id}:team:{record.team_id}:exit_times"
            self.redis_service.add_to_sorted_set(exit_times_key, player_key, record.time_out)

        # Track player minutes played
        if record.time_in is not None and record.time_out is not None:
            minutes_played = record.time_out - record.time_in
            player_minutes_key = f"match:{record.match_id}:player_minutes"
            self.redis_service.hset(player_minutes_key, player_key, minutes_played)

    def _handle_goal(self, record, redis_prefix):
        """Handle Goal special relationships"""
        # match:{match.id}:goals
        match_goals_key = f"match:{record.match_id}:goals"
        player_key = f"player:{record.player_id}"

        # Use minute as score for sorting
        score = record.minute if hasattr(record, "minute") else 0
        self.redis_service.add_to_sorted_set(match_goals_key, player_key, score)

        # Update player goal statistics
        if hasattr(record, "season_id"):
            # Update season goals
            player_season_goals_key = f"player:{record.player_id}:season:{record.season_id}:goals"
            goals_count = self.redis_service.get(player_season_goals_key) or 0
            self.redis_service.set(player_season_goals_key, goals_count + 1)

            # Update career goals
            player_career_goals_key = f"player:{record.player_id}:career:goals"
            career_goals = self.redis_service.get(player_career_goals_key) or 0
            self.redis_service.set(player_career_goals_key, career_goals + 1)

            # Update season top scorers
            season_scorers_key = f"season:{record.season_id}:top_scorers"
            self.redis_service.add_to_sorted_set(season_scorers_key, player_key, goals_count + 1)



    def _handle_card(self, record, redis_prefix):
        """Handle Card special relationships"""
        # match:{match_id}:cards
        match_cards_key = f"match:{record.match_id}:cards"
        player_key = f"player:{record.player_id}"

        # Use minute as score for sorting
        score = record.minute if hasattr(record, "minute") else 0
        self.redis_service.add_to_sorted_set(match_cards_key, player_key, score)

        # Update player card statistics
        if hasattr(record, "season_id") and hasattr(record, "card_type"):
            card_type = record.card_type.lower()  # 'yellow' or 'red'
            player_season_cards_key = f"player:{record.player_id}:season:{record.season_id}:{card_type}_cards"
            cards_count = self.redis_service.get(player_season_cards_key) or 0
            self.redis_service.set(player_season_cards_key, cards_count + 1)

    def _handle_substitution(self, record, redis_prefix):
        """Handle Substitution special relationships"""
        # match:{match_id}:substitutions
        match_subs_key = f"match:{record.match_id}:substitutions"

        # Create an ID for the substitution event
        sub_key = f"substitution:{record.id}"

        # Use minute as score for sorting
        score = record.minute if hasattr(record, "minute") else 0
        self.redis_service.add_to_sorted_set(match_subs_key, sub_key, score)

    def _handle_transfer(self, record, redis_prefix):
        """Handle Transfer special relationships"""
        transfer_key = f"transfer:{record.id}"

        # Get score based on transfer date
        if hasattr(record, "transfer_date") and record.transfer_date:
            if isinstance(record.transfer_date, str):
                transfer_date = time.mktime(datetime.fromisoformat(record.transfer_date).timetuple())
            else:
                transfer_date = time.mktime(record.transfer_date.timetuple())
        else:
            transfer_date = 0

        # player:{player_id}:transfers
        player_transfers_key = f"player:{record.player_id}:transfers"
        team_key = f"team:{record.destination_team_id}"
        self.redis_service.add_to_sorted_set(player_transfers_key, team_key, transfer_date)

        # team:{team_id}:season:{season_id}:transfers
        if hasattr(record, "season_id"):
            team_transfers_key = f"team:{record.destination_team_id}:season:{record.season_id}:transfers"
            player_key = f"player:{record.player_id}"
            self.redis_service.add_to_sorted_set(team_transfers_key, player_key, transfer_date)