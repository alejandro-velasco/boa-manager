from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Text,
    ForeignKey,
    Table,
    Index,
    Engine
)
from boa_manager.db.database import Base

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return f'<Organization {self.name!r}>'

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    organization_id = Column("organization_id", ForeignKey("organizations.id"))
    cluster_id = Column("cluster_id", ForeignKey("clusters.id"))

    def __init__(self, name=None, organization_id=None, cluster_id=None):
        self.name = name
        self.organization_id = organization_id
        self.cluster_id = cluster_id

    def __repr__(self):
        return f'<job {self.name!r}>'
    
class OrganizationUniqueIndex():
    def __init__(self, id: int, engine: Engine) -> None:
        self.id = id
        self.index = Index(f'unique_org_jobs_{self.id}', Job.name, unique=True, postgresql_where=Job.organization_id == self.id)
        self.engine = engine

    def create(self):
        self.index.create(self.engine)

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