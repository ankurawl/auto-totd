# Thought of the Day Generator

A Python-based system to extract thought-of-the-day quotes from web content and post them to Twitter/X.

## Components

1. **acquire_content.py** - Fetches content from URLs listed in sources.txt
2. **prepare_text.py** - Cleans and prepares the text
3. **extract_quotes.py** - Generates quotes using Google Gemini API
4. **post_quote.py** - Posts quotes to Twitter/X

## Setup

1. Install required dependencies:
```
pip install -r requirements.txt
```

2. Set up API keys:
   - Create a `.env` file in the project directory with the following:
```
# Google Gemini API Key
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Twitter API Keys
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here
```

3. Create a `sources.txt` file with URLs to scrape content from:
```
https://example.com/interesting-article
https://another-site.com/content
```

## Usage

Run the scripts in order:

1. Acquire content:
```
python acquire_content.py
```

2. Clean the text:
```
python prepare_text.py
```

3. Generate a quote:
```
python extract_quotes.py
```

4. Post to Twitter/X:
```
python post_quote.py
```

## Command Line Arguments

### extract_quotes.py
- `--api_key` - Provide Google Gemini API key directly (alternatively, set in .env file)

### post_quote.py
- `--api_key` - Twitter API Key
- `--api_secret` - Twitter API Secret
- `--access_token` - Twitter Access Token
- `--access_token_secret` - Twitter Access Token Secret
- `--quote` - Directly provide a quote instead of reading from totd.txt

## Notes

- The system limits web crawling depth to 2 levels to avoid excessive bandwidth usage
- Quotes are generated between 250-500 characters and truncated to 280 for Twitter if necessary
- The system creates sample files (sources.txt) if they don't exist
- The system uses Google's newest Gemini 2.0 models via the google-genai SDK 