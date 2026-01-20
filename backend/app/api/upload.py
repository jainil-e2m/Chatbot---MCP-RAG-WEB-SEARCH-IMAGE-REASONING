"""
Document upload API with RAG processing and image support.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.core.rag import process_document, create_vector_store
from app.tools.vision_query import encode_image_to_base64
from app.storage.chat_history import chat_history_store

router = APIRouter(tags=["upload"])

# Supported image formats
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: str = Form(...)
):
    """
    Upload a document (PDF/TXT) or image for RAG/vision processing.
    
    Args:
        file: PDF, TXT, or image file
        conversation_id: Conversation to associate with
        
    Returns:
        Upload status
    """
    try:
        # Read file content
        content = await file.read()
        filename_lower = file.filename.lower()
        
        # Check if it's an image
        file_ext = None
        for ext in IMAGE_EXTENSIONS:
            if filename_lower.endswith(ext):
                file_ext = ext
                break
        
        if file_ext:
            # Handle image upload
            print(f"[Upload] Processing image {file.filename} ({len(content)} bytes)")
            
            # Convert to base64
            image_base64 = encode_image_to_base64(content)
            image_format = file_ext[1:]  # Remove the dot
            
            # Store in memory
            chat_history_store.add_image(
                conversation_id=conversation_id,
                image_base64=image_base64,
                filename=file.filename,
                image_format=image_format
            )
            
            return JSONResponse({
                "status": "success",
                "message": f"Image '{file.filename}' uploaded successfully",
                "filename": file.filename,
                "type": "image",
                "conversation_id": conversation_id,
                "image_data": f"data:image/{image_format};base64,{image_base64}"
            })
        
        # Handle text document upload
        if not (filename_lower.endswith('.pdf') or filename_lower.endswith('.txt')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF, TXT, and image files (jpg, png, gif, etc.) are supported"
            )
        
        # Extract text
        print(f"[Upload] Processing {file.filename} ({len(content)} bytes)")
        text = process_document(content, file.filename)
        
        if not text or len(text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from document"
            )
        
        print(f"[Upload] Extracted {len(text)} characters")
        
        # Create vector store
        success = create_vector_store(conversation_id, text)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to create vector store"
            )
        
        return JSONResponse({
            "status": "success",
            "message": f"Document '{file.filename}' processed successfully",
            "filename": file.filename,
            "type": "document",
            "text_length": len(text),
            "conversation_id": conversation_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Upload] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
