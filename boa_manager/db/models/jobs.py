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
    repo_url = Column(String(100), nullable=False)
    branch = Column(String(50), nullable=True)
    file_path = Column(String(50), nullable=True)
    image = Column(String(50), nullable=False)
    log_level = Column(String(50), nullable=True)
    organization_id = Column("organization_id", ForeignKey("organizations.id"))
    cluster_id = Column("cluster_id", ForeignKey("clusters.id"))

    def __init__(self, 
                 name=None, 
                 organization_id=None, 
                 cluster_id=None, 
                 repo_url=None,
                 branch=None,
                 file_path=None,
                 image=None,
                 log_level=None):
        
        self.name = name
        self.organization_id = organization_id
        self.cluster_id = cluster_id
        self.repo_url = repo_url
        self.branch = branch
        self.file_path = file_path
        self.image = image
        self.log_level = log_level

    def __repr__(self):
        return f'<job {self.name!r}>'