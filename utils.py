import os
import requests
import json
from google import genai

# Initialize Gemini API
gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
if gemini_api_key:
    gemini_client = genai.Client(api_key=gemini_api_key)
else:
    gemini_client = None

# Initialize Africa's Talking Credentials
username = os.environ.get('AT_USERNAME', 'sandbox')
api_key = os.environ.get('AT_API_KEY', '')

def send_alert(phone_number, item_title):
    """
    Sends an SMS alert to the user natively via AT's REST API.
    Bypassing the official SDK to silence Sandbox SSL Errors.
    """
    if not api_key:
        print("Africa's Talking API key not configured. Skipping alert.")
        return

    # E.164 formatting
    if phone_number.startswith('0'):
        phone_number = '+254' + phone_number[1:]
        
    message = f"CampusFind Alert: Good news! An item matching '{item_title}' has been reported found. Please check your account."
    
    url = "https://api.sandbox.africastalking.com/version1/messaging" if username == 'sandbox' else "https://api.africastalking.com/version1/messaging"
    
    headers = {
        'apikey': api_key,
        'Accept': 'application/json'
    }
    
    data = {
        'username': username,
        'to': phone_number,
        'message': message
    }
    
    try:
        # verify=False ignores the buggy sandbox SSL
        response = requests.post(url, data=data, headers=headers, verify=False)
        print(f"Alert sent to {phone_number}: {response.json()}")
    except Exception as e:
        print(f"Failed to send alert to {phone_number}: {e}")

def evaluate_match_with_ai(lost_item, found_item):
    """
    Uses Gemini API to evaluate if a lost item and a found item are a match.
    Returns True if the AI considers it a match with high confidence, False otherwise.
    """
    if not gemini_client:
        print("Gemini API key not configured. Falling back to simple category match.")
        return lost_item.category == found_item.category

    prompt = f"""
    You are an AI assistant for a Lost and Found application. Your task is to determine if a reported 'lost' item and a reported 'found' item are likely the exact same physical item.

    Lost Item Details:
    - Title: {lost_item.title}
    - Description: {lost_item.description}
    - Location Lost: {lost_item.location}
    - Date Lost: {lost_item.date_lost}
    - Category: {lost_item.category}

    Found Item Details:
    - Title: {found_item.title}
    - Description: {found_item.description}
    - Location Found: {found_item.location}
    - Date Found: {found_item.date_lost}
    - Category: {found_item.category}

    Please analyze the details above. Consider similarities in title, description, location proximity, and timing.
    Respond ONLY with a valid JSON object in the following format:
    {{
        "match": true/false,
        "confidence": 0-100,
        "reason": "a brief explanation of your decision"
    }}
    Do not include any markdown formatting like ```json or ``` in your response. Just return the raw JSON object.
    """

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        response_text = response.text.strip()
        
        # Remove markdown JSON block if the model included it despite instructions
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        result = json.loads(response_text.strip())
        
        print(f"AI Match Evaluation: {result}")
        
        is_match = result.get('match', False)
        confidence = result.get('confidence', 0)
        
        # Determine match based on the AI's boolean flag and confidence > 70
        if is_match and confidence >= 70:
            return True
        return False
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Fallback to category match if API fails
        return lost_item.category == found_item.category
