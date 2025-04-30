import re
import os

def clean_text(text):
    """Clean and prepare text for quote extraction"""
    # Remove special characters and excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove citation brackets often found in Wikipedia articles
    text = re.sub(r'\[\d+\]', '', text)
    
    # Remove content markers
    text = re.sub(r'--- Content from .* ---', '', text)
    
    # Basic sentence splitting to avoid partial sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter out very short sentences and join them back
    cleaned_text = ' '.join([s for s in sentences if len(s) > 20])
    
    return cleaned_text

def main():
    # Check if raw_content.txt exists
    if not os.path.exists('raw_content.txt'):
        print("raw_content.txt not found. Please run acquire_content.py first.")
        return
    
    # Read content from raw file
    with open('raw_content.txt', 'r', encoding='utf-8') as f:
        raw_content = f.read()
    
    # Clean the content
    cleaned_content = clean_text(raw_content)
    
    # Save cleaned content back to the file
    with open('clean_content.txt', 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"Content cleaned and saved to clean_content.txt")
    print(f"Original size: {len(raw_content)} characters")
    print(f"Cleaned size: {len(cleaned_content)} characters")

if __name__ == "__main__":
    main() 