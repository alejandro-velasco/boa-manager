import boa_manager.db
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base



class Database:
    def __init__(self) -> None:
        self.username=os.getenv('DB_USERNAME')
        self.password=os.getenv('DB_PASSWORD')
        self.hostname=os.getenv('DB_HOSTNAME')
        self.port=os.getenv('DB_PORT')
        self.database=os.getenv('DB_NAME')
        self.engine = create_engine(f'postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}')
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=False,
                                                   bind=self.engine))          
database = Database()
Base = declarative_base()
Base.query = database.session.query_property()

def init_db(base=Base):
    base.metadata.create_all(bind=database.engine)