from pydantic import BaseSettings, SecretStr, HttpUrl, env_settings


class Settings(BaseSettings):
    email: str
    password: SecretStr
    auth_url: HttpUrl = 'https://auth.chat.arnor.dev/graphql'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
