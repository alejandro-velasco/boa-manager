import random
import string
import base64
import tempfile
from flask import request
from sqlalchemy.exc import NoResultFound
from flask_restful import reqparse, Resource
from boa_manager.utils.string_utils import (
    valid_display_string,
    valid_docker_image
)
from boa_manager.db.database import database
from boa_manager.db.models.jobs import (
    Job, 
    JobExecution
)
from boa_manager.db.models.organizations import Organization
from boa_manager.db.models.clusters import Cluster
from boa_manager.api.kubernetes import BoaK8SClient

class JobStatusListApi(Resource):
    def get(self, organization_name: str, job_name: str):

        # Get Job Id
        organization_id = Organization.query.filter(Organization.name == organization_name).one().id
        job = Job.query.filter(Job.organization_id == organization_id,
                                Job.name == job_name).one()
        job_statuses = JobExecution.query.filter(JobExecution.job_id == job.id)
        response = []

        for status in job_statuses:
            response.append(
                {
                    "id": status.id,
                    "job_name": job_name,
                    "organization_name": organization_name,
                    "execution_id": status.execution_id,
                    "status": status.status
                }
            )

        return response, 200

class JobListApi(Resource):
    def get(self, organization_name: str):

        # Get Job Id
        try:
            organization_id = Organization.query.filter(Organization.name == organization_name).one().id

        except NoResultFound:
            response = {
                "message": "Organization not found."
            }
            return response, 404
        
        jobs = Job.query.filter(Job.organization_id == organization_id)
        response = []

        for job in jobs:
            response.append(
                {
                    "id": job.id,
                    "job_name": job.name,
                    "organization_name": organization_name,
                    "repo_url": job.repo_url,
                    "branch": job.branch,
                    "image": job.image,
                    "file_path": job.file_path,
                    "log_level": job.log_level
                }
            )

        return response, 200

class JobApi(Resource):
    def _validate_request(self, cluster_name: str, image: str, job_name: str):
        if not (valid_display_string(cluster_name) and
                valid_display_string(job_name) and
                valid_docker_image(image)):
            return False
        return True

    def get(self, organization_name: str, job_name: str):

        try:
            # Get Organization Id
            organization_id = Organization.query.filter(Organization.name == organization_name).one().id
        
            # Get Job
            job_query = Job.query.filter(Job.name == job_name,
                                         Job.organization_id == organization_id).one()
    
        except NoResultFound:
            response = {
                "message": "Job not found."
            }
            return response, 404
        
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

        if not self._validate_request(image=args.image,
                                      cluster_name=args.cluster_name,
                                      job_name=job_name):
            response = {
                "message": "Invalid Request."
            }

            return response, 405

        try:
            # Get Organization Id
            organization_id = Organization.query.filter(Organization.name == organization_name).one().id

            # Get Cluster Id        
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
    
        except NoResultFound:
            response = {
                "message": "Invalid Request."
            }
            return response, 405 

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

        if not self._validate_request(image=args.image,
                                      cluster_name=args.cluster_name,
                                      job_name=job_name):
            response = {
                "message": "Invalid Request."
            }

            return response, 405

        try:
            # Get Organization Id
            organization_id = Organization.query.filter(Organization.name == organization_name).one().id
            
            # Get Cluster Id
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
        except NoResultFound:
            response = {
                "message": "Invalid Request."
            }
            return response, 405
    
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

        try:
            # Drop Job Row
            organization_id = Organization.query.filter(Organization.name == organization_name).one().id
            row = Job.query.filter(Job.name == job_name,
                                   Job.organization_id == organization_id).one()
            database.session.delete(row)
            database.session.commit() 
        except NoResultFound:
            response = {
                "message": "Job not found."
            }
            return response, 404
        
        return 200
    
class JobExecutionApi(Resource):
    def post(self, organization_name: str, job_name: str):
        
        # generate server host_url
        server = request.host_url.rstrip('/')

        # Generate Execution ID
        execution_id = ''.join(random.choices(string.ascii_lowercase +
                                              string.digits, k=10))

        try:
            # Get Organization Id
            organization_id = Organization.query.filter(Organization.name == organization_name).one().id

            # Get Job
            job_query = Job.query.filter(Job.name == job_name,
                                          Job.organization_id == organization_id).one()
            
            # Get Cluster Configuration
            cluster_query = Cluster.query.filter(Cluster.id == job_query.cluster_id).one()
        
            # Create Job execution
            job_execution=JobExecution(job_id=job_query.id,
                                       organization_id=job_query.organization_id,
                                       execution_id=execution_id,
                                       status='Pending')
            database.session.add(job_execution)
            database.session.commit()
    
            job_execution_query = job_execution.query.filter(JobExecution.execution_id == execution_id).one()

        except NoResultFound:
            response = {
                "message": "Invalid Request."
            }
            return response, 405

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
                name=job_query.rfc_1123_name,
                image=job_query.image,
                url=job_query.repo_url,
                execution_id=execution_id,
                organization_id=organization_id,
                server=server
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

        try:
            # Get Cluster / Job table in the Database
            database.session.query(JobExecution).filter_by(execution_id=execution_id).update({'status': args.status}) 
    
            # Commit Updated Execution status to Database
            database.session.commit()

        except NoResultFound:
            response = {
                "message": "Execution does not exist."
            }
            return response, 404

        if args.status in ['failed', 'succeeded', 'aborted']:
            try:
                # Query Job Executions Table
                job_execution_query = JobExecution.query.filter(JobExecution.execution_id == execution_id).one()

                # Query Jobs Table
                job_query = Job.query.filter(Job.id == job_execution_query.job_id).one()
    
                # Query Clusters table
                cluster_query = Cluster.query.filter(Cluster.id == job_query.cluster_id).one()
    
                # Query Organizations table
                organization_query = Organization.query.filter(Organization.id == job_execution_query.organization_id).one()

                f = tempfile.NamedTemporaryFile(mode='w+')
    
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
                    name=job_query.rfc_1123_name,
                    execution_id=execution_id,
                    organization_id=organization_query.id
                )

            except NoResultFound:
                response = {
                    "message": "Invalid Request."
                }
                return response, 405
            
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

        try:
            # Drop Job Row
            row = JobExecution.query.filter(JobExecution.execution_id == execution_id).one()
            database.session.delete(row)
            database.session.commit() 
        except NoResultFound:
            response = {
                "message": "Execution does not exist."
            }
            return response, 404
        
        return 200

    def get(self, execution_id: str):
        try:
            # Query Job Executions Table
            job_execution_query = JobExecution.query.filter(JobExecution.execution_id == execution_id).one()
            
            # Query Jobs Table
            job_query = Job.query.filter(Job.id == job_execution_query.job_id).one()
    
            # Get Organization Id
            organization_id = Organization.query.filter(Organization.id == job_execution_query.organization_id).one().id
        except NoResultFound:
            response = {
                "message": "Execution does not exist."
            }
            return response, 405    
        
        response = {
            "id": job_execution_query.id,
            "job_name": job_query.id,
            "execution_id": job_execution_query.execution_id,
            "organization_name": organization_id,
            "status": job_execution_query.status
        }
  
        return response, 200