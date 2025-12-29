# 🏃‍♂️ AI Marathon Coach (Powered by OpenAI + Strava)

A personalized running coach agent that connects an LLM (GPT-4o) directly to real-time athlete data via the Strava API.

## 🚀 How It Works
Unlike generic chatbots, this agent has **"Tools"**:
1.  **Context Awareness:** It knows "Today's Date" and can interpret relative time (e.g., "Last Monday").
2.  **Real Data:** It fetches my actual run stats (Pace, Distance, Date) from Strava.
3.  **Reasoning:** It analyzes fatigue and performance to prescribe specific workouts (Tempo vs. Recovery).

## 🛠️ Tech Stack
* **Core:** Python 3.12, FastAPI
* **AI:** OpenAI GPT-4o (Function Calling)
* **Data:** Strava API (OAuth2)
* **Dev Tools:** Uvicorn, Dotenv

## 📸 Demo
### The AI Analyzing My Data
<img width="1942" height="616" alt="image" src="https://github.com/user-attachments/assets/981594b4-7e45-47d3-b1b8-63d2340643b9" />

## ⚙️ Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your keys (STRAVA_CLIENT_ID, OPENAI_API_KEY, etc.)
4. Run: `python -m uvicorn main:app --reload`
