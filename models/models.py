from sqlalchemy import Column, Integer, String, Text, ForeignKey
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
    
    seasons = relationship("Season", back_populates="anime")

class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    anime_id = Column(Integer, ForeignKey('anime.id'))
    
    anime = relationship("Anime", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season")

class Episode(Base):
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    episode_number = Column(Integer)
    season_id = Column(Integer, ForeignKey('seasons.id'))
    
    season = relationship("Season", back_populates="episodes")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
