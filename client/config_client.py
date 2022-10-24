import json
import http.client
from urllib.parse import urlparse
import os
def get_queue_config(type,key):
    headers = {'Content-Type': 'application/json',
                'configurationType':'application/router',
                'user-agent': 'router'}

    # CONFIGURATION_SERVICE_URL="https://5icwu6fpg2.execute-api.us-east-1.amazonaws.com/development/"
    CONFIGURATION_SERVICE_URL= os.getenv('CONFIGURATION_SERVICE_URL') #"https://j89j8rfp8b.execute-api.us-east-1.amazonaws.com/development/"

    queue_config_url=CONFIGURATION_SERVICE_URL+key+'/'+type
    url = urlparse(queue_config_url)
    if url.scheme == 'http':
        conn = http.client.HTTPConnection(url.hostname, url.port)
    else:
        conn = http.client.HTTPSConnection(url.hostname, url.port)
    conn.request("GET", url.path, headers=headers)
    response = conn.getresponse().read().decode()
    print('response: ',response)
    responseJson = json.loads(response)
    conn.close()
    return responseJson