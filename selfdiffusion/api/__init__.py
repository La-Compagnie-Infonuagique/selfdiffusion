import pathlib
import json

class SelfDiffusionClient(object):

    def __init__(self, url, config_path):
        self.url = url

        # Load configuration from config_path. The content of the file is json
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.config = config

    def login(self, username, password):
        """ Login to the server and get a token """
        pass

    def signup(self):
        """ Signup to the service """
        pass

    def _initiate_signup(self, username, password):
        """ Signup to selfdiffusion and get a token """
        pass

    def _confirm_signup(self, username, token):
        """ Confirm the signup process """
        pass
