from requests import Session
import json
import argparse
import configparser
import os, sys

# handle cmd arguments
parser = argparse.ArgumentParser(description="Submit test data to the FLEXCoop API. All options can also be defined "
                                             "in the configuration ini file.")
parser.add_argument('-c', '--config', help='config file to use. (default: populate_db.ini)',
                    default='populate_db.ini')

parser.add_argument('-d', '--delete', help='delete database entries before creating new ones. (default: false)',
                    default=False)
parser.add_argument('-j', '--json', help='JSON file with test data. (default: test_data.json)')
parser.add_argument('-u', '--url', help='base URL for API calls')
parser.add_argument('-t', '--token', help='OAuth2 API Token')
args = parser.parse_args()

# load config
if not os.path.exists(args.config):
    raise IOError("Error: config file not found")


config = configparser.ConfigParser()
config.read(args.config)

if args.url:
    base_url = args.url
elif config.has_option('DEFAULT', 'base_url'):
    base_url = config['DEFAULT']['base_url']
else:
    print("No base URL found. User -u or set base_url in the ini file")
    sys.exit(-1)

if args.token:
    token = args.token
elif config.has_option('DEFAULT', 'token'):
    token = config['DEFAULT']['token']
else:
    print("No token found. Use -t or set token in the ini file")
    sys.exit(-1)

if args.delete:
    delete_first = True
elif config.has_option('DEFAULT', 'delete'):
    delete_first = config['DEFAULT']['delete']
else:
    delete_first = False

if args.json:
    input_data = args.json
elif config.has_option('DEFAULT', 'json'):
    input_data = config['DEFAULT']['json']
else:
    input_data = 'test_data.json'

headers = {'accept': 'application/xml', 'Authorization': token, "Content-Type": "application/json"}


session = Session()
session.headers = headers

with open(input_data) as json_file:
    json_data = json.load(json_file)


for domain in json_data:
    if delete_first:
        session.delete(base_url + domain)

    for item in json_data[domain]:
        r = session.post(base_url + domain, data=json.dumps(item))
        print("HTTP status code: " + str(r.status_code) + " while connecting to " + base_url + domain)
        if r.status_code == 201:
            print(json.dumps(item))
        else:
            print(r.text)
        print('=================================================')






