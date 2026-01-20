"""
Google Calendar Tools - Direct implementation without MCP SDK.
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict, Any

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Get authenticated Calendar service."""
    import json
    
    creds = None
    token_path = os.path.expanduser('~/.config/google-calendar-mcp/tokens.json')
    creds_path = os.path.expanduser('~/.calendar-mcp/gcp-oauth.keys.json')
    
    # Try to load existing token
    if os.path.exists(token_path) and os.path.exists(creds_path):
        try:
            # Load the MCP token format
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            
            # Load client credentials
            with open(creds_path, 'r') as f:
                client_data = json.load(f)
                client_info = client_data.get('installed') or client_data.get('web', {})
            
            # Extract token from MCP format (wrapped in "normal" key)
            if 'normal' in token_data:
                token_info = token_data['normal']
            else:
                token_info = token_data
            
            # Create credentials with merged data
            creds_dict = {
                'token': token_info.get('access_token'),
                'refresh_token': token_info.get('refresh_token'),
                'token_uri': client_info.get('token_uri', 'https://oauth2.googleapis.com/token'),
                'client_id': client_info.get('client_id'),
                'client_secret': client_info.get('client_secret'),
                'scopes': SCOPES
            }
            
            creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)
        except Exception as e:
            print(f"Error loading credentials: {e}")
            creds = None
    
    # Refresh if needed
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            creds = None
    
    # If still no valid creds, run OAuth flow
    if not creds or not creds.valid:
        if os.path.exists(creds_path):
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save token
            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)


def parse_time_string(time_str: str) -> str:
    """
    Parse natural language time strings to ISO format.
    
    Args:
        time_str: Time string (can be ISO format or natural language like 'this month', 'today', etc.)
        
    Returns:
        ISO formatted datetime string with 'Z' suffix
    """
    if not time_str:
        return None
    
    # If already in ISO format (contains 'T' or ends with 'Z'), return as-is
    if 'T' in time_str or time_str.endswith('Z'):
        return time_str
    
    now = datetime.utcnow()
    
    # Handle common natural language phrases
    time_str_lower = time_str.lower().strip()
    
    if time_str_lower in ['now', 'today']:
        return now.isoformat() + 'Z'
    
    if time_str_lower in ['this month', 'month']:
        # Start of current month
        return datetime(now.year, now.month, 1).isoformat() + 'Z'
    
    if time_str_lower in ['next month']:
        # Start of next month
        if now.month == 12:
            return datetime(now.year + 1, 1, 1).isoformat() + 'Z'
        else:
            return datetime(now.year, now.month + 1, 1).isoformat() + 'Z'
    
    if time_str_lower in ['this week', 'week']:
        # Start of current week (Monday)
        days_since_monday = now.weekday()
        start_of_week = now - timedelta(days=days_since_monday)
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    
    if time_str_lower in ['tomorrow']:
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    
    # If we can't parse it, return the original and let Google Calendar API handle it
    return time_str


def list_events(maxResults: int = 10, timeMin: str = None, timeMax: str = None) -> Dict[str, Any]:
    """
    List upcoming calendar events.
    
    Args:
        maxResults: Maximum number of events
        timeMin: Start time (ISO format), defaults to now
        timeMax: End time (ISO format), optional
    """
    try:
        print(f"[Calendar] Listing events with maxResults={maxResults}, timeMin={timeMin}, timeMax={timeMax}")
        
        try:
            service = get_calendar_service()
        except Exception as e:
            print(f"[Calendar] Failed to get calendar service: {str(e)}")
            return {
                'success': False,
                'error': f'Calendar authentication failed: {str(e)}. Please ensure your Google Calendar is properly configured.'
            }
        
        
        # Parse natural language time strings to ISO format
        if timeMin:
            timeMin = parse_time_string(timeMin)
            print(f"[Calendar] Parsed timeMin to: {timeMin}")
        
        if not timeMin:
            timeMin = datetime.utcnow().isoformat() + 'Z'
        
        if timeMax:
            timeMax = parse_time_string(timeMax)
            print(f"[Calendar] Parsed timeMax to: {timeMax}")
        
        params = {
            'calendarId': 'primary',
            'timeMin': timeMin,
            'maxResults': maxResults,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        if timeMax:
            params['timeMax'] = timeMax

        
        print(f"[Calendar] Calling Google Calendar API with params: {params}")
        
        try:
            events_result = service.events().list(**params).execute()
        except Exception as e:
            print(f"[Calendar] Google Calendar API error: {str(e)}")
            return {
                'success': False,
                'error': f'Google Calendar API error: {str(e)}'
            }
        
        events = events_result.get('items', [])
        
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_events.append({
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'start': start,
                'end': end,
                'location': event.get('location', ''),
                'description': event.get('description', '')
            })
        
        print(f"[Calendar] Successfully retrieved {len(formatted_events)} events")
        return {
            'success': True,
            'events': formatted_events,
            'count': len(formatted_events)
        }
    except Exception as e:
        print(f"[Calendar] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def get_event(eventId: str) -> Dict[str, Any]:
    """
    Get details of a specific event.
    
    Args:
        eventId: Calendar event ID
    """
    try:
        service = get_calendar_service()
        event = service.events().get(
            calendarId='primary',
            eventId=eventId
        ).execute()
        
        return {
            'success': True,
            'event': {
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'attendees': event.get('attendees', [])
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_event(summary: str, start: str, end: str, description: str = None, 
                location: str = None, attendees: List[str] = None) -> Dict[str, Any]:
    """
    Create a new calendar event.
    
    Args:
        summary: Event title
        start: Start time (ISO format: 2026-01-21T10:00:00)
        end: End time (ISO format: 2026-01-21T11:00:00)
        description: Event description (optional)
        location: Event location (optional)
        attendees: List of attendee emails (optional)
    """
    try:
        service = get_calendar_service()
        
        # Build event object
        event = {
            'summary': summary,
            'start': {
                'dateTime': start,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'UTC',
            }
        }
        
        if description:
            event['description'] = description
        
        if location:
            event['location'] = location
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        # Create event
        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return {
            'success': True,
            'event_id': created_event['id'],
            'html_link': created_event.get('htmlLink', ''),
            'message': f'Event "{summary}" created successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def update_event(event_id: str, summary: str = None, start: str = None, 
                end: str = None, description: str = None, location: str = None) -> Dict[str, Any]:
    """
    Update an existing calendar event.
    
    Args:
        event_id: Event ID to update
        summary: New event title (optional)
        start: New start time (optional, ISO format)
        end: New end time (optional, ISO format)
        description: New description (optional)
        location: New location (optional)
    """
    try:
        service = get_calendar_service()
        
        # Get existing event
        event = service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        # Update fields if provided
        if summary:
            event['summary'] = summary
        
        if start:
            event['start'] = {
                'dateTime': start,
                'timeZone': 'UTC',
            }
        
        if end:
            event['end'] = {
                'dateTime': end,
                'timeZone': 'UTC',
            }
        
        if description is not None:
            event['description'] = description
        
        if location is not None:
            event['location'] = location
        
        # Update event
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        return {
            'success': True,
            'event_id': updated_event['id'],
            'html_link': updated_event.get('htmlLink', ''),
            'message': 'Event updated successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def delete_event(event_id: str) -> Dict[str, Any]:
    """
    Delete a calendar event.
    
    Args:
        event_id: Event ID to delete
    """
    try:
        service = get_calendar_service()
        
        service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        return {
            'success': True,
            'message': f'Event {event_id} deleted successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Tool registry
CALENDAR_TOOLS = {
    'list_events': {
        'function': list_events,
        'description': 'List upcoming calendar events',
        'parameters': {
            'maxResults': {'type': 'integer', 'description': 'Maximum results', 'default': 10},
            'timeMin': {'type': 'string', 'description': 'Start time (ISO format)'},
            'timeMax': {'type': 'string', 'description': 'End time (ISO format)'}
        }
    },
    'get_event': {
        'function': get_event,
        'description': 'Get details of a specific event',
        'parameters': {
            'eventId': {'type': 'string', 'description': 'Event ID', 'required': True}
        }
    },
    'create_event': {
        'function': create_event,
        'description': 'Create a new calendar event',
        'parameters': {
            'summary': {'type': 'string', 'description': 'Event title', 'required': True},
            'start': {'type': 'string', 'description': 'Start time (ISO format)', 'required': True},
            'end': {'type': 'string', 'description': 'End time (ISO format)', 'required': True},
            'description': {'type': 'string', 'description': 'Event description'},
            'location': {'type': 'string', 'description': 'Event location'},
            'attendees': {'type': 'array', 'description': 'List of attendee emails'}
        }
    },
    'update_event': {
        'function': update_event,
        'description': 'Update an existing calendar event',
        'parameters': {
            'event_id': {'type': 'string', 'description': 'Event ID to update', 'required': True},
            'summary': {'type': 'string', 'description': 'New event title'},
            'start': {'type': 'string', 'description': 'New start time (ISO format)'},
            'end': {'type': 'string', 'description': 'New end time (ISO format)'},
            'description': {'type': 'string', 'description': 'New description'},
            'location': {'type': 'string', 'description': 'New location'}
        }
    },
    'delete_event': {
        'function': delete_event,
        'description': 'Delete a calendar event',
        'parameters': {
            'event_id': {'type': 'string', 'description': 'Event ID to delete', 'required': True}
        }
    }
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute a Calendar tool."""
    if tool_name not in CALENDAR_TOOLS:
        return {'success': False, 'error': f'Tool {tool_name} not found'}
    
    tool = CALENDAR_TOOLS[tool_name]
    return tool['function'](**arguments)


def list_tools() -> List[Dict[str, Any]]:
    """List available Calendar tools."""
    return [
        {
            'name': name,
            'description': info['description'],
            'parameters': info['parameters']
        }
        for name, info in CALENDAR_TOOLS.items()
    ]
