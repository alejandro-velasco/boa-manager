import os
import requests
from waitress import serve
from flask import Flask, request, render_template, url_for
from flask_restful import Api
from flask_assets import Bundle, Environment
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

app = Flask(__name__)
api = Api(app)

assets = Environment(app)

css = Bundle("src/main.css", output="dist/main.css")
js = Bundle("src/*.js", output="dist/main.js")

assets.register("css", css)
assets.register("js", js) 

css.build()
js.build()

def init_api():
    api.add_resource(OrganizationApi, '/api/organization/<string:organization_name>')
    api.add_resource(OrganizationListApi, '/api/organizations')
    api.add_resource(ClusterApi, '/api/cluster/<string:cluster_name>')
    api.add_resource(ClusterListApi, '/api/clusters')
    api.add_resource(JobApi, '/api/job/<string:organization_name>/<string:job_name>')
    api.add_resource(JobListApi, '/api/jobs/<string:organization_name>')
    api.add_resource(JobExecutionApi, '/api/job/<string:organization_name>/<string:job_name>/execute')
    api.add_resource(JobStatusListApi, '/api/job/<string:organization_name>/<string:job_name>/statuses')
    api.add_resource(JobStatusApi, '/api/job/status/<string:execution_id>')

#
# Swagger API
#

@app.route('/docs/api')
def get_docs():
    return render_template('swaggerui/swaggerui.html')

@app.route("/ui")
def homepage():
    return render_template("index.html")

#
# Organization Routes
#

@app.route("/ui/organizations")
def organizations_list():
    server = request.host_url.rstrip('/')
    organizations = requests.get(f"{server}/api/organizations")
    return render_template("organizations/list.html", organizations=organizations.json())

@app.route("/ui/organizations/create/form")
def organizations_create_form():
    return render_template("organizations/create.html")

@app.route("/ui/organizations/create", methods=['POST'])
def organizations_create():
    server = request.host_url.rstrip('/')
    headers = {
        "Content-Type": "application/json"
    }

    json = {
        "description": request.form['description']
    }

    response = requests.post(f"{server}/api/organization/{request.form['name']}",
                             headers=headers,
                             json=json)
    return organizations_list()

#
# Cluster Routes
#

@app.route("/ui/clusters")
def clusters_list():
    server = request.host_url.rstrip('/')
    clusters = requests.get(f"{server}/api/clusters")
    return render_template("clusters/list.html", clusters=clusters.json())

@app.route("/ui/clusters/create/form")
def clusters_create_form():
    return render_template("clusters/create.html")

@app.route("/ui/clusters/create", methods=['POST'])
def clusters_create():
    server = request.host_url.rstrip('/')
    headers = {
        "Content-Type": "application/json"
    }

    json = {
        "server_url": request.form['server-url'],
        "certificate_authority": request.form['certificate-authority'],
        "token": request.form['token']
    }

    response = requests.post(f"{server}/api/cluster/{request.form['name']}",
                             headers=headers,
                             json=json)
    return clusters_list()

#
# Job Routes
#

@app.route("/ui/organization/<organization_name>")
def organization_jobs_list(organization_name: str):
    server = request.host_url.rstrip('/')
    jobs = requests.get(f"{server}/api/jobs/{organization_name}")
    return render_template("jobs/list.html", 
                           jobs=jobs.json(),
                           organization=organization_name)

@app.route("/ui/jobs/<organization_name>/create/form")
def organization_jobs_create_form(organization_name: str):
    return render_template("jobs/create.html",
                           organization=organization_name)

@app.route("/ui/jobs/<organization_name>/create", methods=['POST'])
def organization_jobs_create(organization_name: str):
    server = request.host_url.rstrip('/')
    headers = {
        "Content-Type": "application/json"
    }

    json = {
        "branch": request.form['branch'],
        "cluster_name": request.form['cluster-name'],
        "file_path": request.form['file-path'],
        "image": request.form['image'],
        "log_level": request.form['log-level'],
        "repo_url": request.form['repo-url']
    }

    response = requests.post(f"{server}/api/job/{organization_name}/{request.form['job-name']}",
                             headers=headers,
                             json=json)
    return organization_jobs_list(organization_name=organization_name)

@app.route("/ui/job/<organization_name>/<job_name>/dashboard")
def organization_jobs_dashboard(organization_name: str, job_name: str):
    return render_template("jobs/dashboard.html", 
                           job_name=job_name,
                           organization_name=organization_name)

@app.route("/ui/job/<organization_name>/<job_name>/executions")
def organization_jobs_executions(organization_name: str, job_name: str):
    server = request.host_url.rstrip('/')
    executions = requests.get(f"{server}/api/job/{organization_name}/{job_name}/statuses")
    return render_template("jobs/executions.html",
                           organization_name=organization_name,
                           job_name=job_name, 
                           executions=executions.json())

def entrypoint():
    init_db()
    init_api()
    serve(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    entrypoint()