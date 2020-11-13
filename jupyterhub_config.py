# Configuration file for JupyterHub
import os
import socket
import dockerspawner
import subprocess
import warnings
from tornado import gen
from oauthenticator.oauth2 import OAuthenticator
from oauthenticator.generic import GenericOAuthenticator
import json
import os
import base64
import urllib

from tornado.auth import OAuth2Mixin
from tornado import web

from tornado.httputil import url_concat
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

from jupyterhub.auth import LocalAuthenticator

from traitlets import Unicode, Dict, Bool, Union, default, observe


c = get_config()

c.JupyterHub.tornado_settings = {'max_body_size': 1048576000, 'max_buffer_size': 1048576000}

callback = os.environ["OAUTH_CALLBACK_URL"]
os.environ["OAUTH_CALLBACK"] = callback
iam_server = os.environ["OAUTH_ENDPOINT"]

server_host = socket.gethostbyname(socket.getfqdn())
# TODO: run self registration then
#./.init/dodas-IAMClientRec
os.environ["IAM_INSTANCE"] = iam_server

myenv = os.environ.copy()

response = subprocess.check_output(['./.init/dodas-IAMClientRec', server_host], env=myenv)
response_list = response.decode('utf-8').split("\n")
client_id = response_list[len(response_list)-3]
client_secret = response_list[len(response_list)-2]

class EnvAuthenticator(GenericOAuthenticator):

    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        auth_state = yield user.get_auth_state()
        import pprint
        pprint.pprint(auth_state)
        if not auth_state:
            # user has no auth state
            return
        # define some environment variables from auth_state
        self.log.info(auth_state)
        spawner.environment['ACCESS_TOKEN'] = auth_state['access_token']
        spawner.environment['REFRESH_TOKEN'] = auth_state['refresh_token']
        spawner.environment['USERNAME'] = auth_state['oauth_user']['preferred_username']
        spawner.environment['GROUPS'] = " ".join(auth_state['oauth_user']['groups'])

        allowed_groups = os.environ["OAUTH_GROUPS"].split(" ")
        amIAllowed = False

        self.log.info(auth_state['oauth_user']['groups'])
        for gr in allowed_groups:
            if gr in auth_state['oauth_user']['groups']:
                amIAllowed = True

        if not amIAllowed:
                self.log.error(
                    "OAuth user contains not in group the allowed groups %s" % allowed_groups
                )
                raise Exception("OAuth user not in the allowed groups %s" % allowed_groups)


c.JupyterHub.authenticator_class = EnvAuthenticator
c.GenericOAuthenticator.oauth_callback_url = callback

# PUT IN SECRET
c.GenericOAuthenticator.client_id = client_id
c.GenericOAuthenticator.client_secret = client_secret
c.GenericOAuthenticator.authorize_url = iam_server.strip('/') + '/authorize'
c.GenericOAuthenticator.token_url = iam_server.strip('/') + '/token'
c.GenericOAuthenticator.userdata_url = iam_server.strip('/') + '/userinfo'
c.GenericOAuthenticator.scope = ['openid', 'profile', 'email', 'address', 'offline_access']
c.GenericOAuthenticator.username_key = "preferred_username"

c.GenericOAuthenticator.enable_auth_state = True
if 'JUPYTERHUB_CRYPT_KEY' not in os.environ:
    warnings.warn(
        "Need JUPYTERHUB_CRYPT_KEY env for persistent auth_state.\n"
        "    export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)"
    )
    c.CryptKeeper.keys = [ os.urandom(32) ]

#c.JupyterHub.tornado_settings = {'max_body_size': 1048576000, 'max_buffer_size': 1048576000}
c.JupyterHub.log_level = 30

#c.ConfigurableHTTPProxy.debug = True

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.


# Spawn single-user servers as Docker containers
class CustomSpawner(dockerspawner.DockerSpawner):
    def _options_form_default(self):
        return """
        <label for="stack">Select your desired image:</label>
  <input list="images" name="img">
  <datalist id="images">
    <option value="dodasts/mlind-tensorflow-nb:latest">Tensorflow</option>
  </datalist>
<br>
        <label for="mem">Select your desired memory size:</label>
        <select name="mem" size="1">
  <option value="4G">4GB</option>
  <option value="8G"> 8GB </option>
  <option value="16G"> 16GB </option>
</select>

        """

    def options_from_form(self, formdata):
        options = {}
        options['img'] = formdata['img']
        container_image = ''.join(formdata['img'])
        print("SPAWN: " + container_image + " IMAGE" )
        self.container_image = container_image
        options['mem'] = formdata['mem']
        memory = ''.join(formdata['mem'])
        self.mem_limit = memory
        return options


    @gen.coroutine
    def create_object(self):
        """Create the container/service object"""

        create_kwargs = dict(
            image=self.image,
            environment=self.get_env(),
            volumes=self.volume_mount_points,
            name=self.container_name,
            command=(yield self.get_command()),
        )

        # ensure internal port is exposed
        create_kwargs["ports"] = {"%i/tcp" % self.port: None}

        create_kwargs.update(self.extra_create_kwargs)

        # build the dictionary of keyword arguments for host_config
        host_config = dict(binds=self.volume_binds, links=self.links)

        if getattr(self, "mem_limit", None) is not None:
            # If jupyterhub version > 0.7, mem_limit is a traitlet that can
            # be directly configured. If so, use it to set mem_limit.
            # this will still be overriden by extra_host_config
            host_config["mem_limit"] = self.mem_limit

        if not self.use_internal_ip:
            host_config["port_bindings"] = {self.port: (self.host_ip,)}
        host_config.update(self.extra_host_config)
        host_config.setdefault("network_mode", self.network_name)

        self.log.debug("Starting host with config: %s", host_config)

        host_config = self.client.create_host_config(**host_config)
        create_kwargs.setdefault("host_config", {}).update(host_config)

        print(create_kwargs)
        # create the container
        obj = yield self.docker("create_container", **create_kwargs)
        return obj

c.JupyterHub.spawner_class = CustomSpawner

# Spawn containers from this image
#c.DockerSpawner.container_image = 'tensorflow/tensorflow:latest-gpu-jupyter'
#c.DockerSpawner.image = 'dciangot/test:latest'

spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "jupyterhub-singleuser --port 8889 --ip 0.0.0.0 --allow-root --debug")

c.DockerSpawner.port = 8889
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })

#c.DockerSpawner.use_internal_ip = True
#network_name = os.environ['DOCKER_NETWORK_NAME']
#c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
device_request = {
            'Driver': 'nvidia',
            'Capabilities': [['gpu']],  # not sure which capabilities are really needed
            'Count': 1,  # enable all gpus
}
if os.environ["WITH_GPU"] == "true":
    c.DockerSpawner.extra_host_config = {
                                      'device_requests': [device_request]
                                        }
c.DockerSpawner.network_name = 'jupyterhub'


# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir

notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True


#  This is the address on which the proxy will bind. Sets protocol, ip, base_url
c.JupyterHub.bind_url = 'http://:8888'
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_connect_ip = 'jupyterhub'

c.Authenticator.allowed_users = {'test'}

