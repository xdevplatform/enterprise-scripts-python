# Pass in dataURL to retrieve list of URLs and download corresponding data files

import argparse
import gzip
import json
import os

import requests
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Sets creds from '.env' file
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")

# Argparse for cli options. Run `python download_job.py -h` to see list of available arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data_url", required=True,
                    help="Pass the `dataURL` value returned in the response from a completed job. URL ends in /results.json")
args = parser.parse_args()


def main():
    data_url = args.data_url
    job_uuid = data_url.rsplit('/', 2)[1]

    urls = get_url_list(data_url)
    total_files = len(urls)
    files_retrieved = 0

    # Create downloads directory 
    if not os.path.exists('./downloads'):
        os.makedirs('./downloads')

    for link in urls:
        file_name = create_file_name(link, job_uuid)
        files_retrieved += 1
        # Downloads file if it doesn't exist (helps if restarting download due to error)
        if not os.path.isfile(f"./downloads/{file_name}"):
            data = get_data(link)
            # Verbose - comment out line below to remove verbose print statement
            print(f"Downloading file {files_retrieved}/{total_files}...")
            with open(f"./downloads/{file_name}", "w") as outfile:
                json.dump(data, outfile)


# Function that gets the urls containing the actual Tweet data
def get_url_list(url):
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code is not 200:
        print(f"The request returned an error: {response.text}")
    parsed = json.loads(response.text)
    return parsed['urlList']


# Function that gets tweets data from each url in the results.json
def get_data(url):
    headers = {
        "Accept-Encoding": "gzip"
    }

    response = requests.get(url, headers=headers)
    if response.status_code is not 200:
        print(f"The request returned an error: {response.text}")
    result = gzip.decompress(response.content)
    list_items = result.decode('utf-8').split('\n')
    # list items contains a list of strings
    data = []
    for item in list_items:
        # convert each string to json
        data.append(json.loads(item))
    return data;


# Helper function that creates a file name from url string to store the json
def create_file_name(url, job_uuid):
    left = f"{job_uuid}/"
    right = ".json.gz"

    file_name = url[url.index(left) + len(left):url.index(right)].replace("/", "_")
    return f"{file_name}.json"


if __name__ == '__main__':
    main()
