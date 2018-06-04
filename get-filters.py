import sys
from pprint import pprint
from datetime import datetime
import json

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

################ GET Sensors
print 'Retrieving all filters'
print '-' * 40
resp = rc.get('/filters/inventories')
if resp:
    filters = resp.json()
    for filter in filters:
        print("Filter {} has ID {}. It is in scope ID {}. The query is {}").format(
               filter["id"],
               filter["name"],
               filter["app_scope_id"],
               filter["query"])
        print '-' * 40
else:
    sys.exit("No data returned! HTTP {}".format(resp.status_code))



