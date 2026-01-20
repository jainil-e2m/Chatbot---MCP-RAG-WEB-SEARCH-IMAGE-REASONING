import streamlit as st
import requests
import uuid
import base64

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="Aether AI", page_icon="⚡", layout="wide")

# Session State
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# Sidebar
with st.sidebar:
    st.title("⚡ Aether AI")
    st.markdown("---")
    
    # Model Selection
    model = st.selectbox(
        "Model", 
        ["qwen/qwen-2.5-vl-7b-instruct", "google/gemini-2.0-flash-exp:free"],
        index=0
    )
    
    # File Upload
    st.subheader("Attachments")
    uploaded_file = st.file_uploader(
        "Upload Image or Document", 
        type=["png", "jpg", "jpeg", "gif", "pdf", "txt"],
        key="file_uploader"
    )
    
    if uploaded_file:
        # Check if already uploaded
        if uploaded_file.name not in st.session_state.uploaded_files:
            with st.spinner(f"Uploading {uploaded_file.name}..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    data = {"conversation_id": st.session_state.conversation_id}
                    response = requests.post(f"{API_BASE_URL}/api/upload", files=files, data=data)
                    
                    if response.status_code == 200:
                        st.success("Uploaded successfully!")
                        st.session_state.uploaded_files.append(uploaded_file.name)
                        
                        # Add system note to chat
                        st.session_state.messages.append({
                            "role": "system",
                            "content": f"📎 Uploaded: {uploaded_file.name}"
                        })
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    # Settings
    st.markdown("---")
    use_rag = st.toggle("Use RAG / Documents", value=True)
    image_gen = st.toggle("Image Generation", value=False)
    web_search = st.toggle("Web Search", value=False)

# Main Chat Interface
st.title("Chat")

# Display Messages
for msg in st.session_state.messages:
    if msg["role"] == "system":
        with st.chat_message("assistant", avatar="📎"):
            st.markdown(f"*{msg['content']}*")
    else:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Display images if present in the message (custom logic)
            if "image_url" in msg and msg["image_url"]:
                st.image(msg["image_url"], caption="Generated/Attached", use_column_width=True)
            
            # Display sources if present
            if "sources" in msg and msg["sources"]:
                with st.expander(f"📚 Sources ({len(msg['sources'])})"):
                    for source in msg["sources"]:
                        if "url" in source:
                            st.markdown(f"[{source.get('title', 'Link')}]({source['url']})")
                        elif "filename" in source:
                            st.markdown(f"📄 **{source['filename']}**")

# Input
if prompt := st.chat_input("Ask anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Backend
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            payload = {
                "conversation_id": st.session_state.conversation_id,
                "message": prompt,
                "model": model,
                "use_rag": use_rag,
                "web_search": web_search,
                "image_generation": image_gen,
                "enabled_mcps": [], # Add logic if needed
                "enabled_tools": {}
            }
            
            response = requests.post(f"{API_BASE_URL}/api/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                content = data["message"]
                
                # Update placeholder
                message_placeholder.markdown(content)
                
                # Store in history
                msg_entry = {
                    "role": "assistant",
                    "content": content,
                    "sources": data.get("sources", []),
                    "image_url": data.get("image_url")
                }
                st.session_state.messages.append(msg_entry)
                
                # Render extras
                if data.get("image_url"):
                    st.image(data["image_url"], caption="Generated Image")
                
                if data.get("sources"):
                    with st.expander(f"📚 Sources ({len(data['sources'])})"):
                        for source in data["sources"]:
                             if "url" in source:
                                st.markdown(f"[{source.get('title', 'Link')}]({source['url']})")
                             elif "filename" in source:
                                st.markdown(f"📄 **{source['filename']}**")
                                
            else:
                message_placeholder.error(f"Error: {response.text}")
        except Exception as e:
             message_placeholder.error(f"Connection failed: {e}")
