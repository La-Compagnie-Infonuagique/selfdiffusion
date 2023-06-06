"""
RunPod | API Wrapper | GraphQL
"""

import json
from typing import Any, Dict

import urllib3

http = urllib3.PoolManager()



def run_graphql_query(query: str) -> Dict[str, Any]:
    '''
    Run a GraphQL query
    '''
    from runpod import api_key  # pylint: disable=import-outside-toplevel, cyclic-import

    print (api_key)
    url = f"https://api.runpod.io/graphql?api_key={api_key}"
    headers = {
        "Content-Type": "application/json",
    }
    data = json.dumps({"query": query})
    response = http.request("POST",url, headers=headers, body=data, timeout=30)

    body = response.data.decode('utf-8')
    resp_data = json.loads(body)

    return resp_data
