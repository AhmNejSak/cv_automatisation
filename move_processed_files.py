# import os
# import shutil
# def move_processed_files(src_folder, dest_folder):

#     # créer le dossier de destination s'il n'existe pas
#     if not os.path.exists(dest_folder):
#         os.makedirs(dest_folder)
#         print(f"Dossier créé : {dest_folder}")

#     # deplacement des cv traités dans le dossier data_processed
#     for filename in os.listdir(src_folder):
#         file_path = os.path.join(src_folder,filename)
#         if filename.endwith(".pdf"):
#             shutil.move(file_path, os.path.join(dest_folder,filename))
#         print(f"Fichier {filename} traité et deplacé vers {dest_folder}")

# if __name__ == "__main__":
#     move_processed_files('/home/ahsak/Bureau/IA_projet/data', '/home/ahsak/Bureau/IA_projet/data_processed')

########

# import os
# import shutil
# from dotenv import load_dotenv

# load_dotenv()
# project_path = os.getenv('PROJECT_PATH')


# def move_processed_file(src_folder, dest_folder):
#     """Déplacer les fichiers traités dans un dossier différent."""
    
#     if not os.path.exists(dest_folder):
#         os.makedirs(dest_folder)
#         print(f"Dossier créé : {dest_folder}")

#     for filename in os.listdir(src_folder):
#         file_path = os.path.join(src_folder, filename)
        
#         if os.path.isfile(file_path) and filename.endswith(".pdf"):
#             try:
#                 shutil.move(file_path, os.path.join(dest_folder, filename))
#                 print(f"Fichier {filename} déplacé vers : {dest_folder}")
#             except Exception as e:
#                 print(f"Erreur lors du déplacement du fichier {filename}: {e}")
#         else:
#             print(f"Le fichier {filename} n'est pas un PDF ou n'est pas un fichier valide.")

# if __name__ == "__main__":
#     move_processed_file(f'{project_path}/data', f'{project_path}/data_processed') ##modif'

########


# import os
# import pickle
# from googleapiclient.discovery import build
# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# from dotenv import load_dotenv

# load_dotenv()

# google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# input_folder_id = os.getenv('INPUT_FOLDER_ID')
# archive_folder_id = os.getenv('ARCHIVE_FOLDER_ID')
# SCOPES = ['https://www.googleapis.com/auth/drive']

# def authenticate_drive():
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

# def move_files_to_archive():
#     drive_service = authenticate_drive()

#     query = f"'{input_folder_id}' in parents and mimeType='application/pdf' and trashed=false"
#     results = drive_service.files().list(q=query, fields="files(id, name)").execute()
#     files = results.get('files', [])

#     if not files:
#         print("📂 Aucun fichier à déplacer.")
#         return

#     for file in files:
#         try:
#             drive_service.files().update(
#                 fileId=file['id'],
#                 addParents=archive_folder_id,
#                 removeParents=input_folder_id
#             ).execute()
#             print(f"✅ {file['name']} déplacé dans l'archive.")
#         except Exception as e:
#             print(f"❌ Erreur avec {file['name']} : {e}")

# if __name__ == "__main__":
#     move_files_to_archive()


########## SOLUTION QWEN AI ############

import os
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv


load_dotenv()

# google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# input_folder_id = os.getenv('INPUT_FOLDER_ID')
# archive_folder_id = os.getenv('ARCHIVE_FOLDER_ID')
# SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_google_drive(token_path):
    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Les credentials ne sont pas valides et ne peuvent pas être rafraîchis.")

    return build('drive', 'v3', credentials=creds)

def move_files_to_archive(token_path, input_folder_id, archive_folder_id):
    drive_service = authenticate_google_drive(token_path)

    query = f"'{input_folder_id}' in parents and mimeType='application/pdf' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("📂 Aucun fichier à déplacer.")
        return

    for file in files:
        try:
            drive_service.files().update(
                fileId=file['id'],
                addParents=archive_folder_id,
                removeParents=input_folder_id
            ).execute()
            print(f"✅ {file['name']} déplacé dans l'archive.")
        except Exception as e:
            print(f"❌ Erreur avec {file['name']} : {e}")

if __name__ == "__main__":
    token_path = os.getenv('TOKEN_PATH')
    input_folder_id = os.getenv('INPUT_FOLDER_ID')
    archive_folder_id = os.getenv('ARCHIVE_FOLDER_ID')

    move_files_to_archive(token_path, input_folder_id, archive_folder_id)