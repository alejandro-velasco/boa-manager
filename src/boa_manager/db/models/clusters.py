from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Text
)

from boa_manager.db.database import Base

class Cluster(Base):
    __tablename__ = 'clusters'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    server_url = Column(String(50), unique=False, nullable=False)
    certificate_authority = Column(Text, unique=False, nullable=False)
    token = Column(Text, unique=False, nullable=False)

    def __init__(self, name=None, server_url=None, certificate_authority=None, token=None):
        self.name = name
        self.server_url = server_url
        self.certificate_authority = certificate_authority
        self.token = token

    def __repr__(self):
        return f'<Cluster {self.name!r}>'