# POST /insights/engagement/28hr
import argparse
import json
import os
import sys

import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Argparse for cli options. Run `python engagement_totals.py -h` to see list of available arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--tweet_ids", nargs='+', required=True, help="Enter one or more\
                    space delimited Tweet IDs (for example: `-t 123 456`)")
parser.add_argument("-m", "--metrics", nargs='+', help="Overrides default metrics")
args = parser.parse_args()

# Retrieves and stores credential information from the '.env' file
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Generate user context auth (OAuth1)
user_context_auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, TOKEN_SECRET)

# 28hr API endpoint (same for all accounts)
endpoint = "https://data-api.twitter.com/insights/engagement/28hr"


def main():
    request_body = build_request_body(args.tweet_ids)
    try:
        response = requests.post(endpoint, auth=user_context_auth, json=request_body)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(120)

    print(f"Status: {response.status_code}\n", format_response(response))


def build_request_body(tweet_ids):
    # Initialize request body with Tweet IDs and groupings
    request_body = {"tweet_ids": tweet_ids, "engagement_types":
                    ["impressions", "engagements", "favorites", "retweets", "replies",
                     "video_views", "media_views", "media_engagements", "url_clicks",
                     "hashtag_clicks", "detail_expands", "permalink_clicks",
                     "app_install_attempts", "app_opens", "email_tweet", "user_follows",
                     "user_profile_clicks"],
                    "groupings": {"my_grouping": {"group_by": ["tweet.id", "engagement.type"]}}
                    }
    if args.metrics:
        # Update request_body with user supplied metrics passed on the command line (-m option)
        request_body.update(engagement_types=args.metrics)

    return request_body


def format_response(response):
    parsed = json.loads(response.text)
    pretty_print = json.dumps(parsed, indent=2, sort_keys=True)

    return pretty_print

if __name__ == '__main__':
    main()
