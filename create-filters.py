import sys
from pprint import pprint
from datetime import datetime

try:
    from credentials import API_ENDPOINT, API_KEY, API_SECRET
except ImportError:
    sys.exit("Error: please verify credentials file format.")

# Import Tetration client
from tetration import RestClient
import json
import requests.packages.urllib3
import csv

requests.packages.urllib3.disable_warnings()
rc = RestClient(API_ENDPOINT, API_KEY, API_SECRET, verify=False)
if rc:
    print("Connected to TA cluster!")
else:
    print("Failed to connect to TA cluster!")
    sys.exit(1)

start_ip="10.48.58.{}"
numOfPods=6
pod_array = {}
for i in range(1,numOfPods):
    for j in range(0, 4):
        lastByte=25 + i*4 + j
        pod_array[j]=start_ip.format(lastByte)

    pod_query_string_array = {u'type': u'or', u'filters': [{u'field': u'ip', u'type': u'eq', u'value': pod_array[0]}, {u'field': u'ip', u'type': u'eq', u'value': pod_array[1]}, {u'field': u'ip', u'type': u'eq', u'value': pod_array[2]}, {u'field': u'ip', u'type': u'eq', u'value': pod_array[3]}]}
    filter_name = "DXB-Lab-Pod{}".format(i+1)

    print("Built query {}").format(pod_query_string_array)

    req_payload = {
      "app_scope_id": "59e4b74a497d4f36417521c2",
      "name": filter_name,
      "query": pod_query_string_array,
      }
    
    print("POSTing request to TA cluster")
    resp = rc.post('/filters/inventories', json_body=json.dumps(req_payload))
    if resp.status_code == 200:
        parsed_resp = json.loads(resp.content)
        print json.dumps(parsed_resp, indent=4, sort_keys=True)
        filter = parsed_resp['id']
        print '\tCreated filter {}'.format(filter)
    else:
        sys.exit("Something went wrong creating the filter. HTTP {}".format(resp.status_code))
