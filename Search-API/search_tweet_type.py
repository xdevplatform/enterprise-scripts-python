# Enterprise Search Tweets - Data request with Tweet type function to demonstrate how to classify Tweets
# Supports data request only (not counts) and returns parsed Tweet payload (only select fields)
import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Argparse for cli options. Run `python search_tweet_type.py -h` to see the list of arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--request_file", help="Use json file for request body",
                    action="store_true")
parser.add_argument("-q", "--query", help="A valid query up to 2,048 characters")
parser.add_argument("-f", "--from_date", help="Oldest date from which results will be provided")
parser.add_argument("-t", "--to_date", help="Most recent date to which results will be provided")
parser.add_argument("-m", "--max_results", help="Maximum number of results returned by a single\
                    request/response cycle (range: 10-500, default: 100)")
parser.add_argument("-b", "--bucket", choices=['day', 'hour', 'minute'],
                    help="The unit of time for which count data will be provided.")
parser.add_argument("-n", "--next", help="Auto paginate through next tokens", action="store_true")
args = parser.parse_args()

# Retrieves and stores credential information from the '.env' file
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
ENDPOINT_LABEL = os.getenv("SEARCH_LABEL")
ARCHIVE = os.getenv ("SEARCH_ARCHIVE")


def main():
    search_endpoint = f"https://gnip-api.twitter.com/search/{ARCHIVE}/accounts/{ACCOUNT_NAME}/{ENDPOINT_LABEL}.json"
    # Build request body from file if it exists, else use cli args
    request_body = build_request_body()
    # Make first request
    first_response = make_request(search_endpoint, request_body)
    # Deserialize json response
    json_response = (json.loads(first_response.text))
    # Create Python dict from results list
    tweet_results = json_response["results"]
    parsed_results = { "parsed_results": [] }

    # Loop through Tweet results to test for type, extended Tweet, and parse JSON
    for tweet in tweet_results:
        extended_tweet = check_for_extended_tweet(tweet)
        tweet_type = determine_tweet_type(tweet)
        if extended_tweet is True:
            text = tweet["extended_tweet"]["full_text"]
        else:
            text = tweet["text"]
        custom_dict = { 
                "tweet_id": tweet["id_str"],
                "text": text,
                "tweet_type": tweet_type,
                "hyperlink": "https://twitter.com/twitter/status/" + tweet["id_str"]
        }
        parsed_results["parsed_results"].append(custom_dict) # Add Tweet to parsed_results list
    print(json.dumps(parsed_results, indent=2, sort_keys=True))

    # Pagination logic (if -n flag is passed, paginate through the results)
    if json_response.get("next") is None or args.next is False:
        print(f"Request complete.")
    elif json_response.get("next") is not None and args.next:
        next_token = json_response.get("next")
        request_count = 1  # Keep track of the number of requests being made (pagination) 
        while next_token is not None:
            # Update request_body with next token
            request_body.update(next=next_token)
            # Make the request with the next token
            response = make_request(search_endpoint, request_body)
            parsed_results = { "parsed_results": [] }
            # Loop through Tweet results to test for type, extended Tweet, and parse JSON
            for tweet in tweet_results:
                extended_tweet = check_for_extended_tweet(tweet)
                tweet_type = determine_tweet_type(tweet)
                if extended_tweet is True:
                    text = tweet["extended_tweet"]["full_text"]
                else:
                    text = tweet["text"]
                custom_dict = { 
                        "tweet_id": tweet["id_str"],
                        "text": text,
                        "tweet_type": tweet_type,
                        "hyperlink": "https://twitter.com/twitter/status/" + tweet["id_str"]
                }
                parsed_results["parsed_results"].append(custom_dict) # Add Tweet to parsed_results
            print(json.dumps(parsed_results, indent=2, sort_keys=True))
            # Parse n response and it's 'next' token
            n_response = (json.loads(response.text))
            next_token = n_response.get("next")
            # Iterates the request counter
            request_count += 1
        print(f"Done paginating.\nTotal requests made: {request_count}")


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
    else:
        tweet_type = "Original Tweet"

    return tweet_type  


def check_for_extended_tweet(tweet):
    try:
       value = tweet["extended_tweet"]
       return True
    except KeyError:
        return False


if __name__ == '__main__':
    main()
