import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow

CREDENTIALS_PATH = os.getenv("CREDENTIALS_OAUTH_PATH")
TOKEN_PATH = os.getenv("TOKEN_PATH")

flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, scopes=['https://www.googleapis.com/auth/drive'])
creds = flow.run_local_server(port=0)

with open(TOKEN_PATH, 'wb') as token:
    pickle.dump(creds, token)

print("✅ Token généré avec succès.")
