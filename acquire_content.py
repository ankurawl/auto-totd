import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re

def is_valid_url(url, base_url=None):
    """
    Check if URL is valid, has http/https scheme, and is downstream from base_url
    if base_url is provided
    """
    try:
        result = urlparse(url)
        is_valid = all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        
        # Skip image, video, and other non-HTML resources
        if any(result.path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.mp4', '.pdf']):
            return False
        
        # If base_url is provided, only check if domain matches (not path)
        if base_url and is_valid:
            base_parsed = urlparse(base_url)
            return result.netloc == base_parsed.netloc
        
        return is_valid
    except:
        return False

def get_domain(url):
    """Extract the domain from a URL"""
    parsed = urlparse(url)
    return parsed.netloc

def is_product_management_content(text):
    """Check if text contains product management related keywords"""
    pm_keywords = [
        'product management', 'product manager', 'product development', 
        'user experience', 'customer development', 'product strategy',
        'product roadmap', 'product vision', 'feature prioritization',
        'agile', 'scrum', 'sprint', 'backlog', 'mvp', 'minimum viable product',
        'user story', 'stakeholder', 'user testing', 'market research',
        'customer feedback', 'product metrics', 'kpi', 'okr'
    ]
    
    text_lower = text.lower()
    
    # Count how many PM keywords are in the text
    keyword_count = sum(1 for keyword in pm_keywords if keyword in text_lower)
    
    # If at least 2 PM keywords are found, consider it relevant
    return keyword_count >= 2

def get_article_content(soup):
    """Extract only the main article content, filtering out headers, footers, navigation, etc."""
    # Common article container tags and classes
    article_containers = [
        soup.find('article'),
        soup.find(class_=re.compile(r'post|article|entry|content|main')),
        soup.find(id=re.compile(r'post|article|entry|content|main')),
        soup.find('div', class_=re.compile(r'post-content|article-content|entry-content|post-body|article-body'))
    ]
    
    # Use the first valid container found
    content_container = next((container for container in article_containers if container), None)
    
    # If no specific container found, use the body
    if not content_container:
        content_container = soup.find('body')
    
    if content_container:
        # Remove navigation, headers, footers, sidebars, comments
        for element in content_container.find_all(['nav', 'header', 'footer', 'aside']):
            element.extract()
            
        for element in content_container.find_all(class_=re.compile(r'comment|sidebar|menu|nav|footer|header')):
            element.extract()
            
        for element in content_container.find_all(id=re.compile(r'comment|sidebar|menu|nav|footer|header')):
            element.extract()
        
        # Extract text using both paragraphs and headings for better context
        text_elements = content_container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        text_content = "\n\n".join([elem.get_text().strip() for elem in text_elements if elem.get_text().strip()])
        
        return text_content
    
    return ""

def extract_article_links(soup, current_url):
    """Extract links to potential articles within the page"""
    article_links = []
    domain = get_domain(current_url)
    
    # Look for link elements
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        # Skip anchors and javascript links
        if href.startswith('#') or href.startswith('javascript:'):
            continue
            
        full_url = urljoin(current_url, href)
        
        # Check if it's a valid URL in the same domain
        if not is_valid_url(full_url, current_url):
            continue
            
        url_path = urlparse(full_url).path.lower()
        link_text = link.get_text().strip()
        
        # Identify likely article links - either by URL structure or link text
        # Article URLs often have patterns like /yyyy/mm/dd/ or /blog/post-title or /p/post-title
        article_url_patterns = [
            r'/\d{4}/\d{2}/',  # Date-based URL structure
            r'/blog/',
            r'/article/',
            r'/post/',
            r'/p/',
            r'-vs-',           # Common in comparison articles
            r'/how-to-',
            r'/guide-',
            r'/case-study'
        ]
        
        # Avoid admin, tag, category, and other non-article pages
        avoid_keywords = ['admin', 'login', 'tag/', 'category/', 'author/', 'search/', '/comment', '/feed/', '/rss/']
        
        is_likely_article = any(re.search(pattern, url_path) for pattern in article_url_patterns)
        should_avoid = any(keyword in url_path for keyword in avoid_keywords)
        
        # Also check if link text suggests it's an article
        has_article_title = (len(link_text) > 15 and  # Long enough to be a title
                         not any(keyword in link_text.lower() for keyword in ['tag', 'category', 'archive', 'login', 'sign in']))
        
        if (is_likely_article or has_article_title) and not should_avoid:
            if full_url not in article_links:
                article_links.append(full_url)
    
    return article_links

def process_blog_index(url, max_articles=10):
    """Process a blog index page to find article links"""
    try:
        print(f"Fetching blog index: {url}")
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch blog index {url}: Status code {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article_links = extract_article_links(soup, url)
        
        print(f"Found {len(article_links)} potential article links")
        return article_links[:max_articles]  # Limit to prevent too many requests
        
    except Exception as e:
        print(f"Error processing blog index {url}: {str(e)}")
        return []

def get_text_from_article(url):
    """Extract text content from a single article URL"""
    try:
        print(f"Fetching article: {url}")
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch article {url}: Status code {response.status_code}")
            return ""
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = get_article_content(soup)
        
        # Check if the content has enough substance (at least 300 words)
        if len(text_content.split()) < 300:
            print(f"Article has insufficient content: {url}")
            return ""
            
        print(f"Successfully extracted content from: {url}")
        return text_content
        
    except Exception as e:
        print(f"Error fetching article {url}: {str(e)}")
        return ""

def main():
    # Check if sources.txt exists
    if not os.path.exists('sources.txt'):
        with open('sources.txt', 'w') as f:
            f.write("https://www.svpg.com/articles/\n")
            f.write("https://www.mindtheproduct.com/\n")
        print("Created sample sources.txt file with product management blogs")
    
    # Read URLs from sources.txt
    with open('sources.txt', 'r') as f:
        blog_urls = [url.strip() for url in f.readlines() if url.strip()]
    
    # Process each blog index to find article links
    all_content = ""
    for blog_url in blog_urls:
        if not is_valid_url(blog_url):
            print(f"Invalid URL: {blog_url}")
            continue
            
        # First, extract article links from the blog index
        article_links = process_blog_index(blog_url, max_articles=5)
        
        if not article_links:
            print(f"No article links found at: {blog_url}")
            continue
            
        # Then fetch content from each article
        blog_content = f"\n\n--- Content from {blog_url} ---\n\n"
        article_count = 0
        
        for article_url in article_links:
            # Add a delay between requests
            time.sleep(2)
            article_text = get_text_from_article(article_url)
            
            if article_text:
                blog_content += f"\n\n--- Article: {article_url} ---\n\n{article_text}\n\n"
                article_count += 1
        
        if article_count > 0:
            all_content += blog_content
            print(f"Extracted content from {article_count} articles at {blog_url}")
        else:
            print(f"Could not extract content from any articles at {blog_url}")
    
    # Save content to raw file
    if all_content:
        with open('raw_content.txt', 'w', encoding='utf-8') as f:
            f.write(all_content)
        print(f"Content saved to raw_content.txt")
    else:
        print("No content was extracted. Please check your source URLs.")

if __name__ == "__main__":
    main() 