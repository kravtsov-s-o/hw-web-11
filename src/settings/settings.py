from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings
    """
    postgres_name: str = 'postgres'
    postgres_host: str = 'host'
    postgres_port: int = 5672
    postgres_user: str = 'user'
    postgres_password: str = 'password'
    postgres_database_url: str = 'postgresql+psycopg2://user:password@host:5672/postgres'
    secret_key: str = 'secret_key'
    algorithm: str = 'algorithm'
    mail_username: str = 'mail_username'
    mail_password: str = 'mail_password'
    mail_from: str = 'mail@mail.loc'
    mail_port: int = 5672
    mail_server: str = 'mail_server'
    redis_host: str = 'redis'
    redis_port: int = 6379
    cloudinary_name: str = 'cloudinary'
    cloudinary_api_key: int = 1234567889
    cloudinary_api_secret: str = 'cloudinary_secret'

    class Config:
        """
        Config env
        """
        env_file = ".env"
        env_file_encoding = "UTF-8"


settings = Settings()
