# # import os
# # import time
# # import shutil
# # import pandas as pd
# # from googleapiclient.discovery import build
# # from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
# # from google.auth.transport.requests import Request
# # from google.oauth2.credentials import Credentials
# # from google_auth_oauthlib.flow import InstalledAppFlow
# # from dotenv import load_dotenv
# # from langchain_mistralai import ChatMistralAI
# # from PyPDF2 import PdfReader
# # import io
# # import pickle

# # load_dotenv()

# # # Charger les informations de l'environnement
# # google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# # input_folder_id = os.getenv('INPUT_FOLDER_ID')
# # output_folder_id = os.getenv('OUTPUT_FOLDER_ID')
# # archive_folder_id = os.getenv('ARCHIVE_FOLDER_ID')

# # # Scopes pour l'accès Google Drive
# # SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Accès aux fichiers

# # # Authentification avec OAuth 2.0
# # def authenticate_google_drive():
# #     creds = None
# #     # Le fichier token.pickle stocke les credentials d'accès de l'utilisateur
# #     if os.path.exists('token.pickle'):
# #         with open('token.pickle', 'rb') as token:
# #             creds = pickle.load(token)

# #     # Si les credentials sont invalides, refaire le processus d'authentification
# #     if not creds or not creds.valid:
# #         if creds and creds.expired and creds.refresh_token:
# #             creds.refresh(Request())
# #         else:
# #             flow = InstalledAppFlow.from_client_secrets_file(google_credentials_path, SCOPES)
# #             creds = flow.run_local_server(port=0)

# #         # Sauvegarder les credentials dans token.pickle pour les prochaines exécutions
# #         with open('token.pickle', 'wb') as token:
# #             pickle.dump(creds, token)

# #     # Créer le service Google Drive
# #     drive_service = build('drive', 'v3', credentials=creds)
# #     return drive_service

# # # Télécharger un fichier depuis Google Drive
# # def download_file_from_drive(drive_service, file_id, local_path):
# #     request = drive_service.files().get_media(fileId=file_id)
# #     fh = io.FileIO(local_path, 'wb')
# #     downloader = MediaIoBaseDownload(fh, request)
# #     done = False
# #     while done is False:
# #         status, done = downloader.next_chunk()
# #     print(f"Fichier téléchargé: {local_path}")

# # # Upload du fichier vers Google Drive
# # def upload_file_to_drive(drive_service, local_file_path, folder_id, mime_type="application/vnd.ms-excel"):
# #     file_metadata = {
# #         'name': os.path.basename(local_file_path),
# #         'parents': [folder_id]
# #     }
# #     media = MediaIoBaseUpload(io.FileIO(local_file_path, 'rb'), mimetype=mime_type)
# #     file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
# #     print(f"Fichier téléchargé sur Drive : {file['id']}")
# #     return file['id']

# # # Extraire le texte d'un fichier PDF
# # def get_pdf_text(pdf_path):
# #     """Extrait le texte d'un fichier PDF."""
# #     text = ""
# #     pdf_reader = PdfReader(pdf_path)
# #     for page in pdf_reader.pages:
# #         extracted_text = page.extract_text()
# #         if extracted_text:
# #             text += extracted_text + "\n"
# #     return text.strip()

# # # Processus principal pour traiter les fichiers PDF et extraire les données
# # def process_pdf_files():
# #     # Initialisation du modèle IA
# #     llm = ChatMistralAI(model='mistral-large-latest', temperature=0)

# #     # Authentification Google Drive
# #     drive_service = authenticate_google_drive()

# #     # Récupérer la liste des fichiers PDF dans le dossier d'entrée sur Drive
# #     results = drive_service.files().list(q=f"'{input_folder_id}' in parents and mimeType='application/pdf'", 
# #                                          fields="files(id, name)").execute()
# #     files = results.get('files', [])

# #     if not files:
# #         print("Aucun fichier PDF trouvé dans le dossier d'entrée.")
# #         return

# #     # Liste pour stocker les résultats extraits des fichiers
# #     data = []

# #     # Pour chaque fichier PDF dans le dossier d'entrée
# #     for file in files:
# #         file_id = file['id']
# #         file_name = file['name']
# #         local_pdf_path = f'/tmp/{file_name}'

# #         print(f"📄 Traitement du fichier : {file_name}")

# #         # Télécharger le PDF depuis Google Drive vers un dossier temporaire local
# #         download_file_from_drive(drive_service, file_id, local_pdf_path)

# #         # Extraire le texte du fichier PDF
# #         text = get_pdf_text(local_pdf_path)

# #         if not text:
# #             print(f"⚠️ Aucun texte extrait du fichier {file_name}.")
# #             continue

# #         # Construction du message pour l'IA
# #         message = [
# #             ("system", """Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
# #             Ton objectif est d'extraire **de manière fidèle** les informations suivantes, **sans modifier ni interpréter** les données d'origine :

# #             ### **Informations à extraire :**
# #             1. **Nom du candidat**  
# #             2. **Les entreprises dans lesquelles la personne a travaillé** et leur classification :
# #                - Si c'est une **ESN**, indique-le clairement et liste ses clients.
# #                - Si c'est une **entreprise classique**, indique-le clairement également.

# #             3. **Les technologies utilisées** :
# #                - Associe chaque entreprise (ou client d'ESN) aux stacks techniques mentionnées dans le texte.
# #                - **Ne jamais inventer ou omettre une technologie** : si ce n’est pas précisé dans le texte, ne l'ajoute pas.

# #             4. **Si un client ESN est mentionné, précise à quelle ESN il est rattaché.**

# #             ### **Format de sortie attendu (exemple) :**
            
# #             ----
# #             **Nom du Candidat**  
# #             [Nom du candidat]  

# #             **Entreprise ESN**  
# #             [Nom de l'ESN]  

# #             **Client ESN : [Nom du client]** (ESN : [Nom de l'ESN])  
# #             - Technologie 1  
# #             - Technologie 2  

# #             **Client ESN : [Nom du client]** (ESN : [Nom de l'ESN])  
# #             - Technologie 3  
# #             - Technologie 4  

# #             ---
# #             **Entreprise classique**  
# #             [Nom de l'entreprise]  
# #             - Technologie 1  
# #             - Technologie 2  
            
# #             ----
# #             """),
# #             ("human", text)
# #         ]

# #         try:
# #             # Appel à l'API Mistral pour obtenir la réponse
# #             ai_msg = llm.invoke(message)
# #             extracted_text = ai_msg.content

# #             # Sauvegarder le texte brut dans un fichier .txt
# #             local_txt_path = f'/tmp/{file_name.replace(".pdf", ".txt")}'
# #             with open(local_txt_path, "w", encoding="utf-8") as f:
# #                 f.write(extracted_text)

# #             # Sauvegarder les fichiers traités (txt et xlsx) dans le dossier output
# #             upload_file_to_drive(drive_service, local_txt_path, output_folder_id, mime_type="text/plain")

# #             # Génération ou mise à jour du fichier Excel (si nécessaire)
# #             excel_path = '/tmp/resultats.xlsx'
# #             df = pd.DataFrame([["Nom", "Entreprise", "Status", "ESN", "Stacks"]])  # Simuler un traitement pour excel
# #             df.to_excel(excel_path, index=False)

# #             upload_file_to_drive(drive_service, excel_path, output_folder_id)

# #             # Déplacer le PDF traité vers le dossier d'archive sur Drive
# #             drive_service.files().update(fileId=file_id, addParents=archive_folder_id, removeParents=input_folder_id).execute()
# #             print(f"📦 PDF déplacé vers l'archive: {file_name}")

# #         except Exception as e:
# #             print(f"❌ Erreur lors du traitement de {file_name}: {e}")

# #         # Supprimer les fichiers locaux temporaires
# #         os.remove(local_pdf_path)
# #         os.remove(local_txt_path)

# # if __name__ == "__main__":
# #     process_pdf_files()




# import os
# import io
# import time
# import pickle
# import pandas as pd
# from dotenv import load_dotenv
# from PyPDF2 import PdfReader
# from langchain_mistralai import ChatMistralAI
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# # Charger les variables d'environnement
# load_dotenv()
# CLIENT_SECRET_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # credentials_oauth.json
# INPUT_FOLDER_ID = os.getenv("INPUT_FOLDER_ID")
# OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")
# ARCHIVE_FOLDER_ID = os.getenv("ARCHIVE_FOLDER_ID")

# SCOPES = ["https://www.googleapis.com/auth/drive"]  # Accès aux fichiers Drive

# def authenticate_google_drive():
#     creds = None
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#     return build('drive', 'v3', credentials=creds)

# def download_file(drive_service, file_id, local_path):
#     request = drive_service.files().get_media(fileId=file_id)
#     with open(local_path, 'wb') as f:
#         downloader = MediaIoBaseDownload(f, request)
#         done = False
#         while not done:
#             _, done = downloader.next_chunk()

# def upload_file(drive_service, local_path, folder_id, mime_type):
#     file_metadata = {
#         'name': os.path.basename(local_path),
#         'parents': [folder_id]
#     }
#     media = MediaIoBaseUpload(io.FileIO(local_path, 'rb'), mimetype=mime_type)
#     file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     print(f"✅ Fichier uploadé : {file['id']} ({os.path.basename(local_path)})")

# def extract_pdf_text(pdf_path):
#     reader = PdfReader(pdf_path)
#     return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

# def process_pdf_files():
#     drive = authenticate_google_drive()
#     llm = ChatMistralAI(model='mistral-large-latest', temperature=0)

#     response = drive.files().list(
#         q=f"'{INPUT_FOLDER_ID}' in parents and mimeType='application/pdf'",
#         fields="files(id, name)"
#     ).execute()

#     files = response.get('files', [])
#     if not files:
#         print("📭 Aucun fichier PDF trouvé dans le dossier d'entrée.")
#         return

#     for file in files:
#         file_id = file['id']
#         file_name = file['name']
#         local_pdf = f"/tmp/{file_name}"
#         local_txt = f"/tmp/{file_name.replace('.pdf', '.txt')}"
#         local_xlsx = "/tmp/resultats.xlsx"

#         try:
#             print(f"\n📄 Traitement de : {file_name}")
#             download_file(drive, file_id, local_pdf)
#             text = extract_pdf_text(local_pdf)

#             if not text:
#                 print("⚠️ Aucun texte extrait.")
#                 continue

#             message = [
#                 ("system", """Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
#             Ton objectif est d'extraire **de manière fidèle** les informations suivantes, **sans modifier ni interpréter** les données d'origine :

#             ### **Informations à extraire :**
#             1. **Nom du candidat**  
#             2. **Les entreprises dans lesquelles la personne a travaillé** et leur classification :
#                - Si c'est une **ESN**, indique-le clairement et liste ses clients.
#                - Si c'est une **entreprise classique**, indique-le clairement également.

#             3. **Les technologies utilisées** :
#                - Associe chaque entreprise (ou client d'ESN) aux stacks techniques mentionnées dans le texte.
#                - **Ne jamais inventer ou omettre une technologie** : si ce n’est pas précisé dans le texte, ne l'ajoute pas.

#             4. **Si un client ESN est mentionné, précise à quelle ESN il est rattaché.**

#             ### **Format de sortie attendu (exemple) :**
            
#             ----
#             **Nom du Candidat**  
#             [Nom du candidat]  

#             **Entreprise ESN**  
#             [Nom de l'ESN]  

#             **Client ESN : [Nom du client]** (ESN : [Nom de l'ESN])  
#             - Technologie 1  
#             - Technologie 2  

#             **Client ESN : [Nom du client]** (ESN : [Nom de l'ESN])  
#             - Technologie 3  
#             - Technologie 4  

#             ---
#             **Entreprise classique**  
#             [Nom de l'entreprise]  
#             - Technologie 1  
#             - Technologie 2  
            
#             ----
#             """),
#                 ("human", text)
#             ]

#             response = llm.invoke(message)
#             with open(local_txt, "w", encoding="utf-8") as f:
#                 f.write(response.content)

#             upload_file(drive, local_txt, OUTPUT_FOLDER_ID, "text/plain")

#             df = pd.DataFrame([["Nom", "Entreprise", "Status", "ESN", "Stacks"]])  # Exemple minimal
#             df.to_excel(local_xlsx, index=False)
#             upload_file(drive, local_xlsx, OUTPUT_FOLDER_ID, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

#             drive.files().update(
#                 fileId=file_id,
#                 addParents=ARCHIVE_FOLDER_ID,
#                 removeParents=INPUT_FOLDER_ID
#             ).execute()

#             print(f"📦 Archivé : {file_name}")

#         except Exception as e:
#             print(f"❌ Erreur sur {file_name} : {e}")

#         finally:
#             for f in [local_pdf, local_txt, local_xlsx]:
#                 if os.path.exists(f):
#                     os.remove(f)

# if __name__ == "__main__":
#     process_pdf_files()


# import os
# import pickle
# from googleapiclient.discovery import build
# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# from dotenv import load_dotenv

# load_dotenv()

# # Chargement des variables
# google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# input_folder_id = os.getenv("INPUT_FOLDER_ID")

# # Scopes
# SCOPES = ["https://www.googleapis.com/auth/drive"]

# def authenticate_google_drive():
#     creds = None
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(google_credentials_path, SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#     return build('drive', 'v3', credentials=creds)

# def list_files_in_folder(drive_service, folder_id):
#     query = f"'{folder_id}' in parents and trashed = false"
#     results = drive_service.files().list(q=query, fields="files(id, name)").execute()
#     files = results.get('files', [])
#     return files

# if __name__ == "__main__":
#     drive_service = authenticate_google_drive()
#     print(f"🔍 Recherche de fichiers dans le dossier ID : {input_folder_id}")

#     # 🔍 Afficher l'adresse e-mail connectée
#     about = drive_service.about().get(fields="user(emailAddress)").execute()
#     print(f"🧑 Connecté avec l'adresse : {about['user']['emailAddress']}")

#     results = drive_service.files().list(pageSize=10, fields="files(id, name)").execute()
#     for f in results.get('files', []):
#         print(f"📄 {f['name']} (ID: {f['id']})")


#     files = list_files_in_folder(drive_service, input_folder_id)
#     if not files:
#         print("❌ Aucun fichier trouvé dans le dossier.")
#     else:
#         print(f"✅ {len(files)} fichier(s) trouvé(s) :")
#         for f in files:
#             print(f"📄 {f['name']} (ID: {f['id']})")



import os
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

# Chargement des variables
google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
input_folder_id = os.getenv("INPUT_FOLDER_ID")

# Scopes
SCOPES = ["https://www.googleapis.com/auth/drive"]

def authenticate_google_drive():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(google_credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def list_files_in_folder(drive_service, folder_id):
    """Lister les fichiers dans un dossier spécifique sur Google Drive."""
    query = f"'{folder_id}' in parents and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files

if __name__ == "__main__":
    # Authentifier l'utilisateur et obtenir le service Google Drive
    drive_service = authenticate_google_drive()
    print(f"🔍 Recherche de fichiers dans le dossier ID : {input_folder_id}")

    # 🔍 Afficher l'adresse e-mail connectée
    about = drive_service.about().get(fields="user(emailAddress)").execute()
    print(f"🧑 Connecté avec l'adresse : {about['user']['emailAddress']}")

    # Vérifier les fichiers dans le dossier spécifié
    files = list_files_in_folder(drive_service, input_folder_id)
    
    if not files:
        print("❌ Aucun fichier trouvé dans le dossier.")
    else:
        print(f"✅ {len(files)} fichier(s) trouvé(s) dans le dossier :")
        for f in files:
            print(f"📄 {f['name']} (ID: {f['id']})")

