# Creates a new job with the Historical PowerTrack API
import argparse
import json
import os
import sys

import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Argparse for cli options. Run `python monitor_job.py -h` to see list of available arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-j", "--job_url", required=True,
                    help="Pass the `jobURL` value from the 'create_job' phase.")
args = parser.parse_args()

# Sets creds from '.env' file
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")


def main():
    job_url = args.job_url
    job_uuid = parse_job_uuid(job_url)

    try:
        print(f"Checking the status of your job: {job_uuid}...")
        response = requests.get(job_url, auth=(USERNAME, PASSWORD))
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(120)

    print(f"Status: {response.status_code}\n", format_response(response))


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
