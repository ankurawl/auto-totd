import re
import os
import html

def clean_text(text):
    """Clean and prepare text for quote extraction"""
    # Find all article sections
    article_sections = re.findall(r'--- Article: (https?://[^\s]+) ---\s*([\s\S]*?)(?=--- Article:|$)', text)
    
    cleaned_articles = []
    
    for url, content in article_sections:
        # Step 1: Fix encoding and remove unwanted content
        
        # Replace HTML entities with proper characters
        content = html.unescape(content)
        
        # Fix common encoding issues
        content = content.replace('â€"', '-')
        content = content.replace('â€™', "'")
        content = content.replace('â€œ', '"')
        content = content.replace('â€', '"')
        
        # Remove common blog elements
        content = re.sub(r'Share this post', '', content)
        content = re.sub(r'Thanks for reading.*?Subscribe for free to receive new posts.*?', '', content, flags=re.DOTALL)
        
        # Remove citations and other markers
        content = re.sub(r'\[\d+\]', '', content)
        
        # Step 2: Process text line by line to form proper paragraphs
        
        # First normalize line breaks
        content = re.sub(r'\r\n?', '\n', content)
        
        # Split into lines and begin processing
        lines = content.split('\n')
        paragraphs = []
        current_para = []
        
        for line in lines:
            clean_line = line.strip()
            if clean_line:  # If line contains text
                current_para.append(clean_line)
            elif current_para:  # We've hit an empty line after collecting text
                # Join the current paragraph with spaces
                paragraph_text = ' '.join(current_para)
                # Clean up any remaining excess whitespace
                paragraph_text = re.sub(r'\s+', ' ', paragraph_text).strip()
                paragraphs.append(paragraph_text)
                current_para = []
        
        # Don't forget the last paragraph
        if current_para:
            paragraph_text = ' '.join(current_para)
            paragraph_text = re.sub(r'\s+', ' ', paragraph_text).strip()
            paragraphs.append(paragraph_text)
        
        # Step 3: Filter out paragraphs that are too short
        meaningful_paragraphs = [p for p in paragraphs if len(p) >= 40]
        
        if not meaningful_paragraphs:
            continue
            
        # Format the article with proper paragraphs
        clean_article = '\n\n'.join(meaningful_paragraphs)
        
        # Add the article to our collection
        cleaned_articles.append(f"--- From: {url} ---\n\n{clean_article}")
    
    return '\n\n\n'.join(cleaned_articles)

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
    
    word_count = len(re.findall(r'\b\w+\b', cleaned_content))
    print(f"Content cleaned and saved to clean_content.txt")
    print(f"Original size: {len(raw_content)} characters")
    print(f"Cleaned size: {len(cleaned_content)} characters")
    print(f"Retention rate: {(len(cleaned_content) / len(raw_content) * 100):.1f}%")
    print(f"Word count: {word_count} words")
    
    # Calculate the number of potential quotes
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_content)
    potential_quotes = [s for s in sentences if 200 <= len(s) <= 250]
    print(f"Potential quotes (200-250 chars): {len(potential_quotes)}")

if __name__ == "__main__":
    main() 