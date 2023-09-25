from flask_restful import reqparse, Resource
from sqlalchemy.exc import NoResultFound
from boa_manager.utils.string_utils import (
    valid_display_string,
    valid_url
)
from boa_manager.db.database import database
from boa_manager.db.models.clusters import Cluster

class ClusterListApi(Resource):
    def get(self):

        # Get all Clusters
        clusters = Cluster.query.all()
        database.session.close()
        response = []

        for cluster in clusters:
            response.append(
                {
                    "id": cluster.id,
                    "name": cluster.name,
                    "server_url": cluster.server_url,
                    "certificate_authority": cluster.certificate_authority
                }
            )

        return response, 200

class ClusterApi(Resource):
    def _validate_request(self, cluster_name: str, server_url: str):
        if not (valid_display_string(cluster_name) and
                valid_url(server_url)):
            return False
        return True
    
    def get(self, cluster_name: str):
        try:
            # Get Cluster Row
            cluster = Cluster.query.filter(Cluster.name == cluster_name).one()
            database.session.close()

        except NoResultFound:
            response = {
                "message": "Cluster does not exist."
            }
            return response, 404
        
        response = {
            "id": cluster.id,
            "name": cluster.name,
            "server_url": cluster.server_url,
            "certificate_authority": cluster.certificate_authority
        }

        return response, 200  

    def post(self, cluster_name: str):

        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('server_url')
        parser.add_argument('certificate_authority')
        parser.add_argument('token')
        args = parser.parse_args()

        if not self._validate_request(server_url=args.server_url,
                                      cluster_name=cluster_name):
            response = {
                "message": "Invalid Request."
            }

            return response, 405

        try:
            # Create Cluster in the Database
            cluster = Cluster(
                name=cluster_name,
                server_url=args.server_url,
                certificate_authority=args.certificate_authority,
                token=args.token
            )
    
            # Commit to Database
            database.session.add(cluster)
            database.session.commit()
        except NoResultFound:
            response = {
                "message": "Invalid Request."
            }
            return response, 405 
        
        cluster_query = cluster.query.filter(Cluster.name == cluster_name).one()
        database.session.close()

        response = {
            "id": cluster_query.id,
            "name": cluster_query.name,
            "server_url": cluster_query.server_url,
            "certificate_authority": cluster_query.certificate_authority
            
        }

        return response, 201

    def put(self, cluster_name: str):

        # Parse Arguments
        parser = reqparse.RequestParser()
        parser.add_argument('server_url')
        parser.add_argument('certificate_authority')
        parser.add_argument('token')
        args = parser.parse_args()

        if not self._validate_request(server_url=args.server_url,
                                      cluster_name=cluster_name):
            response = {
                "message": "Invalid Request."
            }

            return response, 405

        try:
            # Update Cluster Row
            database.session.query(Cluster).filter_by(name=cluster_name).update({"server_url": args.server_url,
                                                                           "certificate_authority": args.certificate_authority,
                                                                           "token": args.token}) 
            cluster = Cluster.query.filter(Cluster.name == cluster_name).one()
            database.session.commit()
            database.session.close()

        except NoResultFound:
            response = {
                "message": "Invalid Request."
            }
            return response, 405 
        
        response = {
            "id": cluster.id,
            "name": cluster.name,
            "server_url": cluster.server_url,
            "certificate_authority": cluster.certificate_authority
            
        }

        return response, 200
    
    def delete(self, cluster_name: str):
        try:
            # Drop Cluster Row
            row = Cluster.query.filter(Cluster.name == cluster_name).one()
            database.session.delete(row)
            database.session.commit() 
            database.session.close()

        except NoResultFound:
            response = {
                "message": "Cluster does not exist."
            }
            return response, 404
        
        return 200