import os
import argparse
import requests
import base64
import hmac
import hashlib
import urllib.parse
import time
import random
import string
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_oauth_signature(http_method, base_url, params, consumer_secret, token_secret):
    """Generate OAuth 1.0a signature"""
    # Create parameter string
    sorted_params = sorted(params.items())
    param_string = "&".join([f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}" for k, v in sorted_params])
    
    # Create signature base string
    signature_base = f"{http_method}&{urllib.parse.quote(base_url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
    
    # Create signing key
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    
    # Generate signature
    signature = base64.b64encode(
        hmac.new(
            signing_key.encode('utf-8'),
            signature_base.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('utf-8')
    
    return signature

def post_to_twitter(quote, api_key=None, api_secret=None, access_token=None, access_token_secret=None):
    """Post the quote to Twitter/X using Twitter API v2 with OAuth 1.0a"""
    # Use provided credentials or get from environment variables
    api_key = api_key or os.getenv("TWITTER_API_KEY")
    api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
    access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    # Check if credentials are available
    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError("Twitter API credentials not found. Please provide them as arguments or set environment variables.")
    
    # Twitter API v2 endpoint for creating tweets
    url = "https://api.twitter.com/2/tweets"
    
    # Tweet data 
    data = {"text": quote}
    
    # Generate OAuth parameters
    nonce = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    timestamp = str(int(time.time()))
    
    # Prepare OAuth parameters
    oauth_params = {
        'oauth_consumer_key': api_key,
        'oauth_nonce': nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': timestamp,
        'oauth_token': access_token,
        'oauth_version': '1.0'
    }
    
    # Generate signature
    signature = generate_oauth_signature('POST', url, oauth_params, api_secret, access_token_secret)
    oauth_params['oauth_signature'] = signature
    
    # Create Authorization header
    auth_header = 'OAuth ' + ', '.join([f'{k}="{urllib.parse.quote(v, safe="")}"' for k, v in oauth_params.items()])
    
    # Make request
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            tweet_data = response.json()
            tweet_id = tweet_data.get('data', {}).get('id')
            print(f"Tweet posted successfully! Tweet ID: {tweet_id}")
            return True
        else:
            print(f"Error posting to Twitter: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error posting to Twitter: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Post quote to Twitter/X")
    parser.add_argument("--api_key", help="Twitter API Key", default=None)
    parser.add_argument("--api_secret", help="Twitter API Secret", default=None)
    parser.add_argument("--access_token", help="Twitter Access Token", default=None)
    parser.add_argument("--access_token_secret", help="Twitter Access Token Secret", default=None)
    parser.add_argument("--quote", help="Directly provide a quote instead of reading from file", default=None)
    args = parser.parse_args()
    
    # If quote is not provided directly, read from totd.txt
    if not args.quote:
        if not os.path.exists('totd.txt'):
            print("totd.txt not found. Please run extract_quotes.py first or provide a quote with --quote.")
            return
        
        with open('totd.txt', 'r', encoding='utf-8') as f:
            quote = f.read().strip()
    else:
        quote = args.quote
    
    # Ensure quote is not too long for Twitter (280 characters max)
    if len(quote) > 280:
        print(f"Warning: Quote is {len(quote)} characters. Truncating to 280 characters.")
        quote = quote[:277] + "..."
    
    print(f"Posting to Twitter: {quote}")
    
    # Post to Twitter
    success = post_to_twitter(
        quote,
        args.api_key,
        args.api_secret,
        args.access_token,
        args.access_token_secret
    )
    
    if success:
        print("Quote posted successfully to Twitter/X!")
    else:
        print("Failed to post quote to Twitter/X.")

if __name__ == "__main__":
    main() 