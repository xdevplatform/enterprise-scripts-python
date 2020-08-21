# GET /results - Retrieves information about a completed Historical PowerTrack job,
# including a list of URLs that correspond to the data files generated for a completed job.
# Use `download_job.py` script to actually download the data

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

# Argparse for cli options. Run `python job_results.py -h` to see list of available arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data_url", required=True,
                    help="Pass the `dataURL` value returned in the response from a completed job.")
args = parser.parse_args()


def main():
    data_url = args.data_url
    job_uuid = data_url.rsplit('/', 2)[1]
    try:
        print(f"Retrieving results for job: '{job_uuid}'")
        response = requests.get(url=data_url, auth=(USERNAME, PASSWORD))
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
