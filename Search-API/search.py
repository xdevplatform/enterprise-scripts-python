# Enterprise Search Tweets - Make a data or counts request against 30-day or Full-Archive Search
# Now supports a JSON request file, option to select objects (fields) to parse and
# a function for determining Tweet type (pass '-d' option to have this added to response)

import argparse
import json
import os
import sys

import pandas as pd
import requests
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Argparse for cli options. Run `python searcy.py -h` to see the list of arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--object_selector", help="Specify root-level objects to parse for\
                    (e.g., id_str, text, favorite_count)", nargs='*')
parser.add_argument("-r", "--request_file", help="Use json file for request body", action="store_true")
parser.add_argument("-d", "--determine_tweet_type", help="Helper fn that classifies Tweets by type\
                    (e.g., RT, Reply)", action="store_true")
parser.add_argument("-q", "--query", help="A valid query up to 2,048 characters")
parser.add_argument("-c", "--counts", help="Make request to 'counts' endpoint", action="store_true")
parser.add_argument("-f", "--from_date", help="Oldest date from which results will be provided")
parser.add_argument("-t", "--to_date", help="Most recent date to which results will be provided")
parser.add_argument("-m", "--max_results", help="Maximum number of results returned by a single\
                    request/response cycle (range: 10-500, default: 100)")
parser.add_argument("-b", "--bucket", choices=['day', 'hour', 'minute'],
                    help="The unit of time for which count data will be provided.")
parser.add_argument("-n", "--next", help="Auto paginate through next tokens", action="store_true")
parser.add_argument("-p", "--pretty_print", help="Pretty print the results", action="store_true")
args = parser.parse_args()

# Retrieves and stores credential information from the '.env' file
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
ENDPOINT_LABEL = os.getenv("SEARCH_LABEL")
ARCHIVE = os.getenv ("SEARCH_ARCHIVE")


def main():
    search_endpoint = determine_endpoint()
    # Build request body from file if it exists, else use cli args
    request_body = build_request_body()

    # First scenario: request for counts
    if args.counts:
        counts_response = make_request(search_endpoint, request_body)
        print(f"Status: {counts_response.status_code}\n", format_response(counts_response), "\n")
        # Deserialize json data
        response_dict = (json.loads(counts_response.text))
        # Ensure results are either complete (no next token) or pagination flag (-n) wasn't requested
        if response_dict.get("next") is None or args.next is False:
            print("Request complete.")
        elif response_dict.get("next") is not None and args.next:
            next_token = response_dict.get("next")
            request_count = 1  # Keep track of the number of requests being made (pagination)
            counts_sum_total = response_dict["totalCount"] # Init sum total with totalCount from first resp 
            while next_token is not None:
                request_body.update(next=next_token)
                response = make_request(search_endpoint, request_body)
                print(format_response(response), "\n")
                # Deserialize n response and grab the 'next' token
                n_response_dict = (json.loads(response.text))
                next_token = n_response_dict.get("next")
                counts_sum_total += n_response_dict["totalCount"]
                request_count += 1  # Iterates the request counter

            print(f"Done paginating.\nTotal requests made: {request_count}\nTotal count: {counts_sum_total}")

    # Scenario 2: request for Tweets
    else:
        if args.object_selector is None:
            data_response = make_request(search_endpoint, request_body)
            # print(f"Status: {data_response.status_code}\n", format_response(data_response), "\n")
            # Deserialize json data
            response_dict = (json.loads(data_response.text))
            # Ensure results are either complete (no next token) or pagination flag (-n) wasn't requested
            if response_dict.get("next") is None or args.next is False:
                # print("Request complete.")
                sys.exit() # REMOVE
            elif response_dict.get("next") is not None and args.next:
                next_token = response_dict.get("next")
                request_count = 1  # Keep track of the number of requests being made (pagination)
                while next_token is not None:
                    request_body.update(next=next_token)
                    response = make_request(search_endpoint, request_body)
                    print(format_response(response), "\n")
                    # Deserialize n response and grab the 'next' token
                    n_response_dict = (json.loads(response.text))
                    next_token = n_response_dict.get("next")
                    request_count += 1  # Iterates the request counter

                # print(f"Done paginating.\nTotal requests made: {request_count}")

        elif args.object_selector is not None:
            data_response = make_request(search_endpoint, request_body)
            response_dict = (json.loads(data_response.text)) # Deserialize json data
            # Create Python dict from results list
            tweet_results = response_dict["results"]
            objects_to_parse = args.object_selector
            custom_dict = dict.fromkeys(objects_to_parse)
            parsed_tweets = []
            # Iterate Tweet results to create custom output with only requested objects from payload
            for tweet in tweet_results:
                for key in custom_dict:
                    custom_dict[key] = tweet[key]
                    if args.determine_tweet_type:
                        tweet_type = determine_tweet_type(tweet)
                        custom_dict["tweet_type"] = tweet_type
                        # Add a copy of new dict element to parsed Tweets list
                        parsed_tweets.append(custom_dict.copy())
                    else:
                        # Add a copy of new dict element to parsed Tweets list
                        parsed_tweets.append(custom_dict.copy())
                # df = pd.DataFrame.from_dict(custom_dict, orient ='index')

            # json_output = json.dumps(custom_dict, indent=4)
            print(parsed_tweets)
            # Ensure results are either complete (no next token) or pagination flag (-n) wasn't requested
            if response_dict.get("next") is None or args.next is False:
                print("Request complete.")
            elif response_dict.get("next") is not None and args.next:
                next_token = response_dict.get("next")
                request_count = 1  # Keep track of the number of requests being made (pagination)
                while next_token is not None:
                    # Update request_body with next token
                    request_body.update(next=next_token)
                    # Make the request with the next token
                    response = make_request(search_endpoint, request_body)
                    print(format_response(response), "\n")
                    # Deserialize n response and grab the 'next' token
                    n_response_dict = (json.loads(response.text))
                    next_token = n_response_dict.get("next")
                    request_count += 1  # Iterates the request counter

                print(f"Done paginating.\nTotal requests made: {request_count}")



def determine_endpoint():
    if args.counts:
        endpoint = f"https://gnip-api.twitter.com/search/{ARCHIVE}/accounts/{ACCOUNT_NAME}/{ENDPOINT_LABEL}/counts.json"
        request_type = "tweet_counts"
    else:
        endpoint = f"https://gnip-api.twitter.com/search/{ARCHIVE}/accounts/{ACCOUNT_NAME}/{ENDPOINT_LABEL}.json"
        request_type = "tweet_data"
    return endpoint


def build_request_body():
    # Request file will override CLI options
    if args.request_file is True:
        with open("request.json", "r") as read_file:
            request_body = json.load(read_file)
    else:
        request_body = {}
        if args.query:
            request_body.update(query=args.query)
        if args.from_date:
            request_body.update(fromDate=args.from_date)
        if args.to_date:
            request_body.update(toDate=args.to_date)
        if args.max_results:
            request_body.update(maxResults=args.max_results)
        if args.bucket:
            request_body.update(bucket=args.bucket)

    return request_body


def make_request(endpoint, request_body):
    try:
        response = requests.post(url=endpoint, auth=(USERNAME, PASSWORD), json=request_body)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(120)

    return response


def format_response(response):
    if args.pretty_print:
        formatted_response = json.dumps(json.loads(response.text), indent=2, sort_keys=True)
    else:
        formatted_response = response.text

    return formatted_response


def determine_tweet_type(tweet):
    # Check for reply indicator first
    if tweet["in_reply_to_status_id"] is not None:
        tweet_type = "Reply Tweet"
    # Check boolean quote status field but make sure it's not a Retweet (of a Quote Tweet) 
    elif tweet["is_quote_status"] is True and not tweet["text"].startswith("RT"):
        tweet_type = "Quote Tweet"
    # Check both indicators of a Retweet
    elif tweet["text"].startswith("RT") and tweet.get("retweeted_status") is not None:
        tweet_type = "Retweet"
    # If it's not a Reply, QT, or RT then it's an 'original' Tweet
    else:
        tweet_type = "Original Tweet"

    return tweet_type


# def parse_tweets(response_dict):
#     if args.object_selector:
#         # Create Python dict from results list
#         tweet_results = response_dict["results"]

#         objects_to_parse = args.object_selector
#         custom_dict = dict.fromkeys(objects_to_parse)
#         # Iterate Tweet results to create custom output with only requested objects from payload
#         tweet_list = []
#         for tweet in tweet_results:
#             for key in custom_dict:
#                 custom_dict[key] = tweet[key]
#             tweet_list.append(custom_dict)
#             # Serialize python dict to json
#             json_output = json.dumps(custom_dict, indent=4)
#             # print(json_output)
#         print(tweet_list.length)



if __name__ == '__main__':
    main()
