import json

def lambda_handler(event, _):

    path = event['path']

    # dispatch to correct function
    if path == "/config":
        conf = config()
        return ok_with_payload(conf)
    if path ==  "/balance":
        return ok_with_text("Hello World!")
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
        'body': payload
    }

def config():
    
    return {
        "name": "selfdiffusion-api",
    }
