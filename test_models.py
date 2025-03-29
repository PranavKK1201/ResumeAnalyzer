import os
import requests
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return

    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("\nAvailable Gemini Models:")
            print("-" * 50)
            for model in models:
                print(f"Name: {model.get('name', 'N/A')}")
                print(f"Display Name: {model.get('displayName', 'N/A')}")
                print(f"Description: {model.get('description', 'N/A')}")
                print("-" * 50)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_available_models() 