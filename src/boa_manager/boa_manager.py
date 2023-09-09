import os
from waitress import serve
from flask import Flask, request
from flask_restful import Resource, Api
from boa_manager.db.database import Database, init_db
from boa_manager.api.organizations import OrganizationApi, OrganizationListApi
from boa_manager.api.clusters import ClusterApi, ClusterListApi
from boa_manager.api.jobs import (
    JobApi, 
    JobExecutionApi, 
    JobStatusApi, 
    JobListApi, 
    JobStatusListApi
)

def entrypoint():
    app = Flask(__name__)
    api = Api(app)
    init_db()

    api.add_resource(OrganizationApi, '/api/organization/<string:organization_name>')
    api.add_resource(OrganizationListApi, '/api/organizations')
    api.add_resource(ClusterApi, '/api/cluster/<string:cluster_name>')
    api.add_resource(ClusterListApi, '/api/clusters')
    api.add_resource(JobApi, '/api/job/<string:organization_name>/<string:job_name>')
    api.add_resource(JobListApi, '/api/jobs/<string:organization_name>')
    api.add_resource(JobExecutionApi, '/api/job/<string:organization_name>/<string:job_name>/execute')
    api.add_resource(JobStatusListApi, '/api/job/<string:organization_name>/<string:job_name>/statuses')
    api.add_resource(JobStatusApi, '/api/job/status/<string:execution_id>')
    serve(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    entrypoint()