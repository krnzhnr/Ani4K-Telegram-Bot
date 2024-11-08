from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Токен бота — сохраняем его как SecretStr для безопасности
    bot_token: SecretStr
    
    # Добавляем параметр для подключения к базе данных (DATABASE_URL)
    database_url: str  # Просто строка, потому что мы не скрываем её (не секретная информация)

    # В модели настроек указываем файл .env для загрузки и его кодировку
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# При импорте файла будет создан и провалидирован объект конфигурации
# Этот объект можно будет использовать в разных местах кода
config = Settings()
