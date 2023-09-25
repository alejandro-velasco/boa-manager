from sqlalchemy import (
    Column, 
    Integer, 
    String,
    Index,
    Text,
    Engine
)

from boa_manager.db.database import Base
from boa_manager.db.models.jobs import Job
from boa_manager.utils.string_utils import rfc_1123_str

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    rfc_1123_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, unique=False, nullable=False, default='')

    def __init__(self, name=None, description=None):
        self.name = name,
        self.rfc_1123_name = rfc_1123_str(name)
        self.description = description

    def __repr__(self):
        return f'<Organization {self.name!r}>'
    
class OrganizationUniqueIndex():
    def __init__(self, id: int, engine: Engine) -> None:
        self.id = id
        self.index = Index(f'unique_org_jobs_{self.id}', 
                           Job.name,
                           Job.rfc_1123_name, 
                           unique=True, 
                           postgresql_where=Job.organization_id == self.id)
        self.engine = engine

    def create(self):
        self.index.create(self.engine)

    def drop(self):
        self.index.drop(self.engine)