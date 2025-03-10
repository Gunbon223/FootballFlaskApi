from flask import current_app
from app.service.redis_service import RedisService
from appdb import db
import time
import json
from datetime import date, datetime


class DBSyncService:
    def __init__(self):
        self.redis_service = RedisService.get_instance()

    def sync_model(self, model_class, redis_prefix):
        try:
            records = model_class.query.all()
            count = 0

            # Store all IDs for this model
            all_ids = [record.id for record in records]
            self.redis_service.set(f"{redis_prefix}:ids", all_ids)

            # Store total count
            self.redis_service.set(f"{redis_prefix}:count", len(all_ids))

            for record in records:
                # Generate Redis key
                redis_key = f"{redis_prefix}:{record.id}"

                # Serialize and store record
                data = {}
                for c in record.__table__.columns:
                    value = getattr(record, c.name)
                    if isinstance(value, (datetime, date)):
                        value = value.isoformat()
                    data[c.name] = value

                # Store in Redis
                if self.redis_service.set(redis_key, data):
                    count += 1

                if model_class.__name__ == "Season" and hasattr(record, "tournament_id"):
                    # Sorted set by time
                    sorted_key = f"tournament:{record.tournament_id}:seasons_sorted"
                    if hasattr(record, "end_date") and record.end_date:
                        # Use timestamp as score (negative for descending order)
                        score = time.mktime(record.end_date.timetuple()) if isinstance(record.end_date, (date, datetime)) else 0
                        self.redis_service.add_to_sorted_set(sorted_key, record.id, score)
                # For Team Coach
                elif model_class.__name__ == "Team_Coach":

                    # Handle Team_Coach relationships (3-way relationship)
                    # Team to Team_Coach relationship
                    team_coaches_key = f"team:{record.team_id}:team_coaches"
                    team_coaches = self.redis_service.get(team_coaches_key) or []
                    if record.id not in team_coaches:
                        team_coaches.append(record.id)
                        self.redis_service.set(team_coaches_key, team_coaches)

                    # Coach to Team_Coach relationship
                    coach_teams_key = f"coach:{record.coach_id}:team_coaches"
                    coach_teams = self.redis_service.get(coach_teams_key) or []
                    if record.id not in coach_teams:
                        coach_teams.append(record.id)
                        self.redis_service.set(coach_teams_key, coach_teams)

                    # Season to Team_Coach relationship
                    season_teams_key = f"season:{record.season_id}:team_coaches"
                    season_teams = self.redis_service.get(season_teams_key) or []
                    if record.id not in season_teams:
                        season_teams.append(record.id)
                        self.redis_service.set(season_teams_key, season_teams)


                    # For Player Team Season
                    elif model_class.__name__ == "Team_Season_Ranking":
                        # Team to Team_Season_Ranking relationship
                        team_rankings_key = f"team:{record.team_id}:rankings"
                        team_rankings = self.redis_service.get(team_rankings_key) or []
                        if record.id not in team_rankings:
                            team_rankings.append(record.id)
                            self.redis_service.set(team_rankings_key, team_rankings)

                        # Season to Team_Season_Ranking relationship
                        season_rankings_key = f"season:{record.season_id}:rankings"
                        season_rankings = self.redis_service.get(season_rankings_key) or []
                        if record.id not in season_rankings:
                            season_rankings.append(record.id)
                            self.redis_service.set(season_rankings_key, season_rankings)



            current_app.logger.info(f"Synced {count} {model_class.__name__} records to Redis")
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
