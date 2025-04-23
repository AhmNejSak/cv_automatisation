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


#######
import os
import io
import pickle
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
output_folder_id = os.getenv('OUTPUT_FOLDER_ID')
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_drive():
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

def clean_excel_on_drive():
    drive_service = authenticate_drive()

    # Trouver le fichier Excel sur le Drive
    results = drive_service.files().list(
        q=f"'{output_folder_id}' in parents and name='resultats.xlsx' and trashed=false",
        fields="files(id, name)").execute()
    files = results.get('files', [])
    if not files:
        print("❌ Aucun fichier resultats.xlsx trouvé.")
        return

    file_id = files[0]['id']

    # Télécharger
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)

    df = pd.read_excel(fh)
    df = df.sort_values(by=['Nom'])
    df_cleaned = df.drop_duplicates()

    # Réécriture locale temporaire
    cleaned_path = '/tmp/resultats_cleaned.xlsx'
    df_cleaned.to_excel(cleaned_path, index=False)

    # Réécriture sur Drive (écrasement)
    media_body = MediaIoBaseUpload(io.FileIO(cleaned_path, 'rb'), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    drive_service.files().update(fileId=file_id, media_body=media_body).execute()

    print("🧼 Fichier Excel nettoyé et mis à jour sur Drive.")

if __name__ == "__main__":
    clean_excel_on_drive()


#######
