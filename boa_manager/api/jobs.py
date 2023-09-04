import random
import string
import base64
import tempfile
from flask_restful import reqparse, Resource
from boa_manager.db.database import Database
from boa_manager.db.models.jobs import Job
from boa_manager.db.models.clusters import Cluster
from boa_manager.api.kubernetes import BoaK8SClient

class JobApi(Resource):
    def post(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('organization_id')
        parser.add_argument('cluster_id')
        args = parser.parse_args()

        # Create Job in the Database
        db = Database()
        job = Job(
            name=args.name,
            organization_id=args.organization_id,
            cluster_id=args.cluster_id,
        )

        # Commit to Database
        db.session.add(job)
        db.session.commit()

        return args, 201
    
    def get(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('organization_id')
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
        parser.add_argument('name')
        parser.add_argument('organization_id')
        args = parser.parse_args()

        # Get Cluster / Job table in the Database
        db = Database()

        # Get Cluster Information
        cluster_id = Job.query.filter(Job.name == args.name,
                                      Job.organization_id == args.organization_id).one().cluster_id
        cluster_query = Cluster.query.filter(Cluster.id == cluster_id).one()
        
        pod_id = ''.join(random.choices(string.ascii_lowercase +
                                     string.digits, k=10))

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
                name=f'{args.name}-{pod_id}',
                image="boa-client:test",
                url="https://github.com/alejandro-velasco/boa-test-repo.git"
            )
                
        finally:
            f.close()

        return 200  