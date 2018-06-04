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

role_dict = {}
print 'Indexing roles from system'
resp = rc.get('/roles')
if resp.status_code == 200:
    parsed_resp = json.loads(resp.content)
    for role in parsed_resp:
        role_dict[role['id']] = role['name']
        print '\t{} is {}'.format(role['id'],role['name'])
else:
    sys.exit('Unable to enumerate roles - are you authorized? HTTP {}'.format(resp.status_code))

print 'Retrieving users from system'
resp = rc.get('/users')
if resp.status_code == 200:
    parsed_resp = json.loads(resp.content)
    for users in parsed_resp:
        role_string = ''
        for role in users['role_ids']:
            role_string+=(role_dict[role] + ',')
        print '\tUser {} has roles {}'.format(users['email'],role_string[:-1])
else:
    sys.exit('Unable to retrieve list of users - are you authorized? HTTP {}'.format(resp.status_code))
