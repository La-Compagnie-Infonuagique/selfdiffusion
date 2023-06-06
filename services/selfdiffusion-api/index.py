import json
import os
import boto3
import runpod

class GPUNotAvailableError(Exception):
    pass

def lambda_handler(event, _):

    path = event['path']

    # dispatch to correct function
    if path == "/config":
        conf = config()
        return ok_with_payload(conf)

    elif path ==  "/balance":
        auth_context = event['requestContext']['authorizer']
        payload = balance(auth_context)
        return ok_with_payload(payload)

    elif path == "/runtime":
        print(event)
        auth_context = event['requestContext']['authorizer']
        req_data = json.loads(event['body'])
        try:
            payload = runtime(auth_context, req_data)
            return ok_with_payload(payload)
        except GPUNotAvailableError as e:
            return error_with_text(str(e), 503)

    else:
        return not_found()

def not_found():
    return {
        'statusCode': 404,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Not Found'
    }


def ok_with_text(text):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': text
    }

def error_with_text(text, code):
    return {
        'statusCode': code,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': text
    }

def ok_with_payload(payload):
    body = json.dumps(payload)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': body
    }

def config():

    # extract environment variables
    client_id = os.environ['ClientId']
    user_pool_id = os.environ['UserPoolId']
    region = os.environ['Region']
    
    return {
        "client_id": client_id,
        "user_pool_id": user_pool_id,
        "region": region
    }

def balance(auth_context):

    # get cognito user
    username = auth_context['claims']['cognito:username']

    # get balance from dynamodb
    table_name = os.environ['UserInfoTableName']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    response = table.get_item(Key={'username': username})

    if 'Item' in response:
        balance = response['Item'].get('balance')
        return {'balance': balance}

    else:
        return {'balance': 0}

def runtime(auth_context, _):

    # Extract the user email from auth_context
    username = auth_context['claims']['cognito:username']

    ## Retrieve the Runpod API key from the SSM parameter store.
    ssm = boto3.client('ssm')
    ssm_response = ssm.get_parameter(
        Name=os.environ['RunpodApiKeyParamName'],
        WithDecryption=True)
    runpod_api_key = ssm_response['Parameter']['Value']

    ## Set the runpod api key 
    runpod.api_key = runpod_api_key

    ## Try and create the pod
    pod = runpod.create_pod(
        username, 
        'runpod/pytorch:3.10-2.0.0-117',
        'NVIDIA A100 80GB PCIe'
    )

    return pod


    