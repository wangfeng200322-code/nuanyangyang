from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(encoding='utf-8-sig')

app = FastAPI()

# Mount the 'static' directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatMessage(BaseModel):
    message: str

# This is a placeholder for the actual DeepSeek API call
def get_deepseek_response(user_message: str):
    # IMPORTANT: Replace with your actual DeepSeek API call
    # You will need to get your API key from DeepSeek
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return "Error: DEEPSEEK_API_KEY not found. Please set it in a .env file."

    # Example of calling the DeepSeek API (this is a generic example, you might need to adjust it)
    # Please refer to the official DeepSeek API documentation for the correct endpoint and payload structure
    api_url = "https://api.deepseek.com/v1/chat/completions" # Replace with the correct API endpoint
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "deepseek-chat", # Or whatever model you are using
        "messages": [
            {"role": "system", "content": "你是一个懂心理学，懂得老年人的聊天机器人。"
            "你的名字叫暖洋洋，一个让人感觉温暖的名字.你了解这里的没一个老人，每天听他们唠家常，帮他们排解孤独和烦恼。"
            "请认真倾听他们的聊天，理解他们的情绪，和他们共情，但是请不要给他们提供医疗建议。"
            "请在聊天中以温暖、关怀的语气回应他们。请以晚辈的身份和他们聊天。"},
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return "Sorry, I couldn't connect to the AI service."
    except (KeyError, IndexError) as e:
        print(f"Failed to parse API response: {e}")
        return "Sorry, I received an unexpected response from the AI service."


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/api/chat")
async def chat(message: ChatMessage):
    # In a real application, you would call the DeepSeek API here
    # For now, we'll just echo the message back
    # reply = f"You said: {message.message}"
    reply = get_deepseek_response(message.message)
    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
