# PUT /jobs/uuid - Accept (-a) or reject (-r) a historical job in the "quoted" stage.
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

# Argparse for cli options. Run `python accept_or_reject_job.py -h` to see list of available arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-j", "--job_url", required=True,
                    help="Pass the `jobURL` value from the 'create_job' phase.")
parser.add_argument("-a", "--accept", help="Pass -a to accept the job.", action="store_true")
parser.add_argument("-r", "--reject", help="Pass -r to reject the job.", action="store_true")
args = parser.parse_args()


def main():
    job_url = args.job_url
    job_uuid = parse_job_uuid(job_url)
    request_body = build_request_body()
    job_action = request_body["status"]

    try:
        print(f"Making request to '{job_action}' the specified job: '{job_uuid}'")
        response = requests.put(url=job_url, auth=(USERNAME, PASSWORD), json=request_body)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(120)

    print(f"Status: {response.status_code}\n", format_response(response))


def build_request_body():
    if args.accept:
        request_body = {"status": "accept"}
    elif args.reject:
        request_body = {"status": "reject"}
    else:
        print("Error: neither 'accept' or 'reject' argument was passed.")

    return request_body


def parse_job_uuid(job_url):
    split_on_slash = job_url.rsplit('/', 1).pop()
    job_uuid = split_on_slash.split('.', 1).pop(0)

    return job_uuid


def format_response(response):
    parsed = json.loads(response.text)
    pretty_print = json.dumps(parsed, indent=2, sort_keys=True)

    return pretty_print

if __name__ == '__main__':
    main()
