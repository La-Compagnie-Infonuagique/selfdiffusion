import json
import os
import boto3
import runpod
import uuid

from helpers import not_found, ok_with_text, ok_with_payload, error_with_text

class GPUNotAvailableError(Exception):
    pass

def lambda_handler(event, _):

    # Extract auth and path for dispatch.
    path = event['path']
    auth_context = event['requestContext']['authorizer']

    # dispatch to correct function.
    if path == "/config":
        conf = config()
        return ok_with_payload(conf)

    elif path ==  "/balance":
        payload = balance(auth_context)
        return ok_with_payload(payload)

    elif path == "/runtime":
        req_data = json.loads(event['body'])
        try:
            payload = runtime(auth_context, req_data)
            return ok_with_payload(payload)
        except GPUNotAvailableError as e:
            return error_with_text(str(e), 503)

    elif path == "/generate":
        req_data = json.loads(event['body'])
        payload = mock_generate(auth_context, req_data)
        return ok_with_payload(payload)

    elif path == "/result":
        req_data = json.loads(event['body'])
        payload = mock_result(auth_context, req_data)
        return ok_with_payload(payload)

    elif path == "/generatedev":
        req_data = json.loads(event['body'])
        payload = generate(auth_context, req_data)
        return ok_with_payload(payload)

    else:
        return not_found()

def generate(auth_context, req_data):
    # get cognito user
    username = auth_context['claims']['cognito:username']

    # Get the job table 
    job_table_name = os.environ['JobTableName']

    # Generate the UUID for the job 
    job_id = str(uuid.uuid4())

    # Create a JOB payoad
    job_data = {
        'job_id': job_id,
        'username': username,
        'status': 'PENDING',
        'job_type': 'INFERENCE',
        'args': req_data
    }

    # write that to the dynamoDB table
    dynamodb = boto3.resource('dynamodb')
    job_table = dynamodb.Table(job_table_name)

    job_table.put_item(Item=job_data)

    # also write the payload to the SQS Job Queue.
    ## Get the job queue url
    job_queue_url = os.environ['JobQueueUrl']

    sqs = boto3.client('sqs')

    print(f"Sending message to {job_queue_url}")
    response = sqs.send_message(
        QueueUrl=job_queue_url,
        MessageBody=json.dumps(job_data)
    )

    print(response)

    return {'job_id': job_id}


def mock_generate(auth_context, req_data):
    """ returns a phony job id """
    job_id = str(uuid.uuid4())

    return {'job_id': job_id}

def mock_result(auth_context, req_data):
    """ returns a list of url for the images generated """
    JOB_ID = '4910499e-3356-4b4d-a872-5c6ebd64b819'

    # get the bucket name
    bucket_name = os.environ['JobResultBucketName']

    # get a list of all files under job_id
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    urls = []
    for obj in bucket.objects.filter(Prefix=JOB_ID):
        url = f"https://{bucket_name}.s3.amazonaws.com/{obj.key}"
        urls.append(url)

    return {'urls':urls}





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


    