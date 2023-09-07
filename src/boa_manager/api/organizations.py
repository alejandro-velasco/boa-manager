from flask_restful import reqparse, Resource
from boa_manager.db.database import database
from boa_manager.db.models.organizations import (
    Organization,
    OrganizationUniqueIndex
)

class OrganizationApi(Resource):
    def get(self, organization_name: str):

        # Get Organization Id
        organization_id = Organization.query.filter(Organization.name == organization_name).one().id

        response = {
            "id": organization_id,
            "name": organization_name
        }

        return response, 200

    def post(self, organization_name: str):

        # Create Organization in the Database
        org = Organization(name=organization_name)

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
            "name": organization_name
        }

        return response, 201

    def delete(self, organization_name: str):

        # Drop Organization Row
        row = Organization.query.filter(Organization.name == organization_name).one()
        database.session.delete(row)
        database.session.commit()

        # Drop Partial Unique Index
        unique_index = OrganizationUniqueIndex(id=row.id, 
                                               engine=database.engine)
        unique_index.drop()
        
    
        return 200