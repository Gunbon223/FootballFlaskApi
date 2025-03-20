from flask import current_app
from app.service.redis_service import RedisService
from appdb import db
from datetime import date


class BaseRepository:
    def __init__(self, model_class, redis_key_prefix):
        self.model_class = model_class
        self.redis_key_prefix = redis_key_prefix
        self.redis_service = RedisService.get_instance()

    def _make_redis_key(self, id):
        """Generate Redis key from prefix and ID"""
        return f"{self.redis_key_prefix}:{id}"

    def _serialize_model(self, model):
        """Convert model to dictionary for Redis storage"""
        if hasattr(model, 'to_dict'):
            # Use model's own serialization method if available
            return model.to_dict()

        # Custom serialization with date handling
        data = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            # Convert date objects to ISO format strings
            if isinstance(value, date):
                value = value.isoformat()
            data[column.name] = value
        return data

    def _deserialize_model(self, data):
        """Convert dictionary to model instance"""
        if not data:
            return None
        return self.model_class(**data)

    def get_by_id(self, id):
        """Get entity by ID - try Redis first, then SQL if not found"""
        redis_key = self._make_redis_key(id)

        # Try Redis first
        data = self.redis_service.get(redis_key)
        if data:
            current_app.logger.debug(f"Retrieved from Redis: {redis_key}")
            return self._deserialize_model(data)
        return None

    def get(self,redis_key):
        data = self.redis_service.get(redis_key)
        if data:
            return self._deserialize_model(data)
        return None

    def save(self, entity):
        """Save entity to both Redis and SQL"""
        try:
            # Save to SQL
            db.session.add(entity)
            db.session.commit()

            # Save to Redis
            redis_key = self._make_redis_key(entity.id)
            self.redis_service.set(redis_key, self._serialize_model(entity))

            return entity
        except Exception as e:
            current_app.logger.error(f"Error saving entity: {str(e)}")
            db.session.rollback()
            return None

    def update(self, entity):
        """Update entity in both Redis and SQL"""
        try:
            # Update SQL
            db.session.commit()

            # Update Redis
            redis_key = self._make_redis_key(entity.id)
            self.redis_service.set(redis_key, self._serialize_model(entity))

            return entity
        except Exception as e:
            current_app.logger.error(f"Error updating entity: {str(e)}")
            db.session.rollback()
            return None

    def delete(self, id):
        """Delete entity from both Redis and SQL"""
        try:
            # Delete from Redis
            redis_key = self._make_redis_key(id)
            self.redis_service.delete(redis_key)

            # Delete from SQL
            entity = self.model_class.query.get(id)
            if entity:
                db.session.delete(entity)
                db.session.commit()

            return True
        except Exception as e:
            current_app.logger.error(f"Error deleting entity: {str(e)}")
            return False

    def search(self, query):
        """Search entities by name or other attributes with Redis caching"""
        try:
            # Create a unique Redis key for this search query
            query_str = "_".join([f"{k}:{v}" for k, v in query.items()])
            redis_key = f"{self.redis_key_prefix}:search:{query_str}"

            # Try Redis first
            cached_results = self.redis_service.get(redis_key)
            if cached_results:
                return [self._deserialize_model(item) for item in cached_results]

            # Fall back to database if not in cache
            entities = self.model_class.query.filter_by(**query).all()

            # Cache the results
            if entities:
                serialized_results = [self._serialize_model(entity) for entity in entities]
                self.redis_service.set(redis_key, serialized_results, expire=3600)  # 1 hour expiration

            return entities
        except Exception as e:
            current_app.logger.error(f"Error searching entities: {str(e)}")
            return []

    def get_all_paginated(self, page, per_page, order_by=None, sort_order="asc"):
        """Get paginated entities with Redis as primary data source"""
        try:
            # Normalize parameters
            sort_order = sort_order.lower() if sort_order else "asc"
            if sort_order not in ["asc", "desc"]:
                sort_order = "asc"
            # Define Redis keys
            count_key = f"{self.redis_key_prefix}:count"
            sorted_key = f"{self.redis_key_prefix}:sorted:{order_by}:{sort_order}"

            # Check if data exists in Redis
            count = self.redis_service.get(count_key)
            if count is None:
                # Load data from SQL into Redis
                self._load_all_to_redis()
                count = self.redis_service.get(count_key) or 0

            # Adjust per_page if needed
            if per_page > count and count > 0:
                per_page = count

            # Calculate offsets
            offset = (page - 1) * per_page

            # Ensure sorted list exists
            if not self.redis_service.get(sorted_key):
                self._create_sorted_list(order_by, sort_order)

            # Get paginated IDs
            entity_ids = self.redis_service.get_sorted_range(sorted_key, offset, per_page)

            # Get actual entities
            entities = []
            for entity_id in entity_ids:
                entity_data = self.redis_service.get(self._make_redis_key(entity_id))
                if entity_data:
                    entities.append(self._deserialize_model(entity_data))

            return entities, count

        except Exception as e:
            current_app.logger.error(f"Redis error: {str(e)}")
            # Fall back to SQL only when Redis fails
            return self._get_from_sql_paginated(page, per_page, order_by, sort_order)

    def _load_all_to_redis(self):
        """Load all entities from SQL into Redis"""
        try:
            # Get all entities from SQL
            entities = self.model_class.query.all()
            count = len(entities)

            # Store count
            self.redis_service.set(f"{self.redis_key_prefix}:count", count)

            # Store all entity IDs
            entity_ids = [entity.id for entity in entities]
            self.redis_service.set(f"{self.redis_key_prefix}:ids", entity_ids)

            # Store individual entities
            for entity in entities:
                self.redis_service.set(
                    self._make_redis_key(entity.id),
                    self._serialize_model(entity)
                )

            return True
        except Exception as e:
            current_app.logger.error(f"Error loading to Redis: {str(e)}")
            return False

    def _create_sorted_list(self, order_by=None, sort_order="asc"):
        """Create a sorted list in Redis"""
        try:
            # Get all entity IDs
            entity_ids = self.redis_service.get(f"{self.redis_key_prefix}:ids")
            if not entity_ids:
                self._load_all_to_redis()
                entity_ids = self.redis_service.get(f"{self.redis_key_prefix}:ids") or []

            # Get all entities data
            entities_data = []
            for entity_id in entity_ids:
                data = self.redis_service.get(self._make_redis_key(entity_id))
                if data:
                    entities_data.append(data)

            # Sort entities
            reverse = sort_order == "desc"
            if order_by:
                entities_data.sort(
                    key=lambda x: x.get(order_by, 0) if order_by in x else 0,
                    reverse=reverse
                )
            else:
                # Default sort by ID
                entities_data.sort(
                    key=lambda x: x.get("id", 0),
                    reverse=reverse
                )

            # Extract sorted IDs
            sorted_ids = [entity.get("id") for entity in entities_data]

            # Store sorted list
            self.redis_service.set_list(
                f"{self.redis_key_prefix}:sorted:{order_by}:{sort_order}",
                sorted_ids
            )

            return True
        except Exception as e:
            current_app.logger.error(f"Error creating sorted list: {str(e)}")
            return False

    def _get_from_sql_paginated(self, page, per_page, order_by=None, sort_order="asc"):
        """SQL fallback for pagination"""
        try:
            offset = (page - 1) * per_page
            query = self.model_class.query

            # Apply ordering
            if order_by and hasattr(self.model_class, order_by):
                column = getattr(self.model_class, order_by)
                if sort_order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
            else:
                query = query.order_by(self.model_class.id)

            entities = query.limit(per_page).offset(offset).all()
            total = self.model_class.query.count()

            return entities, total
        except Exception as e:
            current_app.logger.error(f"SQL fallback error: {str(e)}")
            return [], 0