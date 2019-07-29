# POST /jobs - Creates a new Historical PowerTrack job
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

# POST /jobs endpoint for creating a new Historical PowerTrack job
domain = "https://gnip-api.gnip.com"
endpoint = f"{domain}/historical/powertrack/accounts/{ACCOUNT_NAME}/publishers/twitter/jobs.json"


def main():
    if os.path.exists('historical_job.json') and os.path.getsize('historical_job.json') > 0:
        job_data = build_request_body("historical_job.json")
        try:
            print("Creating Historical PowerTrack job...")
            response = requests.post(endpoint, auth=(USERNAME, PASSWORD), json=job_data)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(120)
    else:
        print("Error: Missing 'historical_job.json' file in current directory.\n")

    print(f"Status: {response.status_code}\n", format_response(response))


def build_request_body(job_file):
    with open("historical_job.json", "r") as read_file:
        job_data = json.load(read_file)

    return job_data


def format_response(response):
    parsed = json.loads(response.text)
    pretty_print = json.dumps(parsed, indent=2, sort_keys=True)

    return pretty_print

if __name__ == '__main__':
    main()
