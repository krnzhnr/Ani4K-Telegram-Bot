from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime, timezone, timedelta

from config_reader import config

# Определим часовой пояс для Беларуси
belarus_timezone = timezone(timedelta(hours=3))

# Инициализация базы данных
# engine = create_async_engine(config.database_url, echo=True)
# Base = declarative_base()
# async_session = async_sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     future=True
# )

# Инициализация базы данных SQLite
engine = create_async_engine(
    config.database_url, 
    echo=False,
    connect_args={"check_same_thread": False}  # Эта опция нужна для SQLite
)

Base = declarative_base()

# Инициализация асинхронной сессии
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True
)


# Вспомогательная таблица для связи "многие ко многим"
anime_genre_association = Table(
    "anime_genre_association",
    Base.metadata,
    Column("anime_id", Integer, ForeignKey("anime.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True)
)


class Anime(Base):
    __tablename__ = "anime"
    id = Column(Integer, primary_key=True)
    poster_id = Column(String(255))
    release_name = Column(String(100), nullable=False)
    description = Column(Text)
    episodes_count = Column(Integer)
    dub = Column(String(50))
    dub_team = Column(String(100))
    hashtags = Column(Text)

    genres = relationship("Genre", secondary=anime_genre_association, back_populates="anime")
    episodes = relationship("Episode", back_populates="anime")
    # Связь с подписками
    subscriptions = relationship("Subscription", back_populates="anime", cascade="all, delete-orphan")


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    anime = relationship("Anime", secondary=anime_genre_association, back_populates="genres")


class Episode(Base):
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True)
    media_id = Column(String(255), nullable=False)
    episode_number = Column(Integer, nullable=False)
    anime_id = Column(Integer, ForeignKey('anime.id'), nullable=False)
    added_at = Column(DateTime, default=lambda: datetime.now(belarus_timezone))  # Время с учетом часового пояса

    anime = relationship("Anime", back_populates="episodes")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class User(Base):
    """
    Модель пользователя. Содержит информацию о пользователях, взаимодействующих с ботом.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # ID пользователя (Telegram user_id)
    first_name = Column(String, nullable=False)  # Имя пользователя
    last_name = Column(String, nullable=True)  # Фамилия пользователя
    full_name = Column(String, nullable=False)  # Полное имя пользователя
    username = Column(String, nullable=True)  # Username пользователя
    first_interaction_date = Column(DateTime, default=lambda: datetime.now(belarus_timezone), nullable=False)  # Дата первого взаимодействия
    last_interaction_date = Column(DateTime, default=lambda: datetime.now(belarus_timezone), onupdate=lambda: datetime.now(belarus_timezone), nullable=False)  # Дата последнего взаимодействия
    subscriptions_last_updated = Column(DateTime, default=None, nullable=True)  # Последнее обновление подписок

    # Связь с подписками
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


class Subscription(Base):
    """
    Модель подписки. Связывает пользователей и аниме, на которые они подписаны.
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)  # Уникальный ID записи
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # ID пользователя
    anime_id = Column(Integer, ForeignKey("anime.id", ondelete="CASCADE"), nullable=False)  # ID аниме
    subscribed_at = Column(DateTime, default=lambda: datetime.now(belarus_timezone), nullable=False)  # Дата подписки

    # Связи с пользователями и аниме
    user = relationship("User", back_populates="subscriptions")
    anime = relationship("Anime", back_populates="subscriptions")