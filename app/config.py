from pydantic import BaseSettings


# class for reading enviroment variables into that are converted to settings for our app
class Settings(BaseSettings):
    db_hostname: str
    db_port: str
    db_password: str
    db_name: str
    db_username: str
    secret_key: str
    algorithm: str
    token_expire_minutes: int

    class Config:
        env_file = '.env'
    # automatically searches the given file and assigns values to the properties above


settings = Settings()
