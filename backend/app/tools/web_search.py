"""
Web search tool using Tavily API.
"""
from typing import List, Dict, Optional
from tavily import TavilyClient
from app.core.config import settings


def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web using Tavily API.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of search results with title, url, and content
        
    Raises:
        Exception: If Tavily API key is not configured or search fails
    """
    if not settings.tavily_api_key:
        raise ValueError("Tavily API key not configured")
    
    try:
        # Initialize Tavily client
        client = TavilyClient(api_key=settings.tavily_api_key)
        
        # Perform search
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",  # or "advanced" for more comprehensive results
            include_answer=False,  # We'll let the LLM generate the answer
            include_raw_content=False,  # Don't need full page content
            include_images=False  # Don't need images for now
        )
        
        # Extract and format results
        results = []
        for result in response.get('results', []):
            results.append({
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'content': result.get('content', ''),  # Snippet/summary
                'score': result.get('score', 0.0)  # Relevance score
            })
        
        return results
        
    except Exception as e:
        raise Exception(f"Web search failed: {str(e)}")


def format_search_results_for_llm(results: List[Dict[str, str]]) -> str:
    """
    Format search results into a string for LLM context.
    
    Args:
        results: List of search results
        
    Returns:
        Formatted string with search results
    """
    if not results:
        return "No search results found."
    
    formatted = "Here are the most relevant web search results:\n\n"
    
    for i, result in enumerate(results, 1):
        formatted += f"{i}. {result['title']}\n"
        formatted += f"   URL: {result['url']}\n"
        formatted += f"   {result['content']}\n\n"
    
    return formatted
