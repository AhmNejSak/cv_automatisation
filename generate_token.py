# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

# def generate_token_pickle(client_secrets_path, token_path):
#     creds = None
#     if os.path.exists(token_path):
#         with open(token_path, 'rb') as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 client_secrets_path,
#                 scopes=['https://www.googleapis.com/auth/drive']
#             )
#             creds = flow.run_local_server(port=0)  # Ouvre un navigateur pour l'autorisation

#         with open(token_path, 'wb') as token:
#             pickle.dump(creds, token)

#     print(f"Token sauvegardé dans {token_path}")

# if __name__ == "__main__":
#     generate_token_pickle(
#         client_secrets_path='credentials_oauth.json',  
#         token_path='token.pickle'
#     )





# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from dotenv import load_dotenv

# load_dotenv()

# def generate_token_pickle(client_secrets_path, token_path):
#     creds = None
#     if os.path.exists(token_path):
#         with open(token_path, 'rb') as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 client_secrets_path,
#                 scopes=['https://www.googleapis.com/auth/drive']
#             )

#             # Étape 1 : Générer l'URL d'autorisation
#             authorization_url, state = flow.authorization_url(
#                 access_type='offline',  # Permet d'obtenir un refresh token
#                 include_granted_scopes=True
#             )
#             print(f"Ouvrez cette URL dans un navigateur pour autoriser l'application : {authorization_url}")

#             # Étape 2 : Récupérer le code d'autorisation
#             authorization_code = input("Entrez le code d'autorisation ici : ")

#             # Étape 3 : Échanger le code contre un token
#             flow.fetch_token(code=authorization_code)
#             creds = flow.credentials

#         # Sauvegarder les nouveaux credentials dans token.pickle
#         with open(token_path, 'wb') as token:
#             pickle.dump(creds, token)

#     print(f"Token sauvegardé dans {token_path}")

# if __name__ == "__main__":
#     generate_token_pickle(
#         client_secrets_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
#         token_path=os.getenv('TOKEN_PATH')
#     )



###### chatou 30/04

# generate_token.py
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
