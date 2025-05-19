# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from dotenv import load_dotenv

# load_dotenv()



# # Chemin vers le fichier token.pickle
# TOKEN_PATH = os.getenv('TOKEN_PATH')
# CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# def authenticate_google_drive():
#     creds = None
#     if os.path.exists(TOKEN_PATH):
#         with open(TOKEN_PATH, 'rb') as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 CREDENTIALS_PATH,
#                 scopes=['https://www.googleapis.com/auth/drive']
#             )
#             creds = flow.run_local_server(port=0)  # Ouvre un navigateur pour l'autorisation

#         with open(TOKEN_PATH, 'wb') as token:
#             pickle.dump(creds, token)

#     print("Token OAuth généré ou rafraîchi avec succès.")
#     return creds


##### chat gpt du 30/04/2025

# google_drive_utils.py
# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build

# def get_drive_service():
#     scopes = ['https://www.googleapis.com/auth/drive']
#     creds = None
#     token_path = os.getenv("TOKEN_PATH")
#     credentials_path = os.getenv("CREDENTIALS_OAUTH_PATH")

#     # Charger les credentials existants
#     if os.path.exists(token_path):
#         with open(token_path, 'rb') as token:
#             creds = pickle.load(token)

#     # Rafraîchir ou demander l'authentification
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             raise RuntimeError(
#                 "Token OAuth manquant ou expiré. Lance manuellement l'authentification pour générer un nouveau token.pickle"
#             )

#         with open(token_path, 'wb') as token:
#             pickle.dump(creds, token)

#     return build('drive', 'v3', credentials=creds)


###### chatou 30/04 v2

# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
# import shutil

# def get_drive_service():
#     """Récupère un service Google Drive authentifié."""
#     scopes = ['https://www.googleapis.com/auth/drive']
#     creds = None
#     token_path = os.getenv("TOKEN_PATH")
#     credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

#     # Charger les credentials existants
#     if os.path.exists(token_path):
#         with open(token_path, 'rb') as token:
#             creds = pickle.load(token)

#     # Rafraîchir ou demander l'authentification
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             # Si le token est manquant ou expiré, demande une nouvelle authentification
#             flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes=scopes)
#             creds = flow.run_local_server(port=0)

#         # Sauvegarder les credentials dans le token
#         with open(token_path, 'wb') as token:
#             pickle.dump(creds, token)

#     return build('drive', 'v3', credentials=creds)


# def download_pdf_files(service):
#     """Télécharge tous les fichiers PDF du dossier Google Drive spécifié."""
#     input_folder_id = os.getenv("INPUT_FOLDER_ID")

#     # Recherche tous les fichiers PDF dans le dossier d'entrée
#     results = service.files().list(q=f"'{input_folder_id}' in parents and mimeType = 'application/pdf'", fields="files(id, name)").execute()
#     files = results.get('files', [])

#     pdf_files = []
#     for file in files:
#         file_id = file['id']
#         file_name = file['name']
#         file_path = os.path.join(os.getenv("PROJECT_PATH"), 'data', file_name)

#         # Préparer la requête pour télécharger le fichier
#         request = service.files().get_media(fileId=file_id)
#         with open(file_path, 'wb') as f:
#             downloader = MediaIoBaseDownload(f, request)
#             done = False
#             while done is False:
#                 status, done = downloader.next_chunk()

#         pdf_files.append(file_path)

#     return pdf_files


# def upload_excel_file(service, excel_path):
#     """Téléverse le fichier Excel généré dans le dossier de sortie Google Drive."""
#     output_folder_id = os.getenv("OUTPUT_FOLDER_ID")
    
#     # Préparer les métadonnées du fichier
#     file_metadata = {'name': 'resultats.xlsx', 'parents': [output_folder_id]}
#     media = MediaFileUpload(excel_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

#     # Téléverser le fichier
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

#     return file.get('id')  # Retourne l'ID du fichier sur Google Drive


# def move_files_to_archive(service, file_ids):
#     """Déplace les fichiers traités vers le dossier d'archive sur Google Drive."""
#     archive_folder_id = os.getenv("ARCHIVE_FOLDER_ID")

#     for file_id in file_ids:
#         service.files().update(fileId=file_id, addParents=archive_folder_id, removeParents=os.getenv("INPUT_FOLDER_ID")).execute()

#     return len(file_ids)  # Retourne le nombre de fichiers déplacés


# def move_processed_files(src_folder, dest_folder):
#     """Déplace les fichiers traités dans un autre dossier local (local-to-local)."""
#     if not os.path.exists(dest_folder):
#         os.makedirs(dest_folder)
#         print(f"Dossier créé : {dest_folder}")
    
#     for filename in os.listdir(src_folder):
#         file_path = os.path.join(src_folder, filename)
#         if filename.endswith(".pdf"):
#             shutil.move(file_path, os.path.join(dest_folder, filename))
#         print(f"Fichier {filename} traité et déplacé vers {dest_folder}")



import os
import io
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import shutil

def get_drive_service():
    """Récupère un service Google Drive authentifié."""
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = None
    token_path = os.getenv("TOKEN_PATH")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Charger les credentials existants
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # Rafraîchir ou demander l'authentification
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Si le token est manquant ou expiré, demande une nouvelle authentification
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes=scopes)
            creds = flow.run_local_server(port=0)

        # Sauvegarder les credentials dans le token
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def download_file(service, file_id):
    """Télécharge un fichier spécifique de Google Drive."""
    request = service.files().get_media(fileId=file_id)
    file_path = f"/tmp/{file_id}.pdf"  # Définir un nom de fichier dynamique basé sur l'ID
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return file_path

def download_pdf_files(service, folder_id):
    """Télécharge tous les fichiers PDF dans le dossier Google Drive spécifié."""
    results = service.files().list(q=f"'{folder_id}' in parents and mimeType = 'application/pdf'", fields="files(id)").execute()
    files = results.get('files', [])

    if not files:
        print("Aucun fichier PDF trouvé.")
        return []

    pdf_files = []
    for file in files:
        file_id = file['id']
        file_path = download_file(service, file_id)
        pdf_files.append(file_path)

    return pdf_files

def upload_file_to_drive(service, file_path, file_id):
    """Téléverse un fichier Excel sur Google Drive en utilisant son ID."""
    media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    service.files().update(fileId=file_id, media_body=media).execute()

def move_files_to_archive(service, file_ids):
    """Déplace les fichiers traités vers le dossier d'archive sur Google Drive."""
    archive_folder_id = os.getenv("ARCHIVE_FOLDER_ID")
    input_folder_id = os.getenv("INPUT_FOLDER_ID")

    for file_id in file_ids:
        service.files().update(fileId=file_id, addParents=archive_folder_id, removeParents=input_folder_id).execute()

    return len(file_ids)  # Retourne le nombre de fichiers déplacés


def get_file_id_by_name(service, file_name, folder_id):
    """
    Récupère l'ID d'un fichier donné son nom et l'ID du dossier.
    
    Returns:
        str: L'ID du fichier si trouvé, None sinon.
    """
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])

    if files:
        return files[0]['id']  # Retourne le premier fichier trouvé
    return None


def get_pdf_ids_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and mimeType = 'application/pdf'"
    results = service.files().list(q=query, fields="files(id)").execute()
    return [file['id'] for file in results.get('files', [])]