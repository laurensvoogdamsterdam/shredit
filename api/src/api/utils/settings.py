from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment variables
    auth0_secret: str
    auth0_base_url: str
    auth0_issuer_base_url: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_audience: str
    auth0_domain: str
    auth0_api_audience: str
    auth0_issuer: str
    auth0_algorithms: str

    class Config:
        # Specify that the environment variables will be loaded from a `.env` file
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
