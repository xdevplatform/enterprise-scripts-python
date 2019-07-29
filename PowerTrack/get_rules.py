import json
import os
import sys

import requests
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
ENDPOINT_LABEL = os.getenv("POWERTRACK_LABEL")

domain = "https://gnip-api.twitter.com/rules"

endpoint = f"{domain}/powertrack/accounts/{ACCOUNT_NAME}/publishers/twitter/{ENDPOINT_LABEL}.json"


def main():
    try:
        response = requests.get(url=endpoint, auth=(USERNAME, PASSWORD))
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
