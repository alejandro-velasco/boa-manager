from sqlalchemy import (
    Column, 
    Integer, 
    String,
    ForeignKey
)

from boa_manager.db.database import Base
from boa_manager.utils.string_utils import rfc_1123_str

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    rfc_1123_name = Column(String(50), nullable=False)
    repo_url = Column(String(100), nullable=False)
    branch = Column(String(50), nullable=False, default='main')
    file_path = Column(String(50), nullable=False, default='boa.yaml')
    image = Column(String(50), nullable=False, default='boa-client:latest')
    log_level = Column(String(50), nullable=False, default='INFO')
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
        self.rfc_1123_name = rfc_1123_str(name)
        self.organization_id = organization_id
        self.cluster_id = cluster_id
        self.repo_url = repo_url
        self.branch = branch
        self.file_path = file_path
        self.image = image
        self.log_level = log_level

    def __repr__(self):
        return f'<job {self.name!r}>'
    

class JobExecution(Base):
    __tablename__ = 'job_execution_history'
    id = Column(Integer, primary_key=True)
    organization_id = Column("organization_id", ForeignKey("organizations.id"))
    job_id = Column("job_id", ForeignKey("jobs.id"))
    execution_id = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)

    def __init__(self,
                 organization_id=None,
                 job_id=None,
                 execution_id=None, 
                 status=None):
        self.organization_id = organization_id
        self.job_id = job_id
        self.execution_id = execution_id
        self.status = status

    def __repr__(self):
        return f'<job execution {self.execution_id!r}>'