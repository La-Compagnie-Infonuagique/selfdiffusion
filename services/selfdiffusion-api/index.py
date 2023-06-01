import json
import os
import boto3

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
    