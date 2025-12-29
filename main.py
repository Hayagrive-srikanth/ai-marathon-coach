import os
import json
import requests
from datetime import datetime  # <--- NEW: Allows AI to know "Today"
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load Secrets
load_dotenv()

app = FastAPI()

# 2. Allow Lovable to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- TOOL 1: WEATHER ---
def get_weather(city: str):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key: return "Simulated: Sunny, 25°C"
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return f"{data['weather'][0]['description']}, {data['main']['temp']}°C"
    return "Error fetching weather."

# --- TOOL 2: STRAVA (Updated) ---
def get_strava_stats():
    refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    
    if not refresh_token: return "Error: Strava keys missing."

    # A. Refresh the Token
    auth_res = requests.post("https://www.strava.com/oauth/token", data={
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'f': 'json'
    })
    if auth_res.status_code != 200: return "Error: Could not refresh Strava token."
    access_token = auth_res.json().get('access_token')

    # B. Get the Runs (UPDATED: Fetches last 30 runs to find older ones)
    res = requests.get(
        "https://www.strava.com/api/v3/athlete/activities?per_page=30", 
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if res.status_code == 200:
        summary = []
        for run in res.json():
            # Extract data safely
            dist = round(run.get('distance', 0) / 1000, 2)
            date = run.get('start_date', 'Unknown')[:10] # YYYY-MM-DD
            name = run.get('name', 'Run')
            
            line = f"- {date}: {name} ({dist}km)"
            summary.append(line)
            
        # --- DEBUG PRINT: Look at your Terminal to see this list! ---
        print("\n🔎 STRAVA DATA FOUND:")
        print("\n".join(summary))
        print("-----------------------------\n")

        if not summary:
            return "No runs found in the last 30 activities."
            
        return "\n".join(summary)
        
    return "No runs found (API Error)."

# --- THE BRAIN (OpenAI) ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools_list = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_strava_stats",
            "description": "Get the user's recent run stats from Strava",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    print(f"User: {req.message}")
    
    # --- NEW: Get Today's Date ---
    today_str = datetime.now().strftime("%A, %B %d, %Y") # e.g., "Wednesday, December 17, 2025"

    # Step 1: Talk to AI (With Date Context)
    messages = [
        {
            "role": "system", 
            "content": f"You are a helpful Marathon Coach. Today is {today_str}. Compare the dates in the Strava data to today's date to correctly identify 'last Monday', 'yesterday', etc."
        },
        {"role": "user", "content": req.message}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools_list,
        tool_choice="auto"
    )
    
    msg = response.choices[0].message

    # Step 2: Handle Tool Calls
    if msg.tool_calls:
        messages.append(msg)
        
        for tool in msg.tool_calls:
            print(f"🤖 Tool Triggered: {tool.function.name}")
            result = "Error"
            
            if tool.function.name == "get_weather":
                args = json.loads(tool.function.arguments)
                result = get_weather(args.get("city"))
            elif tool.function.name == "get_strava_stats":
                result = get_strava_stats()
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool.id,
                "content": str(result)
            })
        
        # Step 3: Get Final Answer
        final = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return {"response": final.choices[0].message.content}

    return {"response": msg.content}