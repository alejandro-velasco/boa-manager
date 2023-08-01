from flask import Flask
from flask_restful import Api
from boa_manager.api.jobs import Job

app = Flask(__name__)
api = Api(app)

def entrypoint():
    api.add_resource(Job, '/job/<job_id>')
    app.run(debug=True)

if __name__ == '__main__':
    entrypoint()