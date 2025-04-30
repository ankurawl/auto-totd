import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse

def is_valid_url(url):
    """Check if URL is valid and has http/https scheme"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except:
        return False

def get_text_from_url(url, max_depth=3, current_depth=0, visited=None):
    """Recursively fetch text content from URL and its links up to max_depth"""
    if visited is None:
        visited = set()
    
    if current_depth > max_depth or url in visited or not is_valid_url(url):
        return ""
    
    visited.add(url)
    
    try:
        print(f"Fetching content from: {url}")
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: Status code {response.status_code}")
            return ""
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from paragraphs
        paragraphs = soup.find_all('p')
        text_content = "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # If we're not at max depth, get links and follow them
        if current_depth < max_depth:
            links = soup.find_all('a', href=True)
            for link in links:
                full_url = urljoin(url, link['href'])
                if is_valid_url(full_url) and full_url not in visited:
                    # Add a delay to be nice to servers
                    time.sleep(1)
                    text_content += "\n\n" + get_text_from_url(
                        full_url, 
                        max_depth, 
                        current_depth + 1, 
                        visited
                    )
        
        return text_content
    
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return ""

def main():
    # Check if sources.txt exists
    if not os.path.exists('sources.txt'):
        with open('sources.txt', 'w') as f:
            f.write("https://en.wikipedia.org/wiki/Philosophy\n")
            f.write("https://en.wikipedia.org/wiki/Psychology\n")
        print("Created sample sources.txt file")
    
    # Read URLs from sources.txt
    with open('sources.txt', 'r') as f:
        urls = [url.strip() for url in f.readlines() if url.strip()]
    
    # Fetch content from each URL
    all_content = ""
    for url in urls:
        if is_valid_url(url):
            content = get_text_from_url(url, max_depth=2)
            all_content += f"\n\n--- Content from {url} ---\n\n{content}"
        else:
            print(f"Invalid URL: {url}")
    
    # Save content to raw file
    with open('raw_content.txt', 'w', encoding='utf-8') as f:
        f.write(all_content)
    
    print(f"Content saved to raw_content.txt")

if __name__ == "__main__":
    main() 