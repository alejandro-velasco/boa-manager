import os
from flask import Flask, request
from flask_restful import Resource, Api
from boa_manager.db.database import Database, init_db
from boa_manager.db.models.jobs import (
    Job,
    Cluster,
    Organization,
    OrganizationUniqueIndex
)
from boa_manager.api.jobs import (
    OrganizationApi,
    ClusterApi,
    JobApi
)

def entrypoint():
    app = Flask(__name__)
    api = Api(app)
    init_db()

    api.add_resource(OrganizationApi, '/api/organizations')
    api.add_resource(ClusterApi, '/api/clusters')
    api.add_resource(JobApi, '/api/jobs')
    app.run(debug=True)
    
if __name__ == '__main__':
    entrypoint()