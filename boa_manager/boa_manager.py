import os
from flask import Flask, request
from flask_restful import Resource, Api
from boa_manager.db.database import Database, init_db
from boa_manager.api.organizations import OrganizationApi
from boa_manager.api.clusters import ClusterApi
from boa_manager.api.jobs import JobApi, JobExecutionApi


def entrypoint():
    app = Flask(__name__)
    api = Api(app)
    init_db()

    api.add_resource(OrganizationApi, '/api/organizations')
    api.add_resource(ClusterApi, '/api/clusters')
    api.add_resource(JobApi, '/api/jobs')
    api.add_resource(JobExecutionApi, '/api/jobs/execute')
    app.run(debug=True)
    
if __name__ == '__main__':
    entrypoint()