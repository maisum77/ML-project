from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = True
    api_rate_limit: int = 100
    api_key_secret: str = "change_this_to_a_random_secret"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"

    dynamodb_raw_posts_table: str = "socialpulse_raw_posts"
    dynamodb_cleaned_posts_table: str = "socialpulse_cleaned_posts"
    dynamodb_trends_table: str = "socialpulse_trends"
    dynamodb_sentiment_table: str = "socialpulse_sentiment"
    dynamodb_fact_checks_table: str = "socialpulse_fact_checks"
    dynamodb_propagation_table: str = "socialpulse_propagation"

    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "SocialPulseAI/1.0"

    x_api_key: str = ""
    x_api_secret: str = ""
    x_access_token: str = ""
    x_access_token_secret: str = ""
    x_bearer_token: str = ""

    google_fact_check_api_key: str = ""
    claimbuster_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
