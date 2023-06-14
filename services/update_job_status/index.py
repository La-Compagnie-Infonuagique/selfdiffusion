import json
import os
import boto3

def lambda_handler(event, _):

    """ Update the status of a job when the runtime is done with it"""


    # 1. retrieve the job id from the request body
    req_data = json.loads(event['body'])
    job_id = req_data['job_id']

    # 2. update the job status in the database
    job_table = os.environ['JobTableName']

    # 3. update the value of status for this job table in the dynamodb table.
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(job_table)

    table.update_item(
        Key={'job_id': job_id},
        UpdateExpression='SET #statusAttr = :statusValue',
        ExpressionAttributeNames={'#statusAttr': 'status'},
        ExpressionAttributeValues={':statusValue': 'COMPLETED'}
    )

    return

    



