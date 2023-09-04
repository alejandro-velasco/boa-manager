from sqlalchemy import (
    Column, 
    Integer, 
    String,
    ForeignKey
)

from boa_manager.db.database import Base

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