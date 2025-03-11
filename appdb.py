import os

from flask_sqlalchemy import SQLAlchemy
import redis

db = SQLAlchemy()

# Redis Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')  # Changed port to default Redis port
REDIS_EXPIRATION = 86400  # Cache expiration in seconds (24 hours)

# If Redis is unavailable, set this to True to use SQL directly
USE_SQL_FALLBACK = True
