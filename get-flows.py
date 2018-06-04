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

requests.packages.urllib3.disable_warnings()

rc = RestClient(API_ENDPOINT, API_KEY, API_SECRET, verify=False)

# you can specify a filter in flow_req
# this GET returns values for filter options
#
# resp = rc.get('/flowsearch/dimensions')
# print json.dumps(resp.json())
#

flow_req = {
    "t0": "2017-05-30T17:00:00-0700", 
    "t1": "2017-05-31T10:00:00-0700",
    "scopeName": "Prod:Opencart",
    "limit": 100,
    "filter": {"type": "and",
        "filters": [
            {"type": "subnet", "field": "src_address", "value": "10.48.58.0/24"},
            {"type": "regex", "field": "dst_hostname", "value": "cp-opencart*"}
        ]
    }
}

resp = rc.post('/flowsearch', json_body=json.dumps(flow_req))
print resp.status_code
if resp.status_code == 200:
    parsed_resp = json.loads(resp.content)
    print json.dumps(parsed_resp, indent=4, sort_keys=True)

