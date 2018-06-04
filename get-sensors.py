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

################ GET Sensors
print 'Retrieving all sensors, excluding sensors in Tetration VRF'
print '-' * 40
resp = rc.get('/sensors')
if resp:
    sensors = resp.json()
    for i in sensors['results']:
        if i['interfaces'][0]['vrf'] == 'Tetration':
            continue
        hostname = i['host_name']
        agentmode = i['agent_type']
        print('Sensor {} is running {}').format(hostname, agentmode)
else:
    sys.exit("No data returned! HTTP {}".format(resp.status_code))



