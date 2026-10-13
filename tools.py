from langchain.tools import tool
from dotenv import load_dotenv
import os
import requests
from tavily import TavilyClient
from bs4 import BeautifulSoup
import trafilatura
import re
from lxml import html as lxml_html

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str):
    """Searches the web using Tavily and returns up to five results with their titles, URLs, and content snippets formatted as a readable string."""
    results = tavily.search(query=query, max_results=5)
    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Snippet: {r['content'][:300]}\n"
        )

    return '\n----\n'.join(out)

@tool
def scrape_url(url: str) -> str:
    """Scrapes a webpage, extracts and cleans its text content using multiple fallback methods, and handles request and parsing errors."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text

        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r'\s+',' ', extracted)
            return cleaned[:500]

        doc = lxml_html.fromstring(html)
        clean_html = lxml_html.tostring(doc, encoding="unicode")

        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup(["script","style","nav","footer","header","aside","form"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', text)
            return cleaned[:500]

        soup = BeautifulSoup(html, "html.parser")
        
        for tag in soup(["script","style","nav","footer","header","aside","form"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            return cleaned[:5000]

        return "COuld not extract meaningful content."

    except requests.exceptions.Timeout:
        return "Request timed out"

    except requests.exceptions.HTTPError as e:
        return f"HTTP error : {str(e)}"

    except Exception as e:
        return f"Error : {str(e)}"


                             
        
