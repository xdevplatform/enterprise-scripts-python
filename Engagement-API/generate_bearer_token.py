# -*- coding: utf-8 -*-
# Copyright 2017 Twitter, Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# This script generates a bearer token which can be used to make app-only requests to the Twitter API
# Docs: https://developer.twitter.com/en/docs/basics/authentication/overview/application-only#issuing-application-only-requests

import base64
import requests
import sys
import urllib.parse

oauth_endpoint = 'https://api.twitter.com/oauth2/token'

def main():
    # Prompt user to enter consumer key and consumer secret
    consumer_key = input("Enter your consumer key: ")
    consumer_secret = input("Enter your consumer secret: ")
    try:
        response = generate_bearer_token(consumer_key, consumer_secret)
        print(f"Status: {response.status_code}\n", response.text)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(120)

def generate_bearer_token(consumer_key, consumer_secret):
    """
    Return the bearer token for a given pair of consumer key and secret values.
    """
    consumer_key = urllib.parse.quote(consumer_key)
    consumer_secret = urllib.parse.quote(consumer_secret)
    # Concatenate the url encoded key and secret 
    concatenated_key_and_secret = f"{consumer_key}:{consumer_secret}"
    # Base64 encode the concatenated key and secret
    b64_encoded_key_and_secret = base64.b64encode(concatenated_key_and_secret.encode('utf-8'))
    headers = {
        "Authorization": f"Basic {b64_encoded_key_and_secret.decode('utf-8')}", 
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }
    response = requests.post(oauth_endpoint, headers=headers, data={"grant_type": "client_credentials"})
    
    return response

if __name__ == '__main__':
    main()