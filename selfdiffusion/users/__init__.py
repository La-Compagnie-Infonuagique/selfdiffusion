# user management for selfdiffusion

import boto3
import questionary
import pathlib
import json
import requests

def balance():
    """ returns a hello world notice to logged in users"""

    # get the access token from the credentials file
    home = pathlib.Path.home()
    selfdiffusion = home / '.selfdiffusion'
    credentials = selfdiffusion / 'credentials'

    with open(credentials, 'r') as f:
        tokens = json.load(f)

    bearer_token = tokens['id']

    path = API_GATEWAY_URL + '/balance'

    headers = {
        'Authorization': 'Bearer ' + bearer_token
    }


    response = requests.post(path, headers=headers)
    return response
    