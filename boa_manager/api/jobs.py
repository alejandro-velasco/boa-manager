from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

class Job(Resource):
    def post(self, job_id, k8s_client):
        parser = reqparse.RequestParser()
        parser.add_argument('url')
        parser.add_argument('branch')
        parser.add_argument('submodules')
        parser.add_argument('name')
        parser.add_argument('file')
        args = parser.parse_args()
        return args, 201