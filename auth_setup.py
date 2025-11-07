import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# שני הקבצים שצריך: credentials.json (קיים) ו-token.json (יווצר)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

if not os.path.exists(CREDENTIALS_FILE):
    print("ERROR: credentials.json not found! Place it in the same directory.")
else:
    print(f"Starting authentication process using {CREDENTIALS_FILE}...")
    try:
        # זה יפתח חלון דפדפן לאישור הגישה
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # שמירת האישור הקבוע
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print(f"✅ token.json created successfully!")
        print("---")
        print("NEXT STEP: Copy 'token.json' and 'credentials.json' to your Langflow folder.")
    except Exception as e:
        print(f"❌ An error occurred during the OAuth flow: {e}")
        print("Please ensure you installed all required libraries and the credentials file is correct.")