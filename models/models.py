from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config_reader import config

# Инициализация базы данных
engine = create_async_engine(config.database_url, echo=True)
Base = declarative_base()
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
    episodes = Column(String(50))
    dub = Column(String(50))
    dub_team = Column(String(100))
    hashtags = Column(Text)

    # Связь с жанрами
    genres = relationship("Genre", secondary=anime_genre_association, back_populates="anime")

class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    anime = relationship("Anime", secondary=anime_genre_association, back_populates="genres")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
