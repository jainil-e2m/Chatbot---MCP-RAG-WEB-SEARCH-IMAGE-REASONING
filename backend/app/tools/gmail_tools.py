"""
Gmail Tools - Direct implementation without MCP SDK.
Uses Gmail API directly via google-auth and google-api-python-client.
"""
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List, Dict, Any

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """Get authenticated Gmail service."""
    creds = None
    token_path = os.path.expanduser('~/.calendar-mcp/gmail_token.json')
    creds_path = os.path.expanduser('~/.calendar-mcp/gcp-oauth.keys.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def search_emails(query: str = "", maxResults: int = 10) -> Dict[str, Any]:
    """
    Search for emails using Gmail search syntax.
    
    Args:
        query: Gmail search query (e.g., "from:me", "is:unread")
        maxResults: Maximum number of results
    """
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=maxResults
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            # Get full message details
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            # Get snippet
            snippet = message.get('snippet', '')
            
            emails.append({
                'id': msg['id'],
                'subject': subject,
                'from': from_email,
                'date': date,
                'snippet': snippet
            })
        
        return {
            'success': True,
            'emails': emails,
            'count': len(emails)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def read_email(messageId: str) -> Dict[str, Any]:
    """
    Read a specific email by ID.
    
    Args:
        messageId: Gmail message ID
    """
    try:
        service = get_gmail_service()
        message = service.users().messages().get(
            userId='me',
            id=messageId,
            format='full'
        ).execute()
        
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        to_email = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        
        # Get body
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        else:
            if 'body' in message['payload'] and 'data' in message['payload']['body']:
                import base64
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        return {
            'success': True,
            'email': {
                'id': messageId,
                'subject': subject,
                'from': from_email,
                'to': to_email,
                'date': date,
                'body': body,
                'snippet': message.get('snippet', '')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_email(to: str, subject: str, body: str, cc: str = None, bcc: str = None) -> Dict[str, Any]:
    """
    Send an email via Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        cc: CC recipients (comma-separated)
        bcc: BCC recipients (comma-separated)
    """
    try:
        import base64
        from email.mime.text import MIMEText
        
        service = get_gmail_service()
        
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return {
            'success': True,
            'message_id': sent_message['id'],
            'thread_id': sent_message.get('threadId', ''),
            'message': f'Email sent successfully to {to}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def filter_emails(query: str, label: str = None, maxResults: int = 10) -> Dict[str, Any]:
    """
    Filter emails with advanced criteria.
    
    Args:
        query: Gmail search query (e.g., "from:example@gmail.com is:unread")
        label: Optional label to filter by
        maxResults: Maximum number of results
    """
    try:
        # Build query with label if provided
        full_query = query
        if label:
            full_query = f"{query} label:{label}" if query else f"label:{label}"
        
        # Use search_emails with the enhanced query
        return search_emails(full_query, maxResults)
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Tool registry
GMAIL_TOOLS = {
    'search_emails': {
        'function': search_emails,
        'description': 'Search for emails using Gmail search syntax',
        'parameters': {
            'query': {'type': 'string', 'description': 'Gmail search query'},
            'maxResults': {'type': 'integer', 'description': 'Maximum results', 'default': 10}
        }
    },
    'read_email': {
        'function': read_email,
        'description': 'Read a specific email by ID',
        'parameters': {
            'messageId': {'type': 'string', 'description': 'Gmail message ID', 'required': True}
        }
    },
    'send_email': {
        'function': send_email,
        'description': 'Send an email via Gmail',
        'parameters': {
            'to': {'type': 'string', 'description': 'Recipient email address', 'required': True},
            'subject': {'type': 'string', 'description': 'Email subject', 'required': True},
            'body': {'type': 'string', 'description': 'Email body (plain text)', 'required': True},
            'cc': {'type': 'string', 'description': 'CC recipients (comma-separated)'},
            'bcc': {'type': 'string', 'description': 'BCC recipients (comma-separated)'}
        }
    },
    'filter_emails': {
        'function': filter_emails,
        'description': 'Filter emails with advanced criteria',
        'parameters': {
            'query': {'type': 'string', 'description': 'Gmail search query', 'required': True},
            'label': {'type': 'string', 'description': 'Optional label to filter by'},
            'maxResults': {'type': 'integer', 'description': 'Maximum results', 'default': 10}
        }
    }
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute a Gmail tool."""
    if tool_name not in GMAIL_TOOLS:
        return {'success': False, 'error': f'Tool {tool_name} not found'}
    
    tool = GMAIL_TOOLS[tool_name]
    return tool['function'](**arguments)


def list_tools() -> List[Dict[str, Any]]:
    """List available Gmail tools."""
    return [
        {
            'name': name,
            'description': info['description'],
            'parameters': info['parameters']
        }
        for name, info in GMAIL_TOOLS.items()
    ]
