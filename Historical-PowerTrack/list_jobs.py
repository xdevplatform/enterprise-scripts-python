# POST /jobs - Creates a new Historical PowerTrack job
import argparse
import json
import os
import sys

import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Sets creds from '.env' file
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")

# GET /jobs endpoint for retrieving details for all jobs that are not yet expired
domain = "https://gnip-api.gnip.com"
endpoint = f"{domain}/historical/powertrack/accounts/{ACCOUNT_NAME}/publishers/twitter/jobs.json"


def main():
    try:
        print(f"Retrieving active jobs under your account: '{ACCOUNT_NAME}'...")
        response = requests.get(endpoint, auth=(USERNAME, PASSWORD))
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(120)

    print(f"Status: {response.status_code}\n", format_response(response))


def format_response(response):
    parsed = json.loads(response.text)
    pretty_print = json.dumps(parsed, indent=2, sort_keys=True)

    return pretty_print

if __name__ == '__main__':
    main()
