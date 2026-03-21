from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # Эти переменные Pydantic будет искать в файле .env
    bot_token: SecretStr
    openai_api_key: SecretStr
    chrome_user_dir_path: SecretStr

    # Настройка для чтения файла
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

# Создаем экземпляр, который будем использовать в боте
config = Settings()