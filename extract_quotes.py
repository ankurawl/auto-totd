import os
import random
import argparse
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file (for API key)
load_dotenv()

def extract_chunk(text, min_size=2000, max_size=3000):
    """Extract a random chunk of text of appropriate size"""
    # If text is shorter than min_size, return the whole text
    if len(text) <= min_size:
        return text
    
    # Choose a random starting point
    max_start = len(text) - max_size
    if max_start <= 0:
        start = 0
    else:
        start = random.randint(0, max_start)
    
    # Get a chunk of text
    end = min(start + max_size, len(text))
    chunk = text[start:end]
    
    # Try to find sentence boundaries
    # Adjust start to the beginning of a sentence if possible
    if start > 0:
        first_period = chunk.find('. ')
        if first_period != -1:
            chunk = chunk[first_period + 2:]
    
    # Adjust end to the end of a sentence if possible
    last_period = chunk.rfind('. ')
    if last_period != -1:
        chunk = chunk[:last_period + 1]
    
    return chunk

def generate_quote_with_gemini(text_chunk, api_key=None):
    """Generate a thought of the day quote using Google Gemini API"""
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google Gemini API key not found. Please provide it as argument or set GOOGLE_API_KEY environment variable.")
        client = genai.Client(api_key=api_key)
    
    # The prompt for generating quotes
    prompt = f"""
    Based on the following text, create an inspirational thought-of-the-day quote that is 
    between 250-500 characters. The quote should be profound, insightful, and 
    standalone (not requiring context to understand).
    
    The quote should feel original and not directly copied from the source text.
    
    Text:
    {text_chunk}
    
    Provide only the quote as your response, without any additional text, introduction or explanation.
    """
    
    try:
        # Initialize the Gemini model (using gemini-2.0-flash, a fast and efficient model for this task)
        # Can also use gemini-2.0-pro for higher quality if needed
        model_name = "gemini-2.0-flash"
        print(f"Using model: {model_name}")
        
        # Generate content
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        # Extract the quote
        quote = response.text.strip()
        
        # Ensure the quote is within the desired character range
        if len(quote) < 250:
            print(f"Warning: Generated quote is only {len(quote)} characters. Requested minimum was 250.")
        elif len(quote) > 500:
            print(f"Warning: Generated quote is {len(quote)} characters. Truncating to 500.")
            quote = quote[:497] + "..."
        
        return quote
    
    except Exception as e:
        print(f"Error generating quote: {str(e)}")
        print("If you're seeing a model not found error, please try using a different model.")
        print("Available models may include: gemini-2.0-flash, gemini-2.0-pro, gemini-1.5-flash, gemini-1.5-pro")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate thought-of-the-day quotes using Google Gemini API")
    parser.add_argument("--api_key", help="Google Gemini API key", default=None)
    args = parser.parse_args()
    
    # Check if clean_content.txt exists
    content_file = 'clean_content.txt'
    if not os.path.exists(content_file):
        if os.path.exists('raw_content.txt'):
            content_file = 'raw_content.txt'
            print("clean_content.txt not found. Using raw_content.txt instead.")
        else:
            print("Neither clean_content.txt nor raw_content.txt found. Please run previous steps first.")
            return
    
    # Read content from file
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract a reasonable chunk of text to send to the API
    text_chunk = extract_chunk(content)
    
    # Generate quote
    quote = generate_quote_with_gemini(text_chunk, args.api_key)
    
    if quote:
        # Save quote to totd.txt
        with open('totd.txt', 'w', encoding='utf-8') as f:
            f.write(quote)
        
        print(f"Quote generated and saved to totd.txt")
        print(f"Quote length: {len(quote)} characters")
        print(f"Quote: {quote}")
    else:
        print("Failed to generate quote.")

if __name__ == "__main__":
    main() 