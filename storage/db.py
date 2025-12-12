from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from config import SQLITE_DB_PATH

engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
