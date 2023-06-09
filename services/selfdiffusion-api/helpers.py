import json

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