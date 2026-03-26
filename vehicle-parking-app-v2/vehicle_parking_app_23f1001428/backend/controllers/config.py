class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vehicle.db'
    SECRET_KEY = 'my_secret_key'
    SECURITY_PASSWORD_SALT = 'my_salt_pwd'
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300
