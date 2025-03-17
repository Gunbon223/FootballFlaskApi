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
                # Model:id
                redis_key = f"{redis_prefix}:{record.id}"
                # Serialize datetime and date fields
                data = {}
                for c in record.__table__.columns:
                    value = getattr(record, c.name)
                    if isinstance(value, (datetime, date)):
                        value = value.isoformat()
                    data[c.name] = value

                if self.redis_service.set(redis_key, data):
                    count += 1

                if model_class.__name__ == "Season" and hasattr(record, "tournament_id"):
                    # Tournament:id:seasons_sorted
                    sorted_key = f"tournament:{record.tournament_id}:seasons_sorted"
                    if hasattr(record, "start_date") and record.start_date:
                        score = time.mktime(record.start_date.timetuple()) if isinstance(record.start_date,
                                                                                         (date, datetime)) else 0
                        # Store full key name instead of just ID
                        full_key = f"season:{record.id}"
                        self.redis_service.add_to_sorted_set(sorted_key, full_key, score)
                # Team Coach
                elif model_class.__name__ == "Team_Coach":
                    # Team:id:team_coaches_sorted
                    team_coaches_key = f"team:{record.team_id}:team_coaches_sorted"
                    if hasattr(record, "start_date") and record.start_date:
                        if isinstance(record.start_date, str):
                            start_date = datetime.fromisoformat(record.start_date)
                        else:
                            start_date = record.start_date
                        score = time.mktime(start_date.timetuple())

                    # Store full key name instead of just ID
                    full_key = f"team_coach:{record.id}"
                    self.redis_service.add_to_sorted_set(team_coaches_key, full_key, score)

                    # Coach:id:team_coaches_sorted
                    coach_teams_key = f"coach:{record.coach_id}:team_coaches_sorted"
                    self.redis_service.add_to_sorted_set(coach_teams_key, full_key, score)

                    # Season:id:team_coaches_sorted
                    season_teams_key = f"season:{record.season_id}:team_coaches_sorted"
                    self.redis_service.add_to_sorted_set(season_teams_key, full_key, score)

                # For Player Team Season
                elif model_class.__name__ == "Team_Season_Ranking":
                    # Team:id:rankings
                    team_rankings_key = f"team:{record.team_id}:rankings"
                    team_rankings = self.redis_service.get(team_rankings_key) or []

                    # Store full key name instead of just ID
                    full_key = f"team_season_ranking:{record.id}"
                    if full_key not in team_rankings:
                        team_rankings.append(full_key)
                        self.redis_service.set(team_rankings_key, team_rankings)

                    # Season:id:rankings_sorted
                    season_rankings_key = f"season:{record.season_id}:rankings_sorted"
                    score = record.ranking  # Get ranking directly from record
                    self.redis_service.add_to_sorted_set(season_rankings_key, full_key, score)

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
