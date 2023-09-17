from flask_restful import reqparse, Resource
from sqlalchemy.exc import NoResultFound
from boa_manager.db.database import database
from boa_manager.db.models.organizations import (
    Organization,
    OrganizationUniqueIndex
)

class OrganizationListApi(Resource):
    def get(self):

        # Get all Organizations
        organizations = Organization.query.all()
        response = []

        for organization in organizations:
            response.append(
                {
                    "id": organization.id,
                    "name": organization.name
                }
            )

        return response, 200

class OrganizationApi(Resource):
    def get(self, organization_name: str):

        try:
            # Get Organization Id
            organization = Organization.query.filter(Organization.name == organization_name).one()
        except NoResultFound:
            response = {
                "message": "Organization does not exist."
            }
            return response, 404


        response = {
            "id": organization.id,
            "name": organization.name,
            "description": organization.description
        }

        return response, 200

    def post(self, organization_name: str):

        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('description', required=False, default="")
        args = parser.parse_args()

        # Create Organization in the Database
        org = Organization(name=organization_name,
                           description=args.description)

        # Commit to Database
        database.session.add(org)
        database.session.commit()

        # Create Partial Unique Index
        organization_id = org.query.filter(Organization.name == organization_name).one().id
        unique_index = OrganizationUniqueIndex(id=organization_id, 
                                               engine=database.engine)

        # Commit to Database
        unique_index.create()
        database.session.commit()

        response = {
            "id": organization_id,
            "name": organization_name,
            "description": args.description
        }

        return response, 201

    def put(self, organization_name: str):
        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('description', required=False, default="")
        args = parser.parse_args()

        try:
            # Update Organization in the Database
            database.session.query(Organization).filter_by(name=organization_name).update({'description': args.description})

            database.session.commit()

            organization_query = Organization.query.filter(Organization.name == organization_name).one()

        except NoResultFound:
            response = {
                "message": "Invalid Request."
            }
            return response, 405
    
        response = {
            "id": organization_query.id,
            "name": organization_query.name,
            "description": organization_query.description
        }

        return response, 201

    def delete(self, organization_name: str):

        try:
            # Drop Organization Row
            row = Organization.query.filter(Organization.name == organization_name).one()
            database.session.delete(row)
            database.session.commit()
             
            # Drop Partial Unique Index
            unique_index = OrganizationUniqueIndex(id=row.id, 
                                                   engine=database.engine)
            unique_index.drop()

        except NoResultFound:
            response = {
                "message": "Organization does not exist."
            }
            return response, 404
    
        return 200