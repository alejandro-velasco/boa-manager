import random
import string
import base64
import tempfile
from flask_restful import reqparse, Resource
from boa_manager.db.database import Database
from boa_manager.db.models.jobs import (
    Job, 
    JobExecution
)
from boa_manager.db.models.clusters import Cluster
from boa_manager.api.kubernetes import BoaK8SClient

class JobApi(Resource):
    def post(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('organization_id', required=True)
        parser.add_argument('image', required=True)
        parser.add_argument('cluster_id', required=True)
        parser.add_argument('repo_url', required=True)
        parser.add_argument('branch', required=False)
        parser.add_argument('file_path', required=False)
        parser.add_argument('log_level', required=False)
        args = parser.parse_args()

        # Create Job in the Database
        db = Database()
        job = Job(
            name=args.name,
            organization_id=args.organization_id,
            cluster_id=args.cluster_id,
            repo_url=args.repo_url,
            branch=args.branch,
            file_path=args.file_path,
            image=args.image,
            log_level=args.log_level
        )        

        # Commit to Database
        db.session.add(job)
        db.session.commit()

        return args, 201
    
    def get(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('organization_id', required=True)
        args = parser.parse_args()

        # Get Job Id
        job_id = Job.query.filter(Job.name == args.name,
                                  Job.organization_id == args.organization_id).one().id
        resp = {
            "name": args.name,
            "organization_id": args.organization_id,
            "job_id": str(job_id)
        }

        return resp, 200
    
class JobExecutionApi(Resource):
    def post(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('organization_id', required=True)
        parser.add_argument('server', required=True)
        args = parser.parse_args()

        # Generate Execution ID
        execution_id = ''.join(random.choices(string.ascii_lowercase +
                                              string.digits, k=10))

        # Query Cluster and Job tables
        job_query = Job.query.filter(Job.name == args.name,
                                      Job.organization_id == args.organization_id).one()
        cluster_query = Cluster.query.filter(Cluster.id == job_query.cluster_id).one()

        # Get Cluster / Job table in the Database
        db = Database()
        job_execution=JobExecution(job_id=job_query.id,
                                   organization_id=job_query.organization_id,
                                   execution_id=execution_id,
                                   status='Pending')

        # Commit Pending Execution to Database
        db.session.add(job_execution)
        db.session.commit()



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
                name=args.name,
                image=job_query.image,
                url=job_query.repo_url,
                execution_id=execution_id,
                organization_id=args.organization_id,
                server=args.server
            )
                
        finally:
            f.close()

        return 200
    
class JobStatusApi(Resource):
    def post(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('job_name', required=True)
        parser.add_argument('organization_id', required=True)
        parser.add_argument('execution', required=True)
        parser.add_argument('status', required=True)
        
        args = parser.parse_args()

        # Get Cluster / Job table in the Database
        db = Database()
        job_query = Job.query.filter(Job.name == args.job_name,
                                     Job.organization_id == args.organization_id).one()
        
        db.session.query(JobExecution).filter_by(job_id=job_query.id,
                                                 organization_id=job_query.organization_id,
                                                 execution_id=args.execution).update({'status': args.status}) 

        # Commit Updated Execution status to Database
        db.session.commit()

        if args.status in ['failed', 'succeeded', 'aborted']:

            # Query Cluster table
            cluster_query = Cluster.query.filter(Cluster.id == job_query.cluster_id).one()

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
                    name=args.job_name,
                    execution_id=args.execution,
                    organization_id=args.organization_id
                )

            finally:
                f.close()

        return 200  