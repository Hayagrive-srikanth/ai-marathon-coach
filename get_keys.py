import requests

client_id = "187173"
client_secret = "5acc0a72a6840084975a61b56e7d8603a234e352"  
code = "ed83f179c7b53f7e9670359d8d92405f4babb020"  

def get_tokens():
    print("Exchanging code for tokens...")
    url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(url, data=payload)
    data = response.json()
    
    if 'refresh_token' in data:
        print("\n SUCCESS! Copy this into your .env file:")
        print(f"STRAVA_REFRESH_TOKEN=\"{data['refresh_token']}\"")
    else:
        print("\n Error:", data)

if __name__ == "__main__":
    get_tokens()
