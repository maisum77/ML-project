from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = True
    api_rate_limit: int = 100
    api_key_secret: str = "change_this_to_a_random_secret"

    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "SocialPulseAI/1.0"

    x_api_key: str = ""
    x_api_secret: str = ""
    x_access_token: str = ""
    x_access_token_secret: str = ""
    x_bearer_token: str = ""

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "socialpulse_ai"

    redis_url: str = "redis://localhost:6379/0"

    google_fact_check_api_key: str = ""
    claimbuster_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
