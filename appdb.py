import os

from flask_sqlalchemy import SQLAlchemy
import redis

db = SQLAlchemy()

# Redis Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6382/0')
REDIS_EXPIRATION = 86400

USE_SQL_FALLBACK = False
