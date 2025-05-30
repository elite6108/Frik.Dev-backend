from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import httpx
from dotenv import load_dotenv
from apis.ai.prompts import get_system_prompt

load_dotenv()
api_key = os.environ.get("ANT_CLAUDE")

if not api_key:
    print("WARNING: ANT_CLAUDE environment variable is not set!")

router = APIRouter()


@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    try:
        # Validate and sanitize messages
        if not isinstance(messages, list):
            raise ValueError("Messages must be an array")

        # Filter out invalid messages and ensure content is a string
        messages = [
            msg for msg in messages
            if msg and "role" in msg and isinstance(msg.get("content"), str) and msg["content"].strip() != ""
        ]

        if len(messages) == 0:
            raise ValueError("No valid messages provided")
        
    
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-7-sonnet-20250219",
                        "max_tokens": 10000,
                        "messages": messages,
                        "system": get_system_prompt()
                    },
                    timeout=60.0  
                )
                
                response.raise_for_status()  
                response_data = response.json()                
                result_text = response_data.get("content", [{}])[0].get("text", "")
                
                return JSONResponse(content={"response": result_text})
                
            except httpx.HTTPError as http_err:
                # Handle HTTP-specific errors
                error_detail = f"HTTP error: {str(http_err)}"
                if hasattr(http_err, 'response') and http_err.response:
                    error_detail += f", Status: {http_err.response.status_code}"
                    try:
                        error_detail += f", Response: {http_err.response.text}"
                    except:
                        pass
                print(error_detail)
                raise HTTPException(status_code=500, detail=error_detail)

    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle any other errors
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
