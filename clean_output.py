# from dotenv import load_dotenv
# import os
# import pandas as pd


# load_dotenv()
# project_path = os.getenv('PROJECT_PATH')

# def clean_excel_file():
#     # output_file = '/home/ahsak/Bureau/IA_projet/output/resultats.xlsx' ## modif'
#     output_file = f'{project_path}/output/resultats.xlsx' ## modif'

#     # Lire le fichier Excel existant
#     df = pd.read_excel(output_file)

#     # Trier par Nom et Entreprise pour regrouper les entrées similaires
#     df = df.sort_values(by=['Nom']) # gérer les doublons voir comment faire pour ne perdre que très peu d'informations

#     # Supprimer les doublons exacts
#     df_cleaned = df.drop_duplicates()

#     # Sauvegarder le fichier nettoyé en gardant l'organisation cohérente
#     df_cleaned.to_excel(output_file, index=False)

#     print(f"Fichier Excel nettoyé et mis à jour : {output_file}")

# if __name__ == "__main__":
#     clean_excel_file()


# #######
# import os
# import io
# import pickle
# import pandas as pd
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# from dotenv import load_dotenv

# load_dotenv()

# google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# output_folder_id = os.getenv('OUTPUT_FOLDER_ID')
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

# def clean_excel_on_drive():
#     drive_service = authenticate_drive()

#     # Trouver le fichier Excel sur le Drive
#     results = drive_service.files().list(
#         q=f"'{output_folder_id}' in parents and name='resultats.xlsx' and trashed=false",
#         fields="files(id, name)").execute()
#     files = results.get('files', [])
#     if not files:
#         print("❌ Aucun fichier resultats.xlsx trouvé.")
#         return

#     file_id = files[0]['id']

#     # Télécharger
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         _, done = downloader.next_chunk()
#     fh.seek(0)

#     df = pd.read_excel(fh)
#     df = df.sort_values(by=['Nom'])
#     df_cleaned = df.drop_duplicates()

#     # Réécriture locale temporaire
#     cleaned_path = '/tmp/resultats_cleaned.xlsx'
#     df_cleaned.to_excel(cleaned_path, index=False)

#     # Réécriture sur Drive (écrasement)
#     media_body = MediaIoBaseUpload(io.FileIO(cleaned_path, 'rb'), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     drive_service.files().update(fileId=file_id, media_body=media_body).execute()

#     print("🧼 Fichier Excel nettoyé et mis à jour sur Drive.")

# if __name__ == "__main__":
#     clean_excel_on_drive()


# ####### chatou 30/04

# from dotenv import load_dotenv
# import os
# import io
# import pandas as pd
# from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
# from auth_utils import get_drive_service, download_file, upload_file_to_drive

# load_dotenv()
# project_path = os.getenv('PROJECT_PATH')

# def clean_excel_file(service):
#     output_folder_id = os.getenv("OUTPUT_FOLDER_ID")
#     excel_file_id = get_file_id_by_name(service, "resultats.xlsx", output_folder_id)
    
#     if excel_file_id:
#         file_path = download_file(service, excel_file_id)
#         df = pd.read_excel(file_path)
#         df = df.sort_values(by=['Nom']).drop_duplicates()
#         cleaned_path = "/tmp/resultats_cleaned.xlsx"
#         df.to_excel(cleaned_path, index=False)

#         upload_file_to_drive(service, cleaned_path, excel_file_id)
#         print(f"Fichier Excel nettoyé et mis à jour : {cleaned_path}")

# def download_file(service, file_id):
#     request = service.files().get_media(fileId=file_id)
#     file_path = "/tmp/temp_file.xlsx"
#     fh = io.FileIO(file_path, 'wb')
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         status, done = downloader.next_chunk()
#     return file_path

# def upload_file_to_drive(service, file_path, file_id):
#     media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     service.files().update(fileId=file_id, media_body=media).execute()

# def get_file_id_by_name(service, filename, folder_id):
#     query = f"'{folder_id}' in parents and name = '{filename}'"
#     results = service.files().list(q=query, fields="files(id)").execute()
#     files = results.get('files', [])
#     return files[0]['id'] if files else None

# if __name__ == "__main__":
#     service = get_drive_service()
#     clean_excel_file(service)


# from dotenv import load_dotenv
# import os
# import io
# import pandas as pd
# from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
# from auth_utils import get_drive_service, download_file, upload_file_to_drive, get_file_id_by_name

# load_dotenv()
# project_path = os.getenv('PROJECT_PATH')

# def clean_excel_file(service):
#     output_folder_id = os.getenv("OUTPUT_FOLDER_ID")
#     excel_file_id = get_file_id_by_name(service, "resultats.xlsx", output_folder_id)
    
#     if excel_file_id:
#         # Télécharger le fichier Excel depuis Google Drive
#         file_path = download_file(service, excel_file_id)
        
#         # Lire le fichier Excel et nettoyer les données
#         df = pd.read_excel(file_path)
#         df = df.sort_values(by=['Nom']).drop_duplicates()
        
#         # Enregistrer le fichier nettoyé localement
#         cleaned_path = "/tmp/resultats_cleaned.xlsx"
#         df.to_excel(cleaned_path, index=False)

#         # Télécharger le fichier nettoyé sur Google Drive
#         upload_file_to_drive(service, cleaned_path, excel_file_id)
#         print(f"Fichier Excel nettoyé et mis à jour : {cleaned_path}")

# if __name__ == "__main__":
#     service = get_drive_service()  # Obtenir le service Google Drive authentifié
#     clean_excel_file(service)  # Nettoyer le fichier Excel



from dotenv import load_dotenv
import os
import pandas as pd
from auth_utils import get_drive_service, download_file, upload_file_to_drive, get_file_id_by_name

load_dotenv()

def clean_excel_file(service):
    """
    Nettoie le fichier Excel 'resultats.xlsx' en supprimant les doublons
    basés sur la colonne 'Nom', puis met à jour le fichier sur Google Drive.
    """

    output_folder_id = os.getenv("OUTPUT_FOLDER_ID")
    excel_file_name = "resultats.xlsx"

    # Récupère l'ID du fichier Excel
    excel_file_id = get_file_id_by_name(service, excel_file_name, output_folder_id)

    if not excel_file_id:
        print(f"❌ Le fichier '{excel_file_name}' n’a pas été trouvé dans le dossier de sortie.")
        return

    print("📥 Téléchargement du fichier Excel en cours...")

    # Télécharge le fichier Excel depuis Google Drive
    file_path = download_file(service, excel_file_id)

    if not os.path.exists(file_path):
        print(f"❌ Échec du téléchargement du fichier {excel_file_name}.")
        return

    try:
        # Lit le fichier Excel
        df = pd.read_excel(file_path)

        # Nettoyage : suppression des doublons basés sur la colonne 'Nom'
        # df_cleaned = df.sort_values(by=['Nom']).drop_duplicates()

        # tester sur un petit fichier le ordre non alphabetique
        df_cleaned = df.drop_duplicates()
        df_cleaned = df.drop('Date Ingestion')

        # Enregistrement du fichier nettoyé localement
        cleaned_path = "/tmp/resultats_cleaned.xlsx"
        df_cleaned.to_excel(cleaned_path, index=False)
        print("🧼 Fichier Excel nettoyé localement.")

        # Téléverse le fichier nettoyé sur Google Drive (remplace le fichier original)
        upload_file_to_drive(service, cleaned_path, excel_file_id)
        print(f"📤 Fichier Excel mis à jour sur Google Drive (ID: {excel_file_id})")

    except Exception as e:
        print(f"❌ Erreur lors du nettoyage du fichier Excel : {e}")

if __name__ == "__main__":
    service = get_drive_service()  # Authentification Google Drive
    clean_excel_file(service)      # Nettoyage du fichier Excel