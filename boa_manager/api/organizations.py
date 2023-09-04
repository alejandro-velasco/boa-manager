from flask_restful import reqparse, Resource
from boa_manager.db.database import Database
from boa_manager.db.models.jobs import (
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
    
    def get(self):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()

        # Get Organization Id
        org_id = Organization.query.filter(Organization.name == args.name).one().id
        resp = {
            "name": args.name,
            "id": str(org_id)
        }

        return resp, 200