
import argparse
import json
import os
import ssl
import sys

import requests
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Argparse for cli options. Run `python engagement_totals.py -h` to see list of available arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--chunksize", type=int, help="Overrides default chunksize of '10000'.")
args = parser.parse_args()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
ENDPOINT_LABEL = os.getenv("POWERTRACK_LABEL")

domain = "https://gnip-stream.twitter.com/stream"

endpoint = f"{domain}/powertrack/accounts/{ACCOUNT_NAME}/publishers/twitter/{ENDPOINT_LABEL}.json"

headers = {
    'connection': "keep-alive",
    'accept': 'application/json',
    'Accept-Encoding': 'gzip',
    'gnipkeepalive': '30',
}


def main():
    if args.chunksize:
        chunksize = args.chunksize
    else:
        chunksize = 10000
    timeout = 0
    # Reconnect logic with exponential backoff
    while True:
        get_stream(endpoint, chunksize)
        time.sleep(2 ** timeout)
        timeout += 1


def get_stream(endpoint, chunksize):
    response = requests.get(url=endpoint, auth=(USERNAME, PASSWORD), stream=True, headers=headers)
    for chunk in response.iter_content(chunksize, decode_unicode=True):  # Content gets decoded
        if "\n" or "\r" in chunk:  # Handles keep-alive new lines
            print(chunk)  # Prints keep-alive signal to stdout
        else:
            try:
                print(json.loads(chunk))
            except ValueError:
                sys.stderr.write(f"Error processing JSON: {ValueError} {chunk}\n")


if __name__ == '__main__':
    main()
