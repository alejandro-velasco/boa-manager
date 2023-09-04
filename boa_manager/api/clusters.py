from flask_restful import reqparse, Resource
from boa_manager.db.database import Database
from boa_manager.db.models.jobs import Cluster

class ClusterApi(Resource):
    def post(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('server_url')
        parser.add_argument('certificate_authority')
        parser.add_argument('token')
        args = parser.parse_args()

        # Create Cluster in the Database
        db = Database()
        cluster = Cluster(
            name=args.name,
            server_url=args.server_url,
            certificate_authority=args.certificate_authority,
            token=args.token
        )

        # Commit to Database
        db.session.add(cluster)
        db.session.commit()

        return args, 201

    def get(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()

        # Get Cluster Id
        cluster_id = Cluster.query.filter(Cluster.name == args.name).one().id
        resp = {
            "name": args.name,
            "id": str(cluster_id)
        }

        return resp, 200    