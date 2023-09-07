from sqlalchemy import (
    Column, 
    Integer, 
    String,
    Index,
    Engine
)

from boa_manager.db.database import Base
from boa_manager.db.models.jobs import Job

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return f'<Organization {self.name!r}>'
    
class OrganizationUniqueIndex():
    def __init__(self, id: int, engine: Engine) -> None:
        self.id = id
        self.index = Index(f'unique_org_jobs_{self.id}', 
                           Job.name, 
                           unique=True, 
                           postgresql_where=Job.organization_id == self.id)
        self.engine = engine

    def create(self):
        self.index.create(self.engine)

    def drop(self):
        self.index.drop(self.engine)