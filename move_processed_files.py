# import os
# import shutil
# from dotenv import load_dotenv

# load_dotenv()
# projet_path = os.getenv('PROJECT_PATH')


# def move_processed_files(src_folder, dest_folder):
    
#     if not os.path.exists(dest_folder):
#         os.makedirs(dest_folder)
#         print(f"Dossier créé : {dest_folder}")
    
#     for filename in os.listdir(src_folder):
#         file_path = os.path.join(src_folder,filename)
#         if filename.endswith(".pdf"):
#             shutil.move(file_path, os.path.join(dest_folder,filename))
#         print(f"Fichier {filename} traité et deplacé vers {dest_folder}")

# if __name__ == "__main__":
#     move_processed_files(f'{projet_path}/data', f'{projet_path}/data_processed')

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


### chatou 30/04

# import os
# import shutil
# from dotenv import load_dotenv
# from auth_utils import get_drive_service

# load_dotenv()

# def move_processed_files(service, file_ids):
#     """Déplace les fichiers traités vers le dossier d'archive sur Google Drive."""
#     archive_folder_id = os.getenv("ARCHIVE_FOLDER_ID")
#     input_folder_id = os.getenv("INPUT_FOLDER_ID")

#     for file_id in file_ids:
#         service.files().update(
#             fileId=file_id, 
#             addParents=archive_folder_id, 
#             removeParents=input_folder_id
#         ).execute()
        
#     print(f"Fichiers déplacés vers {archive_folder_id}")

# if __name__ == "__main__":
#     # Exemple d'appel à la fonction avec un service Google Drive valide
#     service = get_drive_service()
#     file_ids = ['id_1', 'id_2', 'id_3']  # Liste d'exemple d'ID de fichiers traités
#     move_processed_files(service, file_ids)


from auth_utils import get_drive_service
import os

def get_pdf_ids_in_folder(service, folder_id):
    """
    Récupère les IDs des fichiers PDF dans un dossier Google Drive.
    """
    query = f"'{folder_id}' in parents and mimeType = 'application/pdf'"
    results = service.files().list(q=query, fields="files(id)").execute()
    return [file['id'] for file in results.get('files', [])]

def move_processed_files_to_archive(service, input_folder_id, archive_folder_id):
    """
    Déplace les fichiers PDF traités du dossier input vers le dossier archive.
    """
    file_ids = get_pdf_ids_in_folder(service, input_folder_id)

    if not file_ids:
        print("ℹ️ Aucun fichier PDF trouvé dans le dossier input.")
        return 0

    print(f"🚚 Déplacement de {len(file_ids)} fichiers PDF vers le dossier archive...")

    for file_id in file_ids:
        try:
            service.files().update(
                fileId=file_id,
                addParents=archive_folder_id,
                removeParents=input_folder_id,
                fields='id, parents'
            ).execute()
        except Exception as e:
            print(f"❌ Échec du déplacement du fichier {file_id} : {e}")

    print(f"✅ {len(file_ids)} fichiers déplacés.")
    return len(file_ids)

if __name__ == "__main__":
    # Récupère le service Google Drive
    service = get_drive_service()

    # Récupère les IDs des dossiers depuis .env
    input_folder_id = os.getenv("INPUT_FOLDER_ID")
    archive_folder_id = os.getenv("ARCHIVE_FOLDER_ID")

    if not input_folder_id or not archive_folder_id:
        print("❌ Les IDs des dossiers ne sont pas définis dans .env")
        exit(1)

    # Déplace les fichiers traités
    moved_count = move_processed_files_to_archive(service, input_folder_id, archive_folder_id)
    print(f"✅ {moved_count} fichiers déplacés vers l'archive.")