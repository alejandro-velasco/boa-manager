# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The example covers the following:
    - Creation of a deployment using AppsV1Api
    - update/patch to perform rolling restart on the deployment
    - deletetion of the deployment
"""

import datetime
import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class BoaK8SClient:
    def __init__(self, ca="", server="https://127.0.0.1:6443", token=""):
        self.api = self._configure_client(ca, server, token)

    def _configure_client(self, ca, server, token):

        if not token:
            logging.warn('Bearer token not specified. Checking local serviceaccount mount location.')

            try:
                with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as f:
                    token = f
            except FileNotFoundError as fnfe:
                logging.error('Serviceaccount Token is not mounted.')
                return None, 404
            except IOError as ioe:
                logging.error('Serviceaccount token cannot be read.')
                return None, 403

        if not ca:
            logging.warn('CA not specified. Checking local serviceaccount mount location.')

            try:
                with open('/var/run/secrets/kubernetes.io/serviceaccount/ca.crt') as f:
                    ca = f
            except FileNotFoundError as fnfe:
                logging.error('Serviceaccount ca.crt is not mounted.')
                return None, 404
            except IOError as ioe:
                logging.error('Serviceaccount ca.crt cannot be read.')
                return None, 403            

        configuration = client.Configuration()
        configuration.api_key["authorization"] = token
        configuration.api_key_prefix['authorization'] = 'Bearer'
        configuration.host = server
        configuration.ssl_ca_cert = ca

        return client.CoreV1Api(client.ApiClient(configuration))

    def create_pod(self, 
                   name,  
                   image,
                   url,
                   namespace='boa',
                   submodules=False,
                   branch='master',
                   file='boa.yaml'):
        
        submodules_flag = ""

        if submodules:
            submodules_flag = "--submodules"
        else:
            submodules_flag = "--no-submodules"


        body = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': name
            },
            'spec': {
                'containers': [{
                    'image': image,
                    'name': "boa-client",
                    'args': [
                        f"--repository {url} {submodules_flag} --branch {branch} --name {name} --file {file}"
                    ]
                }]
            }
        }
    
        # Create deployment
        resp = self.api.create_namespaced_pod(
            body=body, namespace=namespace
        )
    
        logging.info(f"pod `{resp.metadata.name}` created.")
        logging.info(f"NAMESPACE\tNAME\t\t\tREVISION\tIMAGE")
        logging.info(f"{resp.metadata.namespace}\t\t{resp.metadata.name}\t{resp.metadata.generation}\t\t{resp.spec.containers[0].image}")
    
    def delete_pod(self, name, namespace):
        # Delete deployment
        resp = self.api.delete_namespaced_pod(
            name=name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=5
            )
        )
        logging.info(f"pod `{name}` deleted.")