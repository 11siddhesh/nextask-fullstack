from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    # This tells Pydantic to look for the .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # This must perfectly match the variable name in your .env file
    DB_CONNECTION: str 
    SECRET_KEY: str
    ALGORITHM: str 
    EXP_TIME: int

    # --- ADD THESE TWO LINES ---
    EMAIL_SENDER: str
    EMAIL_PASSWORD: str

# Create an object we can import into other files
settings = Settings()

