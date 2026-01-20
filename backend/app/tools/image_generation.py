"""
Image Generation Tool - Uses OpenRouter Gemini 2.5 Flash Image.
"""
import os
import json
import requests
import re
from typing import Dict, Any
from app.core.config import settings


def generate_image(prompt: str) -> Dict[str, Any]:
    """
    Generate image using OpenRouter Gemini 2.5 Flash Image.
    
    Args:
        prompt: Description of image to generate
        
    Returns:
        Dict with success status and image_url or error
    """
    try:
        api_key = settings.openrouter_api_key
        if not api_key:
            return {
                'success': False,
                'error': 'OPENROUTER_API_KEY not configured'
            }
        
        print(f"[ImageGen] Generating image for: {prompt[:50]}...")
        
        # Prepare request payload
        payload = {
            "model": "google/gemini-2.5-flash-image",
            "messages": [{
                "role": "user",
                "content": f"Generate an image of: {prompt}"
            }],
            "modalities": ["image", "text"]
        }
        
        # Debug: Log payload size
        payload_str = json.dumps(payload)
        payload_size = len(payload_str)
        estimated_tokens = payload_size // 4
        print(f"[ImageGen] Payload size: {payload_size} chars (~{estimated_tokens} tokens)")
        if estimated_tokens > 10000:
            print(f"[ImageGen] WARNING: Payload is very large!")
            print(f"[ImageGen] Prompt length: {len(prompt)} chars")
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-chat-studio.com",
                "X-Title": "AI Chat Studio"
            },
            timeout=60
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract image URL from response
        choice = data.get('choices', [{}])[0]
        message = choice.get('message', {})
        
        # Check for explicit images array
        if 'images' in message and len(message['images']) > 0:
            image_data = message['images'][0]
            image_url = image_data.get('image_url', {}).get('url') or image_data.get('url')
            if image_url:
                print(f"[ImageGen] Success! Image URL found in images array")
                return {
                    'success': True,
                    'image_url': image_url
                }
        
        # Fallback: Check content for markdown or URL
        content = message.get('content', '')
        if content:
            # Try markdown format: ![alt](url)
            markdown_match = re.search(r'!\[.*?\]\((.*?)\)', content)
            if markdown_match:
                image_url = markdown_match.group(1)
                print(f"[ImageGen] Success! Image URL found in markdown")
                return {
                    'success': True,
                    'image_url': image_url
                }
            
            # Try direct URL
            url_match = re.search(r'https?://[^\s)]+', content)
            if url_match:
                image_url = url_match.group(0)
                print(f"[ImageGen] Success! Image URL found as direct link")
                return {
                    'success': True,
                    'image_url': image_url
                }
            
            # Check for base64
            if content.startswith('data:image'):
                print(f"[ImageGen] Success! Base64 image found")
                return {
                    'success': True,
                    'image_url': content
                }
        
        print(f"[ImageGen] Warning: No image URL found in response")
        return {
            'success': False,
            'error': 'No image found in response',
            'raw_response': str(data)[:200]
        }
        
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Image generation timed out (60s)'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'API request failed: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }
