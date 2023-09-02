from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from boa_manager.db.database import Database
from boa_manager.db.models.jobs import (
    Job,
    Cluster,
    Organization,
    OrganizationUniqueIndex
)

class OrganizationApi(Resource):
    def post(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()

        # Create Organization in the Database
        db = Database()
        org = Organization(name=args.name)

        # Commit to Database
        db.session.add(org)
        db.session.commit()

        # Create Partial Unique Constraint
        org_id = org.query.filter(Organization.name == args.name).one().id
        org_unique_index = OrganizationUniqueIndex(id=org_id, engine=db.engine)

        # Commit to Database
        org_unique_index.create()
        db.session.commit()

        return args, 201
    
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
        cluster = Job(
            name=args.name,
            organization_id=args.organization_id,
            cluster_id=args.cluster_id,
        )

        # Commit to Database
        db.session.add(cluster)
        db.session.commit()

        return args, 201