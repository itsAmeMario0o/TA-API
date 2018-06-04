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

with open('plx_users.csv', 'rb') as fp:
    reader = csv.reader(fp)
    for row in reader:
        print row

sys.exit(666)

requests.packages.urllib3.disable_warnings()

email = 'averri@cisco.com'
rc = RestClient(API_ENDPOINT, API_KEY, API_SECRET, verify=False)


role_dict = {}
print 'Indexing roles from system'
resp = rc.get('/roles')
if resp.status_code == 200:
    parsed_resp = json.loads(resp.content)
    for role in parsed_resp:
        role_dict[role['name']] = role['id']
        print '\t{} is {}'.format(role['name'],role['id'])
else:
    sys.exit('Unable to enumerate roles - are you authorized? HTTP {}'.format(resp.status_code))

print 'Retrieving list of users from system'
resp = rc.get('/users')
if resp.status_code == 200:
    parsed_resp = json.loads(resp.content)
    for users in parsed_resp:
        print '\t{}'.format(users['email'])
        if users['email'] == email:
            sys.exit('User {} exists; exiting'.format(email))
       
print 'Creating {}'.format(email)

req_payload = {
    "first_name": "Andrea",
    "last_name": "Verri",
    "email": "averri@cisco.com"
    }  
resp = rc.post('/users', json_body=json.dumps(req_payload))
if resp.status_code == 200:
    parsed_resp = json.loads(resp.content)
    print json.dumps(parsed_resp, indent=4, sort_keys=True)
    userid = parsed_resp['id']
    print '\tCreated userid {}'.format(userid)
else:
    sys.exit("Something went wrong creating the user. HTTP {}".format(resp.status_code))


role_id = role_dict['Lab User']
print 'Adding role {} to user'.format(role_id)
req_data = {}
req_data['role_id'] = role_id
json_data = json.dumps(req_data)

resp = rc.put('/users/' + userid + '/add_role', json_body=json.dumps(req_data))
print resp.status_code
if resp.status_code == 200:
    parsed_resp = json.loads(resp.content)
    print json.dumps(parsed_resp, indent=4, sort_keys=True)

