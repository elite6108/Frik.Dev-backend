from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from apis.ai.promots import reactBasePrompt, nodeBasePrompt, BASE_PROMPT
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("ANT_CLAUDE")

router = APIRouter()

@router.post("/template")
async def template(request: Request):
    data = await request.json()
    prompt = data.get("prompt")
    print(prompt)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-7-sonnet-20250219",
                    "max_tokens": 200,
                    "messages": [{"role": "user", "content": prompt}],
                    "system": "Return either node or react based on what do you think this project should be. Only return a single word either 'node' or 'react'. Do not return anything extra"
                }
            )
            
            response_data = response.json()
            answer = response_data["content"][0]["text"].strip().lower()
        
        if answer == "react":
            return JSONResponse(content={
                "prompts": [
                    BASE_PROMPT,
                    (
                        "Here is an artifact that contains all files of the project visible to you.\n"
                        "Consider the contents of ALL files in the project.\n\n"
                        f"{reactBasePrompt}\n\n"
                        "Here is a list of files that exist on the file system but are not being shown to you:\n\n"
                        "  - .gitignore\n"
                        "  - package-lock.json\n"
                    )
                ],
                "uiPrompts": [reactBasePrompt]
            })
        
        elif answer == "node":
            return JSONResponse(content={
                "prompts": [
                    (
                        "Here is an artifact that contains all files of the project visible to you.\n"
                        "Consider the contents of ALL files in the project.\n\n"
                        f"{nodeBasePrompt}\n\n"
                        "Here is a list of files that exist on the file system but are not being shown to you:\n\n"
                        "  - .gitignore\n"
                        "  - package-lock.json\n"
                    )
                ],
                "uiPrompts": [nodeBasePrompt]
            })
        
        else:
            raise HTTPException(status_code=403, detail="You can't access this")
    
    except Exception as e:
        print(f"Error in template endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")





