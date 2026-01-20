"""
Vision model query for image understanding using Qwen2.5-VL.
"""
import base64
from typing import Optional
import httpx
from app.core.config import settings


def query_image_with_vision(image_base64: str, question: str, image_format: str = "jpeg") -> str:
    """
    Query an image using Qwen2.5-VL 7B Instruct vision model.
    
    Args:
        image_base64: Base64 encoded image
        question: User's question about the image
        image_format: Image format (jpeg, png, etc.)
        
    Returns:
        Model's response about the image
    """
    try:
        # Construct data URL
        data_url = f"data:image/{image_format};base64,{image_base64}"
        
        print(f"[Vision] Querying image with question: {question[:100]}...")
        
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen-2.5-vl-7b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": question
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url
                                }
                            }
                        ]
                    }
                ]
            },
            timeout=60.0
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print(f"[Vision] Got response: {answer[:100]}...")
            return answer
        else:
            error_msg = f"Vision API error: {response.status_code} - {response.text}"
            print(f"[Vision] {error_msg}")
            return f"Error analyzing image: {error_msg}"
            
    except Exception as e:
        print(f"[Vision] Error querying image: {e}")
        import traceback
        traceback.print_exc()
        return f"Error analyzing image: {str(e)}"


def encode_image_to_base64(image_bytes: bytes) -> str:
    """
    Encode image bytes to base64 string.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Base64 encoded string
    """
    return base64.b64encode(image_bytes).decode('utf-8')
