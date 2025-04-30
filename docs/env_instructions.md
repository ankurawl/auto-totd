# Environment Variables Setup

To use this application, you need to set up the following environment variables in a `.env` file in the root directory of the project.

## Required Environment Variables

```
# Google Gemini API Key
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Twitter API Keys
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here
```

## How to Get API Keys

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an account or sign in
3. Create a new API key
4. Copy the API key and paste it into your `.env` file

### Twitter API
1. Visit [Twitter Developer Platform](https://developer.twitter.com/en/portal/dashboard)
2. Create a developer account and an application
3. Generate API keys and tokens
4. Copy the keys and tokens and paste them into your `.env` file

## Important Notes
- Keep your API keys secure and never share them
- Do not commit your `.env` file to version control 