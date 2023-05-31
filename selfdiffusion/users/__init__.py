# user management for selfdiffusion

import boto3
import questionary
import pathlib
import json
import requests

# TODO: do not hardcode the region and client id
CLIENT_ID = '11vh8fstqhoe9r987euf6cpdff'
USER_POOL_ID = 'ca-central-1_vOgUWeA27'
API_GATEWAY_URL = 'https://fy1g0m8sa8.execute-api.ca-central-1.amazonaws.com/selfdiffusiondev'
# 1. for some reason ??? the verification email is not sent by cognito for new users email.
# need to investigate and maybe look into using SES to send the email instead.
def signup():

    # gather sign up information from the user

    # TODO: add input validation.
    email = questionary.text("Enter your email address:").ask()
    password = questionary.password("Enter your password:").ask()
    phone = questionary.text("Enter a phone number where we can reach you:").ask()

    client = boto3.client('cognito-idp', region_name='ca-central-1')  

    try:

        response = client.sign_up(
            ClientId=CLIENT_ID,  # Replace with your Cognito App Client ID
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email  # Replace with user's email address
                },
                {
                    'Name': 'phone_number',
                    'Value': phone # Replace with user's email address
                }
            ]
        )

        # TODO: remove this auto confirm step

        code = questionary.text("Enter your validation code for the email").ask()
        response = client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=code
        )

        return response

    except Exception as e:
        print(e)
        return 

def login(email, password):
   client = boto3.client('cognito-idp', region_name='ca-central-1')

   response = client.initiate_auth(
       ClientId=CLIENT_ID,
       AuthFlow='USER_PASSWORD_AUTH',
       AuthParameters={
           'USERNAME': email,
           'PASSWORD': password,
       }
   )

   # store the access token and refresh token in the user's home directory
   token_access = response['AuthenticationResult']['AccessToken']
   token_refresh = response['AuthenticationResult']['RefreshToken']
   token_id = response['AuthenticationResult']['IdToken']

   # create the selfdiffusion directory in the user's home directory if it does not exist
   home = pathlib.Path.home()
   selfdiffusion = home / '.selfdiffusion'
   selfdiffusion.mkdir(exist_ok=True)

   # create the credentials file if it does not exist
   credentials = selfdiffusion / 'credentials'

   # write the access token and refresh token to the credentials file
   with open(credentials, 'w') as f:
       json.dump(
          {'access': token_access, 
           'refresh': token_refresh,
           'id':token_id}, f)


   return response

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
    