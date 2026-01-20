"""
Database connection and Supabase client initialization.
"""
import httpx
from typing import Any, Dict, List, Optional
from app.core.config import settings


class SupabaseClient:
    """Lightweight Supabase client using httpx."""
    
    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def table(self, table_name: str):
        """Get table interface."""
        return SupabaseTable(self, table_name)


class SupabaseTable:
    """Table interface for Supabase."""
    
    def __init__(self, client: SupabaseClient, table_name: str):
        self.client = client
        self.table_name = table_name
        self.url = f"{client.url}/rest/v1/{table_name}"
        self._select_fields = "*"
        self._filters = []
    
    def select(self, fields: str = "*"):
        """Select fields."""
        self._select_fields = fields
        return self
    
    def eq(self, column: str, value: Any):
        """Add equality filter."""
        self._filters.append(f"{column}=eq.{value}")
        return self
    
    def execute(self):
        """Execute the query."""
        url = self.url
        if self._select_fields:
            url += f"?select={self._select_fields}"
        if self._filters:
            separator = "&" if "?" in url else "?"
            url += separator + "&".join(self._filters)
        
        response = httpx.get(url, headers=self.client.headers, timeout=10.0)
        response.raise_for_status()
        
        return SupabaseResponse(response.json())
    
    def insert(self, data: Dict[str, Any]):
        """Insert data."""
        response = httpx.post(
            self.url,
            json=data,
            headers=self.client.headers,
            timeout=10.0
        )
        response.raise_for_status()
        
        return SupabaseResponse(response.json())

    def delete(self):
        """Delete records matching filters."""
        url = self.url
        if self._filters:
            separator = "&" if "?" in url else "?"
            url += separator + "&".join(self._filters)
        
        response = httpx.delete(url, headers=self.client.headers, timeout=10.0)
        response.raise_for_status()
        
        # DELETE usually returns 204 No Content, but Supabase might return data if Prefer: return=representation
        if response.status_code == 204:
            return SupabaseResponse([])
        return SupabaseResponse(response.json())


class SupabaseResponse:
    """Response wrapper."""
    
    def __init__(self, data: Any):
        self.data = data if isinstance(data, list) else [data] if data else []


# Global client instance
supabase = SupabaseClient(settings.supabase_url, settings.supabase_key)
