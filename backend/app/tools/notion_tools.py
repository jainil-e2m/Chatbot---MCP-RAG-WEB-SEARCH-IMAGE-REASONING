"""
Notion Tools - Direct implementation without MCP SDK.
"""
import os
import requests
from typing import List, Dict, Any

NOTION_API_KEY = "ntn_E28358481032oUBwpIK8fyW85Mqxso2bEv0cVHeGKCQbLb"
NOTION_VERSION = "2022-06-28"

def get_headers():
    """Get Notion API headers."""
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }


def search_pages(query: str = "", page_size: int = 10) -> Dict[str, Any]:
    """
    Search Notion pages.
    
    Args:
        query: Search query
        page_size: Number of results
    """
    try:
        url = "https://api.notion.com/v1/search"
        payload = {
            "query": query,
            "page_size": page_size,
            "filter": {"property": "object", "value": "page"}
        }
        
        response = requests.post(url, headers=get_headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        
        pages = []
        for result in data.get('results', []):
            title = ""
            if 'properties' in result and 'title' in result['properties']:
                title_prop = result['properties']['title']
                if 'title' in title_prop and len(title_prop['title']) > 0:
                    title = title_prop['title'][0].get('plain_text', '')
            
            pages.append({
                'id': result['id'],
                'title': title or 'Untitled',
                'url': result.get('url', ''),
                'created_time': result.get('created_time', ''),
                'last_edited_time': result.get('last_edited_time', '')
            })
        
        return {
            'success': True,
            'pages': pages,
            'count': len(pages)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_page(page_id: str) -> Dict[str, Any]:
    """
    Get a Notion page by ID.
    
    Args:
        page_id: Notion page ID
    """
    try:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        page = response.json()
        
        return {
            'success': True,
            'page': {
                'id': page['id'],
                'url': page.get('url', ''),
                'created_time': page.get('created_time', ''),
                'last_edited_time': page.get('last_edited_time', ''),
                'properties': page.get('properties', {})
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_page(parent_id: str = None, title: str = None, content: str = None, page_name: str = None) -> Dict[str, Any]:
    """
    Create a new Notion page.
    
    Args:
        parent_id: Parent page or database ID (optional, will search for a suitable parent if not provided)
        title: Page title (or use page_name)
        page_name: Alias for title
        content: Optional page content (plain text)
    """
    # Handle both 'title' and 'page_name' parameters
    page_title = title or page_name
    if not page_title:
        return {
            'success': False,
            'error': 'Either title or page_name must be provided'
        }
    
    try:
        # If no parent_id provided, search for a suitable parent page
        if not parent_id:
            print("[Notion] No parent_id provided, searching for a suitable parent page...")
            search_result = search_pages(query="", page_size=1)
            if search_result.get('success') and search_result.get('pages'):
                parent_id = search_result['pages'][0]['id']
                print(f"[Notion] Using parent page: {search_result['pages'][0]['title']} ({parent_id})")
            else:
                return {
                    'success': False,
                    'error': 'No parent_id provided and could not find a suitable parent page. Please provide a parent_id or ensure you have at least one page in your Notion workspace.'
                }
        
        url = "https://api.notion.com/v1/pages"
        
        # Build page properties
        properties = {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": page_title
                        }
                    }
                ]
            }
        }
        
        # Build page payload
        payload = {
            "parent": {"page_id": parent_id},
            "properties": properties
        }
        
        # Add content if provided
        if content:
            payload["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            ]
        
        response = requests.post(url, headers=get_headers(), json=payload)
        response.raise_for_status()
        page = response.json()
        
        return {
            'success': True,
            'page_id': page['id'],
            'url': page.get('url', ''),
            'message': f'Page "{page_title}" created successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def update_page(page_id: str, title: str = None, archived: bool = None) -> Dict[str, Any]:
    """
    Update an existing Notion page.
    
    Args:
        page_id: Page ID to update
        title: New title (optional)
        archived: Archive status (optional)
    """
    try:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        
        payload = {}
        
        # Update title if provided
        if title:
            payload["properties"] = {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        
        # Update archived status if provided
        if archived is not None:
            payload["archived"] = archived
        
        if not payload:
            return {
                'success': False,
                'error': 'No updates provided'
            }
        
        response = requests.patch(url, headers=get_headers(), json=payload)
        response.raise_for_status()
        page = response.json()
        
        return {
            'success': True,
            'page_id': page['id'],
            'url': page.get('url', ''),
            'message': 'Page updated successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Tool registry
NOTION_TOOLS = {
    'search_pages': {
        'function': search_pages,
        'description': 'Search Notion pages',
        'parameters': {
            'query': {'type': 'string', 'description': 'Search query'},
            'page_size': {'type': 'integer', 'description': 'Number of results', 'default': 10}
        }
    },
    'get_page': {
        'function': get_page,
        'description': 'Get a Notion page by ID',
        'parameters': {
            'page_id': {'type': 'string', 'description': 'Page ID', 'required': True}
        }
    },
    'create_page': {
        'function': create_page,
        'description': 'Create a new Notion page',
        'parameters': {
            'parent_id': {'type': 'string', 'description': 'Parent page or database ID (optional, will auto-select if not provided)'},
            'title': {'type': 'string', 'description': 'Page title', 'required': True},
            'page_name': {'type': 'string', 'description': 'Alias for title'},
            'content': {'type': 'string', 'description': 'Optional page content (plain text)'}
        }
    },
    'update_page': {
        'function': update_page,
        'description': 'Update an existing Notion page',
        'parameters': {
            'page_id': {'type': 'string', 'description': 'Page ID to update', 'required': True},
            'title': {'type': 'string', 'description': 'New title (optional)'},
            'archived': {'type': 'boolean', 'description': 'Archive status (optional)'}
        }
    }
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute a Notion tool."""
    if tool_name not in NOTION_TOOLS:
        return {'success': False, 'error': f'Tool {tool_name} not found'}
    
    tool = NOTION_TOOLS[tool_name]
    return tool['function'](**arguments)


def list_tools() -> List[Dict[str, Any]]:
    """List available Notion tools."""
    return [
        {
            'name': name,
            'description': info['description'],
            'parameters': info['parameters']
        }
        for name, info in NOTION_TOOLS.items()
    ]
