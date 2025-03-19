from flask import current_app
from app.repository.base_repository import BaseRepository
from app.model.team_season_ranking import Team_Season_Ranking



class TeamSeasonRankingRepository(BaseRepository):
    def  __init__(self):
        super().__init__(Team_Season_Ranking, "team_season_ranking")

    def get_leaderboard(self, season_id,sort_order):
        """Get full leaderboard for a season from Redis"""
        try:
            self.update_leaderboard_sorted_list(season_id)
            sorted_key = f"season:{season_id}:rankings_sorted"

            # Get all team ranking keys from the sorted set
            if sort_order == "asc":
                ranking_keys = self.redis_service.get_from_sorted_set(sorted_key, 0, -1, False)
            else:
                ranking_keys = self.redis_service.get_from_sorted_set(sorted_key, 0, -1, True)
            print(ranking_keys)
            # If the sorted list doesn't exist yet, create it


            # Get full data for each ranking
            leaderboard = []
            for key in ranking_keys:
                ranking_data = self.redis_service.get(key)
                if ranking_data:
                    # Get team data to enhance the ranking information
                    team_key = f"team:{ranking_data.get('team_id')}"
                    team_data = self.redis_service.get(team_key) or {}

                    # Combine ranking and team data
                    entry = ranking_data.copy()
                    entry['team_name'] = team_data.get('name', 'Unknown')
                    leaderboard.append(entry)

            return leaderboard

        except Exception as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            return []

    def get_team_rankings(self, team_id):
        """Get all rankings for a specific team"""
        try:
            team_rankings_key = f"team:{team_id}:rankings"
            ranking_keys = self.redis_service.get(team_rankings_key)
            if not ranking_keys:
                current_app.logger.warning(f"No rankings found for team {team_id}")
                return []

            if isinstance(ranking_keys, str):
                ranking_keys = [ranking_keys]

            rankings = []
            for key in ranking_keys:
                ranking_data = self.redis_service.get(key)
                if not ranking_data:
                    current_app.logger.warning(f"No data found for ranking key: {key}")
                    continue

                season_id = ranking_data.get('season_id')
                if not season_id:
                    key_parts = key.split(':')
                    if len(key_parts) >= 3:
                        season_id = key_parts[2]

                season_data = self.redis_service.get(f"season:{season_id}")
                if season_data:
                    entry = ranking_data.copy()
                    entry['season_name'] = season_data.get('name')
                    rankings.append(entry)
                else:
                    rankings.append(ranking_data)

            return rankings

        except Exception as e:
            current_app.logger.error(f"Redis error in get_team_rankings: {str(e)}")
            return Team_Season_Ranking.query.filter_by(team_id=team_id).all()


    def update_leaderboard_sorted_list(self, season_id):
        """Update team rankings in Redis based on match results for a season."""
        try:
            # Get team keys for this season
            season_team_key = f"season:{season_id}:all_team"
            team_keys = self.redis_service.get(season_team_key)
            if not team_keys:
                current_app.logger.error(f"No teams found for season {season_id}")
                return False

            # Initialize team data
            teams_data = {}
            if isinstance(team_keys, str):
                team_keys = [team_keys]

            current_app.logger.info(f"Found {len(team_keys)} teams for season {season_id}")

            for team_key in team_keys:
                team_id = int(team_key.split(":")[1])
                teams_data[team_id] = {
                    'team_id': team_id,
                    'season_id': season_id,
                    'points': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'goals_for': 0,
                    'goals_against': 0,
                    'goal_difference': 0,
                    'matches_played': 0,
                    'ranking': 0
                }

            # Get all rounds for this season
            season_rounds_key = f"season:{season_id}:all_rounds"
            round_keys = self.redis_service.get_from_sorted_set(season_rounds_key, 0, -1) or []

            all_match_keys = []

            if round_keys:
                # Try both match storage formats
                for round_key in round_keys:
                    # Convert byte string to string if needed
                    if isinstance(round_key, bytes):
                        round_key_str = round_key.decode('utf-8')
                    else:
                        round_key_str = round_key

                    # Method 1: Try direct format - round:{id}:matches
                    round_matches_key = f"{round_key_str}:matches"
                    round_match_keys = self.redis_service.get(round_matches_key) or []

                    # Method 2: Try alternative format - season:{id}:round:{num}:matches
                    if not round_match_keys:
                        round_id = round_key_str.split(':')[1]
                        alt_matches_key = f"season:{season_id}:round:{round_id}:matches"
                        round_match_keys = self.redis_service.get(alt_matches_key) or []

                    if isinstance(round_match_keys, str):
                        round_match_keys = [round_match_keys]

                    all_match_keys.extend(round_match_keys)

                current_app.logger.info(f"Found {len(all_match_keys)} matches from rounds")

            # If still no matches, try direct season matches or database
            if not all_match_keys:
                # Try direct season matches
                matches_key = f"season:{season_id}:matches"
                direct_match_keys = self.redis_service.get(matches_key) or []

                if isinstance(direct_match_keys, str):
                    direct_match_keys = [direct_match_keys]

                if direct_match_keys:
                    all_match_keys = direct_match_keys
                    current_app.logger.info(f"Found {len(all_match_keys)} matches directly from season")
                else:
                    # Last resort - database query
                    from app.model.match import Match
                    try:
                        db_matches = Match.query.filter_by(season_id=season_id).all()
                        all_match_keys = [f"match:{match.id}" for match in db_matches]
                        current_app.logger.info(f"Found {len(all_match_keys)} matches from database")
                    except Exception as db_err:
                        current_app.logger.error(f"Database query failed: {str(db_err)}")

            # Process matches and update team statistics
            processed_matches = 0
            for match_key in all_match_keys:
                match = self.redis_service.get(match_key)
                if not match:
                    continue

                home_team_id = match.get('home_team_id')
                away_team_id = match.get('away_team_id')
                home_score = match.get('home_score', 0)
                away_score = match.get('away_score', 0)

                # Skip if teams not in our data
                if home_team_id not in teams_data or away_team_id not in teams_data:
                    continue

                # Update statistics
                home_team = teams_data[home_team_id]
                away_team = teams_data[away_team_id]

                home_team['matches_played'] += 1
                away_team['matches_played'] += 1
                home_team['goals_for'] += home_score
                home_team['goals_against'] += away_score
                away_team['goals_for'] += away_score
                away_team['goals_against'] += home_score

                # Update wins, losses, draws and points
                if home_score > away_score:
                    home_team['wins'] += 1
                    home_team['points'] += 3
                    away_team['losses'] += 1
                elif home_score < away_score:
                    away_team['wins'] += 1
                    away_team['points'] += 3
                    home_team['losses'] += 1
                else:
                    home_team['draws'] += 1
                    away_team['draws'] += 1
                    home_team['points'] += 1
                    away_team['points'] += 1

                processed_matches += 1

            current_app.logger.info(f"Processed {processed_matches} matches")

            # Calculate goal difference and update rankings
            for team_data in teams_data.values():
                team_data['goal_difference'] = team_data['goals_for'] - team_data['goals_against']

            # Sort teams
            sorted_teams = sorted(
                teams_data.values(),
                key=lambda x: (x['points'], x['goal_difference'], x['goals_for']),
                reverse=True
            )

            # Update rankings in Redis
            for i, team in enumerate(sorted_teams, 1):
                team['ranking'] = i
                team_id = team['team_id']
                full_key = f"team_season_ranking:{team_id}:{season_id}"

                self.redis_service.set(full_key, team)

                points_key = f"season:{season_id}:leaderboard_by_points"
                self.redis_service.add_to_sorted_set(points_key, full_key, team['points'])

                rankings_key = f"season:{season_id}:rankings_sorted"
                self.redis_service.add_to_sorted_set(rankings_key, full_key, team['ranking'])

            return True

        except Exception as e:
            current_app.logger.error(f"Error updating rankings: {str(e)}")
            return False