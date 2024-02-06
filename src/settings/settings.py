from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings
    """
    postgres_name: str
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str
    redis_port: int
    cloudinary_name: str
    cloudinary_api_key: int
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "UTF-8"


settings = Settings()
