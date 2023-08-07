from sqlalchemy import create_engine
from sqlalchemy.engine import URL


class Session:

    def __init__(self, host='127.0.0.1:5432', username='postgres', database='boa') -> None:
        self.engine = create_engine(
            URL.create(
                drivername="postgresql",
                username=username,
                host=host,
                database=database
            )
        )
        