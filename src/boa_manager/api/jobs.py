import random
import string
import base64
import tempfile
from flask_restful import reqparse, Resource
from boa_manager.db.database import database
from boa_manager.db.models.jobs import (
    Job, 
    JobExecution
)
from boa_manager.db.models.organizations import Organization
from boa_manager.db.models.clusters import Cluster
from boa_manager.api.kubernetes import BoaK8SClient

class JobApi(Resource):
    def get(self, organization_name: str, job_name: str):

        # Get Job Id
        organization_id = Organization.query.filter(Organization.name == organization_name).one().id
        job_query = Job.query.filter(Job.name == job_name,
                               Job.organization_id == organization_id).one()
        response = {
            "id": job_query.id,
            "job_name": job_query.name,
            "organization_name": organization_name,
            "repo_url": job_query.repo_url,
            "branch": job_query.branch,
            "image": job_query.image,
            "file_path": job_query.file_path,
            "log_level": job_query.log_level
        }

        return response, 200
    
    def post(self, organization_name: str, job_name: str):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('image', required=True)
        parser.add_argument('cluster_name', required=True)
        parser.add_argument('repo_url', required=True)
        parser.add_argument('branch', required=False)
        parser.add_argument('file_path', required=False)
        parser.add_argument('log_level', required=False)
        args = parser.parse_args()

        # Get Organization Id and Cluster Id
        organization_id = Organization.query.filter(Organization.name == organization_name).one().id
        cluster_id = Cluster.query.filter(Cluster.name == args.cluster_name).one().id

        # Create Job in the Database
        job = Job(
            name=job_name,
            organization_id=organization_id,
            cluster_id=cluster_id,
            repo_url=args.repo_url,
            branch=args.branch,
            file_path=args.file_path,
            image=args.image,
            log_level=args.log_level
        )        

        # Commit to Database
        database.session.add(job)
        database.session.commit()

        job_query = job.query.filter(Job.name == job_name,
                                     Job.organization_id == organization_id).one()

        response = {
            "id": job_query.id,
            "job_name": job_query.name,
            "cluster_name": args.cluster_name,
            "organization_name": organization_name,
            "repo_url": job_query.repo_url,
            "branch": job_query.branch,
            "image": job_query.image,
            "file_path": job_query.file_path,
            "log_level": job_query.log_level
        }

        return response, 201
    
    def put(self, organization_name: str, job_name: str):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('image', required=True)
        parser.add_argument('cluster_name', required=True)
        parser.add_argument('repo_url', required=True)
        parser.add_argument('branch', required=False)
        parser.add_argument('file_path', required=False)
        parser.add_argument('log_level', required=False)
        args = parser.parse_args()

        # Get Organization Id and Cluster Id
        organization_id = Organization.query.filter(Organization.name == organization_name).one().id
        cluster_id = Cluster.query.filter(Cluster.name == args.cluster_name).one().id

        # Update Job in the Database
        database.session.query(Job).filter_by(name=job_name,
                                        organization_id=organization_id).update({'name': job_name,
                                                                                 'organization_id': organization_id,
                                                                                 'cluster_id': cluster_id,
                                                                                 'repo_url': args.repo_url,
                                                                                 'branch': args.branch,
                                                                                 'file_path': args.file_path,
                                                                                 'image': args.image,
                                                                                 'log_level': args.log_level})

        database.session.commit()

        job_query = Job.query.filter(Job.name == job_name,
                                     Job.organization_id == organization_id).one()

        response = {
            "id": job_query.id,
            "job_name": job_query.name,
            "cluster_name": args.cluster_name,
            "organization_name": organization_name,
            "repo_url": job_query.repo_url,
            "branch": job_query.branch,
            "image": job_query.image,
            "file_path": job_query.file_path,
            "log_level": job_query.log_level
        }

        return response, 201

    def delete(self, organization_name: str, job_name: str):

        # Drop Job Row
        organization_id = Organization.query.filter(Organization.name == organization_name).one().id
        row = Job.query.filter(Job.name == job_name,
                               Job.organization_id == organization_id).one()
        database.session.delete(row)
        database.session.commit() 
    
        return 200
    
class JobExecutionApi(Resource):
    def post(self, organization_name: str, job_name: str):

        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('server', required=True)
        args = parser.parse_args()

        # Generate Execution ID
        execution_id = ''.join(random.choices(string.ascii_lowercase +
                                              string.digits, k=10))

        # Query Cluster, Organization, and Job tables
        organization_id = Organization.query.filter(Organization.name == organization_name).one().id
        job_query = Job.query.filter(Job.name == job_name,
                                      Job.organization_id == organization_id).one()
        cluster_query = Cluster.query.filter(Cluster.id == job_query.cluster_id).one()

        # Get Cluster / Job table in the Database
        job_execution=JobExecution(job_id=job_query.id,
                                   organization_id=job_query.organization_id,
                                   execution_id=execution_id,
                                   status='Pending')

        # Commit Pending Execution to Database
        database.session.add(job_execution)
        database.session.commit()

        job_execution_query = job_execution.query.filter(JobExecution.execution_id == execution_id).one()

        f = tempfile.NamedTemporaryFile(mode='w+')

        try:
            # Write CA Certificate to Temporary File
            ca = base64.b64decode(cluster_query.certificate_authority).decode()
            f.write(ca)
            f.seek(0)

            # Create K8S Client / Workload
            client = BoaK8SClient(
                ca = f.name,
                server = cluster_query.server_url,
                token = cluster_query.token
            )

            client.create_pod(
                name=job_name,
                image=job_query.image,
                url=job_query.repo_url,
                execution_id=execution_id,
                organization_id=organization_id,
                server=args.server
            )
                
        finally:
            f.close()

        response = {
            "id": job_execution_query.id,
            "job_name": job_name,
            "execution_id": job_execution_query.execution_id,
            "organization_name": organization_name,
            "status": job_execution_query.status
        }

        return response, 200
    
class JobStatusApi(Resource):
    def put(self, execution_id: str):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('status', required=True) 
        args = parser.parse_args()

        # Get Cluster / Job table in the Database
        database.session.query(JobExecution).filter_by(execution_id=execution_id).update({'status': args.status}) 

        # Commit Updated Execution status to Database
        database.session.commit()

        if args.status in ['failed', 'succeeded', 'aborted']:

            # Query Job Executions Table
            job_execution_query = JobExecution.query.filter(JobExecution.execution_id == execution_id).one()

            # Query Jobs Table
            job_query = Job.query.filter(Job.id == job_execution_query.job_id).one()

            # Query Clusters table
            cluster_query = Cluster.query.filter(Cluster.id == job_query.cluster_id).one()

            # Query Organizations table
            organization_query = Organization.query.filter(Organization.id == job_execution_query.organization_id).one()

            f = tempfile.NamedTemporaryFile(mode='w+')
    
            try:
                # Write CA Certificate to Temporary File
                ca = base64.b64decode(cluster_query.certificate_authority).decode()
                f.write(ca)
                f.seek(0)

                # Create K8S Client / Workload
                client = BoaK8SClient(
                    ca = f.name,
                    server = cluster_query.server_url,
                    token = cluster_query.token
                )

                client.delete_pod(
                    name=job_query.name,
                    execution_id=execution_id,
                    organization_id=organization_query.id
                )

            finally:
                f.close()

        response = {
            "id": job_execution_query.id,
            "job_name": job_query.name,
            "execution_id": job_execution_query.execution_id,
            "organization_name": organization_query.id,
            "status": job_execution_query.status
        }

        return response, 200
    
    def delete(self, execution_id: str):

        # Drop Job Row
        row = JobExecution.query.filter(JobExecution.execution_id == execution_id).one()
        database.session.delete(row)
        database.session.commit() 
    
        return 200

    def get(self, execution_id: str):

        # Query Job Executions Table
        job_execution_query = JobExecution.query.filter(JobExecution.execution_id == execution_id).one()
        
        # Query Jobs Table
        job_query = Job.query.filter(Job.id == job_execution_query.job_id).one()

        # Get Organization Id
        organization_id = Organization.query.filter(Organization.id == job_execution_query.organization_id).one().id

        response = {
            "id": job_execution_query.id,
            "job_name": job_query.id,
            "execution_id": job_execution_query.execution_id,
            "organization_name": organization_id,
            "status": job_execution_query.status
        }
    
        return response, 200