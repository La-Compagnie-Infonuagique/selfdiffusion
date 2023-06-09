import pathlib
import json
import requests
import boto3

DEFAULT_CONF_PATH = pathlib.Path.home() / ".selfdiffusion"
DEFAULT_CONF_FILE = "config.json"


class SelfDiffusionClient(object):

    def __init__(self, url, conf_path=DEFAULT_CONF_PATH, conf_file=DEFAULT_CONF_FILE):
        self.url = url
        self.conf_path = conf_path
        self.conf_file_path = conf_path / conf_file

        # Generate the config file if it does not exist
        if not self.conf_file_path.exists():
            # make the equivalent of a touch config_file_path and create parent directory
            self.conf_file_path.parent.mkdir(exist_ok=True)
            configuration = requests.get(self.url + "/config").json()
            with open(self.config_file_path, "w") as f:
                json.dump(configuration, f)

    def _read_conf(self):
        with open(self.conf_file_path,'r') as f:
            return json.load(f)

    def _write_conf(self, conf):

        # read the content of the conf_file into a dict
        with open(self.conf_file_path, 'r') as f:
            conf_file = json.load(f)

            # update the dict with the new conf
            conf_file.update(conf)

        # write the dict back to the conf_file
        with open(self.conf_file_path, 'w') as f:
            json.dump(conf_file, f)

    def _allocate_gpu_runtime(self): #instance_type, count, ephemeral_storage):
        """ request the allocation of a GPU runtime """

        # TODO: replace this re-occuring boiletplate by something cleaner.
        conf = self._read_conf()

        bearer_token = conf['id']
        path = self.url + '/runtime'

        headers = {
            'Authorization': 'Bearer ' + bearer_token
        }

        response = requests.post(path, headers=headers, json={'hello': 'world'})
        return response.json()

        

    def init_signup(self, email, password, phone):
        """ allows a user to sign up """

        # get the configuration from the file
        conf = self._read_conf()

        # call the signup cognito thing
        client = boto3.client('cognito-idp', region_name=conf['region'])  
        try:
            response = client.sign_up(
                ClientId=conf['client_id'], 
                Username=email,
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email 
                    },
                    {
                        'Name': 'phone_number',
                        'Value': phone 
                    }
                ]
            )

            return response

        except Exception as e:
            print(e)
            return 

    def confirm_signup(self, email, code):
        """ confirm a user's signup """

        conf = self._read_conf()
        client = boto3.client('cognito-idp', region_name=conf['region'])

        try:

            response = client.confirm_sign_up(
                ClientId=conf['client_id'],
                Username=email,
                ConfirmationCode=code
            )

            return response

        except Exception as e:
            print(e)
            return
    
    def login(self, email, password):
        """ login a user """

        conf = self._read_conf()
        client = boto3.client('cognito-idp', region_name=conf['region'])

        try:
            response = client.initiate_auth(
                ClientId=conf['client_id'],
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )

            token_access = response['AuthenticationResult']['AccessToken']
            token_refresh = response['AuthenticationResult']['RefreshToken']
            token_id = response['AuthenticationResult']['IdToken']

            conf = {
                'access': token_access, 
                'refresh': token_refresh, 
                'id': token_id
            }

            self._write_conf(conf)
            return

        except Exception as e:
            print(e)
            return

    def balance(self):
        """ returns the balance in the user account """

        conf = self._read_conf()

        bearer_token = conf['id']
        path = self.url + '/balance'

        headers = {
            'Authorization': 'Bearer ' + bearer_token
        }

        response = requests.post(path, headers=headers)
        return response.json()

    def result(self):
        """ generates a text from a prompt on a GPU runtime """
        conf = self._read_conf()

        bearer_token = conf['id']
        path = self.url + '/result'

        headers = {
            'Authorization': 'Bearer ' + bearer_token
        }

        response = requests.post(path, json={'hello':'world'} ,headers=headers)
        return response.json()

    def generate(self):
        """ generates a text from a prompt on a GPU runtime """
        conf = self._read_conf()

        bearer_token = conf['id']
        path = self.url + '/generate'

        headers = {
            'Authorization': 'Bearer ' + bearer_token
        }

        response = requests.post(path, json={'hello':'world'} ,headers=headers)
        return response.json()


    def generatedev(self, prompt, samples):
        """ generates a text from a prompt on a GPU runtime """
        conf = self._read_conf()

        bearer_token = conf['id']
        path = self.url + '/generatedev'

        headers = {
            'Authorization': 'Bearer ' + bearer_token
        }

        data = {
            'prompt': prompt, 
            'samples': samples
        }

        response = requests.post(path, json=data ,headers=headers)
        return response.json()

