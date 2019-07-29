import argparse
import base64
import json
import os
import ssl
import sys
import zlib

import requests
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Argparse for cli options. Run `python engagement_totals.py -h` to see list of available arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rule_value", required=True, help="Add one or more rules to your stream.")
args = parser.parse_args()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
ENDPOINT_LABEL = os.getenv("POWERTRACK_LABEL")

domain = "https://gnip-api.twitter.com/rules"

endpoint = f"{domain}/powertrack/accounts/{ACCOUNT_NAME}/publishers/twitter/{ENDPOINT_LABEL}.json"


def main():
    rules = {"rules": [{"value": "rule1", "tag": "tag1"}]}
    rules.update(rules=[{"value": args.rule_value}])
    try:
        response = requests.post(url=endpoint, auth=(USERNAME, PASSWORD), json=rules)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(120)

    print(f"Status: {response.status_code}\n", format_response(response))


def add_rule(endpoint, rules):
    # The json param in the request sets the Content-Type in the header to 'application/json'
    response = requests.post(url=endpoint, auth=(USERNAME, PASSWORD), json=rules)

    return response


def format_response(response):
    parsed = json.loads(response.text)
    pretty_print = json.dumps(parsed, indent=2, sort_keys=True)

    return pretty_print


if __name__ == '__main__':
    main()
