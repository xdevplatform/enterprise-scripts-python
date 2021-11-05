# -*- coding: utf-8 -*-
# Copyright 2017 Twitter, Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# This script generates a user's access tokens which can be used to make requests on behalf of the user, also known as OAuth 1.0a (user context) authentication method
# Docs: https://developer.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens

import os
import sys
import requests
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Retrieves and stores credential information from the '.env' file
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Request an OAuth Request Token. This is the first step of the 3-legged OAuth flow. This generates a token that you can use to request user authorization for access.
def request_token():

    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri='oob')

    url = "https://api.twitter.com/oauth/request_token"

    try:
        response = oauth.fetch_request_token(url)
        resource_owner_oauth_token = response.get('oauth_token')
        resource_owner_oauth_token_secret = response.get('oauth_token_secret')
    except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(120)
    
    return resource_owner_oauth_token, resource_owner_oauth_token_secret

# Use the OAuth Request Token received in the previous step to redirect the user to authorize your developer App for access.
def get_user_authorization(resource_owner_oauth_token):

    authorization_url = f"https://api.twitter.com/oauth/authorize?oauth_token={resource_owner_oauth_token}"
    authorization_pin = input(f"Copy and past the following URL in your web browser to grant access to this application: {authorization_url} \n Paste PIN here: ")

    return(authorization_pin)

# Exchange the OAuth Request Token you obtained previously for the user’s Access Tokens.
def get_user_access_tokens(resource_owner_oauth_token, resource_owner_oauth_token_secret, authorization_pin):

    oauth = OAuth1Session(CONSUMER_KEY, 
                            client_secret=CONSUMER_SECRET, 
                            resource_owner_key=resource_owner_oauth_token, 
                            resource_owner_secret=resource_owner_oauth_token_secret, 
                            verifier=authorization_pin)
    
    url = "https://api.twitter.com/oauth/access_token"

    try: 
        response = oauth.fetch_access_token(url)
        access_token = response['oauth_token']
        access_token_secret = response['oauth_token_secret']
        user_id = response['user_id']
        screen_name = response['screen_name']
    except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(120)

    print(access_token, access_token_secret, user_id, screen_name)
    return(access_token, access_token_secret, user_id, screen_name)

if __name__ == '__main__':
    resource_owner_oauth_token, resource_owner_oauth_token_secret = request_token()
    authorization_pin = get_user_authorization(resource_owner_oauth_token)
    access_token, access_token_secret, user_id, screen_name = get_user_access_tokens(resource_owner_oauth_token, resource_owner_oauth_token_secret, authorization_pin)
    
    