# from PyPDF2 import PdfReader
# import os
# from dotenv import load_dotenv
# import time
# from langchain_mistralai import ChatMistralAI
# import pandas as pd

# load_dotenv()
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
# project_path = os.getenv('PROJECT_PATH')


# def get_pdf_text(pdf_path):
#     """Extrait le texte d'un fichier PDF."""
#     text = ""
#     pdf_reader = PdfReader(pdf_path)
#     for page in pdf_reader.pages:
#         extracted_text = page.extract_text()
#         if extracted_text:
#             text += extracted_text + "\n"
#     return text.strip()


# def process_pdf_files():
#     """Processus principal pour traiter les fichiers PDF et extraire les données."""
#     # Initialisation du modèle IA
#     llm = ChatMistralAI(model='mistral-large-latest', temperature=0)

#     # Définition des chemins
#     pdf_folder = f"{project_path}/data"
#     output_folder = f"{project_path}/output"
#     excel_path = f"{project_path}/output/resultats.xlsx"

#     # Création du dossier de sortie si nécessaire
#     os.makedirs(output_folder, exist_ok=True)

#     # Récupérer les fichiers PDF
#     pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    
#     # Liste pour stocker les données extraites
#     data = []

#     # Parcours des fichiers PDF
#     for pdf_file in pdf_files:
#         pdf_path = os.path.join(pdf_folder, pdf_file)
#         print(f"📄 Traitement du fichier : {pdf_file}")

#         # Extraire le texte du PDF
#         text = get_pdf_text(pdf_path)

#         if not text:
#             print(f"⚠️ Aucun texte extrait du fichier {pdf_file}, il pourrait être vide ou mal scanné.")
#             continue

#         # Construction du message pour l'IA
#         message = [
#             ("system",
#             """Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
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
#             """
#             ),
#             ("human", text)
#         ]

#         try:
#             # Appel au modèle IA pour obtenir la réponse
#             ai_msg = llm.invoke(message)
#             text_brute = ai_msg.content

#             # Sauvegarde du texte brut dans un fichier
#             output_file = os.path.join(output_folder, f"output_{pdf_file.replace('.pdf', '.txt')}")
#             with open(output_file, "w", encoding="utf-8") as f:
#                 f.write(text_brute)

#             print(f"✅ Résultat sauvegardé dans {output_file}")

#             # Traitement du texte brut pour en extraire les données structurées
#             lines = text_brute.split("\n")
#             nom_candidat = ""
#             entreprise = ""
#             status = ""
#             esn_nom = "-"
#             stacks = []

#             for i, line in enumerate(lines):
#                 line = line.strip()
                
#                 if line.startswith("**Nom du Candidat**"):
#                     nom_candidat = lines[i + 1].strip() if i + 1 < len(lines) else ""
                
#                 elif line.startswith("**Entreprise ESN**"):
#                     entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
#                     status = "ESN"
#                     esn_nom = "-"
                
#                 elif line.startswith("**Client ESN :"):
#                     parts = line.replace("**Client ESN :", "").replace("**", "").strip().split("(ESN :")
#                     entreprise = parts[0].strip()
#                     esn_nom = parts[1].replace(")", "").strip() if len(parts) > 1 else "-"
#                     status = "Client ESN"
                
#                 elif line.startswith("**Entreprise classique**"):
#                     entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
#                     status = "Entreprise Classique"
#                     esn_nom = "-"
                
#                 elif line.startswith("- "):  # Ligne contenant une stack technique
#                     stacks.append(line.replace("- ", "").strip())

#                 # Sauvegarde lorsque l'on change d'entreprise
#                 elif entreprise and status and stacks:
#                     data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks)])
#                     stacks = []

#             # Sauvegarde de la dernière entreprise rencontrée
#             if entreprise and status and stacks:
#                 data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks)])

#         except Exception as e:
#             print(f"❌ Erreur lors du traitement de {pdf_file} : {e}")

#         # Pause pour éviter de surcharger l'API
#         time.sleep(1)

#     # Génération du fichier Excel avec les données extraites
#     print("📊 Génération du fichier Excel...")

#     df = pd.DataFrame(data, columns=["Nom", "Entreprise", "Status", "ESN", "Stacks Techniques"])

#     # Sauvegarde en Excel (ajout de nouvelles données si le fichier existe)
#     if os.path.exists(excel_path):
#         df_existing = pd.read_excel(excel_path)
#         df = pd.concat([df_existing, df], ignore_index=True)

#     df.to_excel(excel_path, index=False)

#     print(f"🎉 Fichier Excel mis à jour : {excel_path}")


# if __name__ == "__main__":
#     process_pdf_files()


### MIGRATION VERS FOLDERS DRIVE ###


# import os
# import pandas as pd
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from dotenv import load_dotenv
# from langchain_mistralai import ChatMistralAI
# from PyPDF2 import PdfReader
# import io
# import pickle

# load_dotenv()
# google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# input_folder_id = os.getenv('INPUT_FOLDER_ID')
# output_folder_id = os.getenv('OUTPUT_FOLDER_ID')
# archive_folder_id = os.getenv('ARCHIVE_FOLDER_ID')

# # Scopes pour l'accès Google Drive
# SCOPES = ['https://www.googleapis.com/auth/drive.file']  

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

#     drive_service = build('drive', 'v3', credentials=creds)
#     return drive_service

# def download_file_from_drive(drive_service, file_id, local_path):
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.FileIO(local_path, 'wb')
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while done is False:
#         status, done = downloader.next_chunk()
#     print(f"Fichier téléchargé: {local_path}")

# def upload_file_to_drive(drive_service, local_file_path, folder_id, mime_type="application/vnd.ms-excel"):
#     file_metadata = {
#         'name': os.path.basename(local_file_path),
#         'parents': [folder_id]
#     }
#     media = MediaIoBaseUpload(io.FileIO(local_file_path, 'rb'), mimetype=mime_type)
#     file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     print(f"Fichier téléchargé sur Drive : id : {file['id']}")
#     return file['id']

# def get_pdf_text(pdf_path):
#     """Extrait le texte d'un fichier PDF."""
#     text = ""
#     pdf_reader = PdfReader(pdf_path)
#     for page in pdf_reader.pages:
#         extracted_text = page.extract_text()
#         if extracted_text:
#             text += extracted_text + "\n"
#     return text.strip()

# ##############
# def get_existing_excel_from_drive(drive_service, file_name, folder_id, local_path):
#     query = f"'{folder_id}' in parents and name='{file_name}' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' and trashed=false"
#     results = drive_service.files().list(q=query, fields="files(id, name)").execute()
#     files = results.get('files', [])
    
#     if not files:
#         return None  # Le fichier n'existe pas encore

#     file_id = files[0]['id']
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.FileIO(local_path, 'wb')
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         _, done = downloader.next_chunk()
#     return file_id

# ##########

# def process_pdf_files():
#     llm = ChatMistralAI(model='mistral-large-latest', temperature=0)

#     drive_service = authenticate_google_drive()

#     results = drive_service.files().list(q=f"'{input_folder_id}' in parents and mimeType='application/pdf' and trashed=false", 
#                                          fields="files(id, name)").execute()
#     files = results.get('files', [])

#     if not files:
#         print("Aucun fichier PDF trouvé dans le dossier d'entrée.")
#         return

    
#     data = []

#     for file in files:
#         file_id = file['id']
#         file_name = file['name']
#         local_pdf_path = f'/tmp/{file_name}'

#         print(f"📄 Traitement du fichier : {file_name}")

        
#         download_file_from_drive(drive_service, file_id, local_pdf_path)

#         text = get_pdf_text(local_pdf_path)

#         if not text:
#             print(f"⚠️ Aucun texte extrait du fichier {file_name}.")
#             continue

#         message = [
#             ("system", """Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
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
#             ("human", text)
#         ]

#         try:
#             ai_msg = llm.invoke(message)
#             extracted_text = ai_msg.content

#             local_txt_path = f'/tmp/{file_name.replace(".pdf", ".txt")}'
#             with open(local_txt_path, "w", encoding="utf-8") as f:
#                 f.write(extracted_text)

#             upload_file_to_drive(drive_service, local_txt_path, output_folder_id, mime_type="text/plain")

#             excel_path = '/tmp/resultats.xlsx'
#             df = pd.DataFrame([["Nom", "Entreprise", "Status", "ESN", "Stacks"]])  
#             df.to_excel(excel_path, index=False)

#             upload_file_to_drive(drive_service, excel_path, output_folder_id)

#             drive_service.files().update(fileId=file_id, addParents=archive_folder_id, removeParents=input_folder_id).execute()
#             print(f"📦 PDF déplacé vers l'archive: {file_name}")

#         except Exception as e:
#             print(f"❌ Erreur lors du traitement de {file_name}: {e}")

# ############## modif nejoujou
#         print('📊 Mise à jour du fichier Excel')

#         # Fichier Excel temporaire
#         excel_path = '/tmp/resultats.xlsx'
#         file_name = 'resultats.xlsx'

#         # Télécharger l'excel existant s’il y en a un
#         existing_file_id = get_existing_excel_from_drive(drive_service, file_name, output_folder_id, excel_path)

#         # Charger l'existant s'il y en a
#         if os.path.exists(excel_path):
#             df_existing = pd.read_excel(excel_path)
#         else:
#             df_existing = pd.DataFrame(columns=["Nom","Entreprise","status","ESN","Stacks Techniques"])

#         # Ajouter les nouvelles données
#         df_new = pd.DataFrame(data, columns=["Nom","Entreprise","status","ESN","Stacks Techniques"])
#         df_combined = pd.concat([df_existing, df_new], ignore_index=True)

#         # Réécrire le fichier mis à jour
#         df_combined.to_excel(excel_path, index=False)

#         # Supprimer l'ancien fichier sur Google Drive s’il existe
#         if existing_file_id:
#             drive_service.files().delete(fileId=existing_file_id).execute()

#         # Uploader la nouvelle version
#         upload_file_to_drive(drive_service, excel_path, output_folder_id,
#                              mime_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

#         print(f'✅ Fichier Excel mis à jour et réuploadé sur Google Drive : {file_name}')


# ##############             

#         os.remove(local_pdf_path)
#         os.remove(local_txt_path)

# if __name__ == "__main__":
#     process_pdf_files()



###### chatou 30/04

# from googleapiclient.http import MediaIoBaseDownload
# import io
# import os
# import time
# from dotenv import load_dotenv
# import pandas as pd
# from langchain_mistralai import ChatMistralAI
# from auth_utils import get_drive_service, download_pdf_files, upload_text_to_drive, save_excel_to_drive

# load_dotenv()
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
# project_path = os.getenv('PROJECT_PATH')

# def get_pdf_text(pdf_path):
#     """Extrait le texte d'un fichier PDF."""
#     from PyPDF2 import PdfReader
#     text = ""
#     pdf_reader = PdfReader(pdf_path)
#     for page in pdf_reader.pages:
#         extracted_text = page.extract_text()
#         if extracted_text:
#             text += extracted_text + "\n"
#     return text.strip()

# def process_pdf_files(service):
#     """Processus principal pour traiter les fichiers PDF et extraire les données."""
#     llm = ChatMistralAI(model='mistral-large-latest', temperature=0)

#     # Récupérer les fichiers PDF depuis Google Drive
#     input_folder_id = os.getenv("INPUT_FOLDER_ID")
#     pdf_files = download_pdf_files(service, input_folder_id)

#     data = []

#     for pdf_file in pdf_files:
#         print(f"📄 Traitement du fichier : {pdf_file['name']}")

#         # Extraire le texte du PDF
#         text = get_pdf_text(pdf_file['path'])

#         if not text:
#             print(f"⚠️ Aucun texte extrait du fichier {pdf_file['name']}")
#             continue

#         message = [
#             ("system", """Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
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
#             ("human", text)
#         ]

#         try:
#             # Appel au modèle IA
#             ai_msg = llm.invoke(message)
#             text_brute = ai_msg.content

#             # Sauvegarde du texte brut sur Google Drive
#             output_file_id = upload_text_to_drive(service, text_brute, pdf_file['name'])

#             # Traitement du texte brut pour extraire les données structurées
#             lines = text_brute.split("\n")
#             nom_candidat = ""
#             entreprise = ""
#             status = ""
#             esn_nom = "-"
#             stacks = []

#             for i, line in enumerate(lines):
#                 line = line.strip()
                
#                 if line.startswith("**Nom du Candidat**"):
#                     nom_candidat = lines[i + 1].strip() if i + 1 < len(lines) else ""
                
#                 elif line.startswith("**Entreprise ESN**"):
#                     entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
#                     status = "ESN"
#                     esn_nom = "-"
                
#                 elif line.startswith("**Client ESN :"):
#                     parts = line.replace("**Client ESN :", "").replace("**", "").strip().split("(ESN :")
#                     entreprise = parts[0].strip()
#                     esn_nom = parts[1].replace(")", "").strip() if len(parts) > 1 else "-"
#                     status = "Client ESN"
                
#                 elif line.startswith("**Entreprise classique**"):
#                     entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
#                     status = "Entreprise Classique"
#                     esn_nom = "-"
                
#                 elif line.startswith("- "):  # Ligne contenant une stack technique
#                     stacks.append(line.replace("- ", "").strip())

#                 # Sauvegarde lorsque l'on change d'entreprise
#                 elif entreprise and status and stacks:
#                     data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks)])
#                     stacks = []

#             # Sauvegarde de la dernière entreprise rencontrée
#             if entreprise and status and stacks:
#                 data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks)])

#         except Exception as e:
#             print(f"❌ Erreur lors du traitement de {pdf_file['name']} : {e}")

#         # Pause pour éviter de surcharger l'API
#         time.sleep(1)

#     # Gérer l'export dans un fichier Excel sur Google Drive
#     save_excel_to_drive(service, data)

# def download_pdf_files(service, folder_id):
#     """Télécharge les fichiers PDF depuis un dossier spécifique sur Google Drive."""
#     query = f"'{folder_id}' in parents and mimeType = 'application/pdf'"
#     results = service.files().list(q=query, fields="files(id, name)").execute()
#     files = results.get('files', [])

#     pdf_files = []
#     for file in files:
#         file_id = file['id']
#         file_name = file['name']
        
#         # Télécharger le fichier PDF
#         request = service.files().get_media(fileId=file_id)
#         fh = io.FileIO(f"/tmp/{file_name}", 'wb')
#         downloader = MediaIoBaseDownload(fh, request)
#         done = False
#         while not done:
#             status, done = downloader.next_chunk()

#         pdf_files.append({
#             'id': file_id,
#             'name': file_name,
#             'path': f"/tmp/{file_name}"
#         })

#     return pdf_files

# if __name__ == "__main__":
#     service = get_drive_service()
#     process_pdf_files(service)




# from PyPDF2 import PdfReader
# import os
# from dotenv import load_dotenv
# import time
# import io
# import pickle
# import pandas as pd
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload,MediaIoBaseDownload
# # from google.auth import Credentials  # Correction ici
# from google.auth.transport.requests import Request  # Cette ligne reste inchangée
# import os
# import pandas as pd
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from dotenv import load_dotenv
# from langchain_mistralai import ChatMistralAI
# from PyPDF2 import PdfReader
# import io
# import pickle


# load_dotenv()
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
# PROJECT_PATH = os.getenv('PROJECT_PATH')
# INPUT_FOLDER_ID = os.getenv("INPUT_FOLDER_ID")
# OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")
# TOKEN_PATH = os.getenv("TOKEN_PATH")
# CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# def get_drive_service():
#     """Récupère un service Google Drive authentifié."""
#     creds = None
#     if os.path.exists(TOKEN_PATH):
#         with open(TOKEN_PATH, 'rb') as token:
#             creds = pickle.load(token)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             from google_auth_oauthlib.flow import InstalledAppFlow
#             flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, ['https://www.googleapis.com/auth/drive'])
#             creds = flow.run_local_server(port=0)
#         with open(TOKEN_PATH, 'wb') as token:
#             pickle.dump(creds, token)
#     return build('drive', 'v3', credentials=creds)

# def download_file(service, file_id):
#     """Télécharge un fichier depuis Google Drive"""
#     request = service.files().get_media(fileId=file_id)
#     file_path = "/tmp/temp_file.pdf"
#     fh = io.FileIO(file_path, 'wb')
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         status, done = downloader.next_chunk()
#     return file_path

# def upload_file_to_drive(service, file_path, folder_id, file_name):
#     """Téléverse un fichier sur Google Drive."""
#     media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     file_metadata = {'name': file_name, 'parents': [folder_id]}
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     return file['id']

# def get_files_in_folder(service, folder_id):
#     """Récupère les fichiers dans un dossier Google Drive."""
#     query = f"'{folder_id}' in parents and mimeType = 'application/pdf'"
#     results = service.files().list(q=query, fields="files(id, name)").execute()
#     return results.get('files', [])

# def get_pdf_text(pdf_path):
#     """Extrait le texte d'un fichier PDF."""
#     text = ""
#     pdf_reader = PdfReader(pdf_path)
#     for page in pdf_reader.pages:
#         extracted_text = page.extract_text()
#         if extracted_text:
#             text += extracted_text + "\n"
#     return text.strip()

# def process_pdf_files():
#     """Processus principal pour traiter les fichiers PDF et extraire les données."""
#     service = get_drive_service()

#     # Récupérer les fichiers PDF depuis Google Drive
#     pdf_files = get_files_in_folder(service, INPUT_FOLDER_ID)

#     if not pdf_files:
#         print("❌ Aucun fichier PDF trouvé dans le dossier Drive.")
#         return

#     data = []
#     for pdf in pdf_files:
#         pdf_id = pdf['id']
#         pdf_name = pdf['name']
#         print(f"📄 Traitement du fichier : {pdf_name}")
        
#         # Télécharger le fichier PDF
#         pdf_path = download_file(service, pdf_id)

#         # Extraire le texte du PDF
#         text = get_pdf_text(pdf_path)
#         if not text:
#             print(f"⚠️ Aucun texte extrait du fichier {pdf_name}.")
#             continue

#         # Traitement du texte (comme dans ton script)
#         # (ton code de traitement avec ChatMistralAI ici)
#         # Exemple : message = llm.invoke(...)

#         # Sauvegarde du texte dans un fichier (ici en local, à adapter si nécessaire)
#         output_file = f"/tmp/output_{pdf_name.replace('.pdf', '.txt')}"
#         with open(output_file, "w", encoding="utf-8") as f:
#             f.write(text)

#         # Sauvegarde dans Google Drive (fichier de sortie)
#         upload_file_to_drive(service, output_file, OUTPUT_FOLDER_ID, f"processed_{pdf_name}.txt")
#         print(f"✅ Fichier texte téléchargé sur Google Drive : {output_file}")

#         # (Traitement de données, ajout dans un DataFrame, etc.)

#     # Sauvegarder les résultats dans un Excel (upload sur Google Drive à adapter)
#     excel_path = "/tmp/resultats.xlsx"  # à ajuster si nécessaire
#     # DataFrame et sauvegarde en Excel ici
#     # upload_file_to_drive(service, excel_path, OUTPUT_FOLDER_ID, 'resultats.xlsx')

# if __name__ == "__main__":
#     process_pdf_files()



# from PyPDF2 import PdfReader
# import os
# from dotenv import load_dotenv
# import time
# import io
# import pickle
# import pandas as pd
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from langchain_mistralai import ChatMistralAI

# # Charger les variables d'environnement
# load_dotenv()
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
# PROJECT_PATH = os.getenv('PROJECT_PATH')
# INPUT_FOLDER_ID = os.getenv("INPUT_FOLDER_ID")
# OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")
# TOKEN_PATH = os.getenv("TOKEN_PATH")
# CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# def get_drive_service():
#     """Récupère un service Google Drive authentifié."""
#     creds = None
#     if os.path.exists(TOKEN_PATH):
#         with open(TOKEN_PATH, 'rb') as token:
#             creds = pickle.load(token)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, ['https://www.googleapis.com/auth/drive'])
#             creds = flow.run_local_server(port=0)
#         with open(TOKEN_PATH, 'wb') as token:
#             pickle.dump(creds, token)
#     return build('drive', 'v3', credentials=creds)

# def download_file(service, file_id):
#     """Télécharge un fichier depuis Google Drive."""
#     request = service.files().get_media(fileId=file_id)
#     file_path = "/tmp/temp_file.pdf"
#     fh = io.FileIO(file_path, 'wb')
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         status, done = downloader.next_chunk()
#     return file_path

# def upload_file_to_drive(service, file_path, folder_id, file_name):
#     """Téléverse un fichier sur Google Drive."""
#     media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     file_metadata = {'name': file_name, 'parents': [folder_id]}
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     return file['id']

# def get_files_in_folder(service, folder_id):
#     """Récupère les fichiers dans un dossier Google Drive."""
#     query = f"'{folder_id}' in parents and mimeType = 'application/pdf'"
#     results = service.files().list(q=query, fields="files(id, name)").execute()
#     return results.get('files', [])

# def get_pdf_text(pdf_path):
#     """Extrait le texte d'un fichier PDF."""
#     text = ""
#     pdf_reader = PdfReader(pdf_path)
#     for page in pdf_reader.pages:
#         extracted_text = page.extract_text()
#         if extracted_text:
#             text += extracted_text + "\n"
#     return text.strip()

# def process_pdf_files():
#     """Processus principal pour traiter les fichiers PDF et extraire les données."""
#     service = get_drive_service()

#     # Récupérer les fichiers PDF depuis Google Drive
#     pdf_files = get_files_in_folder(service, INPUT_FOLDER_ID)

#     if not pdf_files:
#         print("❌ Aucun fichier PDF trouvé dans le dossier Drive.")
#         return

#     data = []
#     llm = ChatMistralAI(model='mistral-large-latest', temperature=0)

#     for pdf in pdf_files:
#         pdf_id = pdf['id']
#         pdf_name = pdf['name']
#         print(f"📄 Traitement du fichier : {pdf_name}")
        
#         # Télécharger le fichier PDF
#         pdf_path = download_file(service, pdf_id)

#         # Extraire le texte du PDF
#         text = get_pdf_text(pdf_path)
#         if not text:
#             print(f"⚠️ Aucun texte extrait du fichier {pdf_name}.")
#             continue

#         # Traitement du texte avec ChatMistralAI
#         message = [
#             ("system",
#             """Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
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
#             """
#             ),
#             ("human", text)
#         ]
#         try:
#             # Appel au modèle IA pour obtenir la réponse
#             ai_msg = llm.invoke(message)
#             text_brute = ai_msg.content

#             # Sauvegarde du texte brut dans un fichier (ici en local, à adapter si nécessaire)
#             output_file = f"/tmp/output_{pdf_name.replace('.pdf', '.txt')}"
#             with open(output_file, "w", encoding="utf-8") as f:
#                 f.write(text_brute)

#             # Sauvegarde dans Google Drive (fichier de sortie)
#             upload_file_to_drive(service, output_file, OUTPUT_FOLDER_ID, f"processed_{pdf_name}.txt")
#             print(f"✅ Fichier texte téléchargé sur Google Drive : {output_file}")

#         except Exception as e:
#             print(f"❌ Erreur lors du traitement de {pdf_name} : {e}")

#     # Sauvegarder les résultats dans un Excel (upload sur Google Drive à adapter)
#     excel_path = "/tmp/resultats.xlsx"  # à ajuster si nécessaire
#     # Crée un DataFrame et sauvegarde en Excel
#     df = pd.DataFrame(data, columns=["Nom", "Entreprise", "Status", "ESN", "Stacks Techniques"])
#     df.to_excel(excel_path, index=False)

#     # Upload du fichier Excel sur Google Drive
#     upload_file_to_drive(service, excel_path, OUTPUT_FOLDER_ID, 'resultats.xlsx')
#     print("✅ Fichier Excel téléchargé sur Google Drive.")

# if __name__ == "__main__":
#     process_pdf_files()


# from PyPDF2 import PdfReader
# from io import BytesIO
# import os
# import pickle
# import time
# from langchain_mistralai import ChatMistralAI
# import pandas as pd
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload, MediaInMemoryUpload

# # Charger les variables d'environnement
# from dotenv import load_dotenv
# load_dotenv()

# # Configuration depuis .env
# CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# TOKEN_PICKLE = os.getenv("TOKEN_PATH")
# INPUT_FOLDER_ID = os.getenv("INPUT_FOLDER_ID")
# OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")

# SCOPES = ['https://www.googleapis.com/auth/drive']

# def authenticate_drive():
#     """Authentifie avec OAuth et sauvegarde/restaure le token en format pickle"""
#     creds = None
    
#     # Charger le token depuis le pickle si disponible
#     if os.path.exists(TOKEN_PICKLE):
#         with open(TOKEN_PICKLE, 'rb') as token:
#             try:
#                 creds = pickle.load(token)
#             except Exception as e:
#                 print(f"⚠️ Échec du chargement du token pickle : {e}")
    
#     # Rafraîchir ou générer un nouveau token si nécessaire
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             try:
#                 creds.refresh(Request())
#             except Exception as e:
#                 print(f"⚠️ Token expiré et impossible à rafraîchir : {e}")
#                 os.remove(TOKEN_PICKLE)
#                 return authenticate_drive()
#         else:
#             # Démarrer le flux OAuth
#             flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON, SCOPES)
#             creds = flow.run_local_server(port=0)
        
#         # Sauvegarder le nouveau token en pickle
#         with open(TOKEN_PICKLE, 'wb') as token:
#             pickle.dump(creds, token)
    
#     return build('drive', 'v3', credentials=creds)

# def get_pdf_files(drive_service):
#     """Récupère les PDFs dans un dossier Drive"""
#     query = f"'{INPUT_FOLDER_ID}' in parents and mimeType='application/pdf'"
#     results = drive_service.files().list(q=query, fields="files(id, name)").execute()
#     return results.get('files', [])

# def get_pdf_text(file_id, drive_service):
#     """Extrait le texte d'un PDF sur Google Drive"""
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
    
#     done = False
#     while not done:
#         status, done = downloader.next_chunk()
    
#     fh.seek(0)
#     text = ""
#     pdf_reader = PdfReader(fh)
    
#     for page in pdf_reader.pages:
#         extracted_text = page.extract_text()
#         if extracted_text:
#             text += extracted_text + "\n"
    
#     return text.strip()

# def upload_processed_result(content, filename, drive_service):
#     """Téléverse un fichier texte vers Google Drive"""
#     file_metadata = {
#         'name': filename,
#         'parents': [OUTPUT_FOLDER_ID]
#     }
#     media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/plain')
    
#     drive_service.files().create(
#         body=file_metadata,
#         media_body=media,
#         fields='id'
#     ).execute()

# def update_excel_sheet(df, drive_service):
#     """Met à jour ou crée un fichier Excel sur Google Drive"""
#     # Nom du fichier Excel final
#     sheet_name = "resultats.xlsx"
    
#     # Rechercher un fichier existant
#     query = f"name='{sheet_name}' and '{OUTPUT_FOLDER_ID}' in parents"
#     results = drive_service.files().list(q=query, fields="files(id)").execute()
#     files = results.get('files', [])
    
#     # Créer un buffer Excel
#     excel_buffer = BytesIO()
#     df.to_excel(excel_buffer, index=False)
    
#     # Mettre à jour ou créer le fichier
#     metadata = {
#         'name': sheet_name,
#         'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#         'parents': [OUTPUT_FOLDER_ID]
#     }
#     media = MediaInMemoryUpload(
#         excel_buffer.getvalue(),
#         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
    
#     if files:
#         # Mise à jour du fichier existant
#         drive_service.files().update(
#             fileId=files[0]['id'],
#             body=metadata,
#             media_body=media
#         ).execute()
#     else:
#         # Création d'un nouveau fichier
#         drive_service.files().create(
#             body=metadata,
#             media_body=media,
#             fields='id'
#         ).execute()

# def process_pdf_files():
#     """Processus principal"""
#     # Authentification
#     drive_service = authenticate_drive()
    
#     # Initialisation du modèle IA
#     llm = ChatMistralAI(model='mistral-large-latest', temperature=0)
    
#     # Récupérer tous les PDFs
#     pdf_files = get_pdf_files(drive_service)
    
#     if not pdf_files:
#         print("❌ Aucun PDF trouvé dans le dossier d'entrée !")
#         return
    
#     # Liste pour stocker les données extraites
#     data = []
    
#     # Traiter chaque PDF
#     for file in pdf_files:
#         print(f"\n📄 Traitement de {file['name']}")
        
#         try:
#             # Extraire le texte
#             text = get_pdf_text(file['id'], drive_service)
            
#             if not text:
#                 print(f"⚠️ Texte vide pour {file['name']}")
#                 continue
            
#             # Prompt système (identique au vôtre)
#             system_prompt = """
#             Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
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
#             """
            
#             message = [
#                 ("system", system_prompt),
#                 ("human", text)
#             ]
            
#             # Appel à Mistral
#             ai_msg = llm.invoke(message)
#             raw_output = ai_msg.content
            
#             # Téléverser le résultat brut
#             output_filename = f"output_{file['name'].replace('.pdf', '.txt')}"
#             upload_processed_result(raw_output, output_filename, drive_service)
#             print(f"✅ Résultat brut sauvegardé : {output_filename}")
            
#             # Extraction structurée (code inchangé)
#             # ... (votre logique d'extraction de données ici)
            
#         except Exception as e:
#             print(f"❌ Erreur lors du traitement de {file['name']} : {str(e)}")
        
#         time.sleep(1)  # Pour éviter les erreurs de quota API
    
#     # Générer et mettre à jour le fichier Excel final
#     if data:
#         df = pd.DataFrame(data, columns=["Nom", "Entreprise", "Status", "ESN", "Stacks Techniques"])
#         update_excel_sheet(df, drive_service)
#         print("✅ Fichier Excel mis à jour dans Google Drive")

# if __name__ == "__main__":
#     process_pdf_files()


# from PyPDF2 import PdfReader
# from io import BytesIO
# import os
# import pickle
# import time
# from langchain_mistralai import ChatMistralAI
# import pandas as pd
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload, MediaInMemoryUpload

# # Charger les variables d'environnement
# from dotenv import load_dotenv
# load_dotenv()

# # Configuration depuis .env
# CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# TOKEN_PICKLE = os.getenv("TOKEN_PATH")
# INPUT_FOLDER_ID = os.getenv("INPUT_FOLDER_ID")
# OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")

# SCOPES = ['https://www.googleapis.com/auth/drive']

# def authenticate_drive():
#     """Authentifie avec OAuth et sauvegarde/restaure le token en format pickle"""
#     creds = None
    
#     # Charger le token depuis le pickle si disponible
#     if os.path.exists(TOKEN_PICKLE):
#         with open(TOKEN_PICKLE, 'rb') as token:
#             try:
#                 creds = pickle.load(token)
#             except Exception as e:
#                 print(f"⚠️ Échec du chargement du token pickle : {e}")
    
#     # Rafraîchir ou générer un nouveau token si nécessaire
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             try:
#                 creds.refresh(Request())
#             except Exception as e:
#                 print(f"⚠️ Token expiré et impossible à rafraîchir : {e}")
#                 os.remove(TOKEN_PICKLE)
#                 return authenticate_drive()
#         else:
#             # Démarrer le flux OAuth
#             flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON, SCOPES)
#             creds = flow.run_local_server(port=0)
        
#         # Sauvegarder le nouveau token en pickle
#         with open(TOKEN_PICKLE, 'wb') as token:
#             pickle.dump(creds, token)
    
#     return build('drive', 'v3', credentials=creds)

# def get_pdf_files(drive_service):
#     """Récupère les PDFs dans un dossier Drive"""
#     query = f"'{INPUT_FOLDER_ID}' in parents and mimeType='application/pdf'"
#     results = drive_service.files().list(q=query, fields="files(id, name)").execute()
#     return results.get('files', [])

# def get_pdf_text(file_id, drive_service):
#     """Extrait le texte d'un PDF sur Google Drive"""
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
    
#     done = False
#     while not done:
#         status, done = downloader.next_chunk()
    
#     fh.seek(0)
#     text = ""
#     pdf_reader = PdfReader(fh)
    
#     for page in pdf_reader.pages:
#         extracted_text = page.extract_text()
#         if extracted_text:
#             text += extracted_text + "\n"
    
#     return text.strip()

# def upload_processed_result(content, filename, drive_service):
#     """Téléverse un fichier texte vers Google Drive"""
#     file_metadata = {
#         'name': filename,
#         'parents': [OUTPUT_FOLDER_ID]
#     }
#     media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/plain')
    
#     try:
#         drive_service.files().create(
#             body=file_metadata,
#             media_body=media,
#             fields='id'
#         ).execute()
#     except Exception as e:
#         print(f"❌ Échec du téléversement de {filename} : {e}")

# def upload_excel_to_drive(df, drive_service, sheet_name="resultats.xlsx"):
#     """Téléverse le DataFrame en Excel vers Google Drive"""
#     try:
#         print("📊 Préparation du fichier Excel en mémoire...")
#         excel_buffer = BytesIO()
#         df.to_excel(excel_buffer, index=False)
#         print("✅ DataFrame converti en Excel en mémoire")

#         # Rechercher si le fichier existe
#         query = f"name='{sheet_name}' and '{OUTPUT_FOLDER_ID}' in parents"
#         results = drive_service.files().list(q=query, fields="files(id, name)").execute()
#         files = results.get('files', [])
        
#         file_metadata = {
#             'name': sheet_name,
#             'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#             'parents': [OUTPUT_FOLDER_ID]
#         }

#         media_body = MediaInMemoryUpload(
#             excel_buffer.getvalue(),
#             mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         )

#         if files:
#             # Mise à jour du fichier existant
#             file_id = files[0]['id']
#             print(f"🔄 Mise à jour du fichier Excel (ID: {file_id})")
#             drive_service.files().update(
#                 fileId=file_id,
#                 body=file_metadata,
#                 media_body=media_body
#             ).execute()
#         else:
#             # Création d'un nouveau fichier
#             print(f"🆕 Création d’un nouveau fichier Excel : {sheet_name}")
#             drive_service.files().create(
#                 body=file_metadata,
#                 media_body=media_body,
#                 fields='id'
#             ).execute()

#         print("🎉 Fichier Excel mis à jour/sauvegardé sur Google Drive")

#     except Exception as e:
#         print(f"❌ Erreur lors de l’upload de l’Excel : {e}")

# def process_pdf_files():
#     """Processus principal"""
#     # Authentification
#     drive_service = authenticate_drive()
    
#     # Initialisation du modèle IA
#     llm = ChatMistralAI(model='mistral-large-latest', temperature=0)
    
#     # Récupérer tous les PDFs
#     pdf_files = get_pdf_files(drive_service)
    
#     if not pdf_files:
#         print("❌ Aucun PDF trouvé dans le dossier d'entrée !")
#         return
    
#     # Liste pour stocker les données extraites
#     data = []
    
#     # Traiter chaque PDF
#     for file in pdf_files:
#         print(f"\n📄 Traitement de {file['name']}")
        
#         try:
#             # Extraire le texte
#             text = get_pdf_text(file['id'], drive_service)
            
#             if not text:
#                 print(f"⚠️ Texte vide pour {file['name']}")
#                 continue
            
#             # Prompt système (identique au vôtre)
#             system_prompt = """
#             Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
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
#             """
            
#             message = [
#                 ("system", system_prompt),
#                 ("human", text)
#             ]
            
#             # Appel à Mistral
#             ai_msg = llm.invoke(message)
#             raw_output = ai_msg.content
            
#             # Téléverser le résultat brut
#             output_filename = f"output_{file['name'].replace('.pdf', '.txt')}"
#             upload_processed_result(raw_output, output_filename, drive_service)
#             print(f"✅ Résultat brut sauvegardé : {output_filename}")
            
#             # Extraction structurée (code inchangé)
#             lines = raw_output.split("\n")
#             nom_candidat = ""
#             entreprise = ""
#             status = ""
#             esn_nom = "-"
#             stacks = []

#             for i, line in enumerate(lines):
#                 line = line.strip()
                
#                 if line.startswith("**Nom du Candidat**"):
#                     nom_candidat = lines[i + 1].strip() if i + 1 < len(lines) else ""
                
#                 elif line.startswith("**Entreprise ESN**"):
#                     entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
#                     status = "ESN"
#                     esn_nom = "-"
                
#                 elif line.startswith("**Client ESN :"):
#                     parts = line.replace("**Client ESN :", "").replace("**", "").strip().split("(ESN :")
#                     entreprise = parts[0].strip()
#                     esn_nom = parts[1].replace(")", "").strip() if len(parts) > 1 else "-"
#                     status = "Client ESN"
                
#                 elif line.startswith("**Entreprise classique**"):
#                     entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
#                     status = "Entreprise Classique"
#                     esn_nom = "-"
                
#                 elif line.startswith("- "):  # Ligne contenant une stack technique
#                     stacks.append(line.replace("- ", "").strip())

#                 # Sauvegarde lorsque l'on change d'entreprise
#                 elif entreprise and status and stacks:
#                     data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks)])
#                     stacks = []

#             # Sauvegarde de la dernière entreprise rencontrée
#             if entreprise and status and stacks:
#                 data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks)])
            
#         except Exception as e:
#             print(f"❌ Erreur lors du traitement de {file['name']} : {str(e)}")
        
#         time.sleep(1)  # Pour éviter les erreurs de quota API
    
#     # Générer et mettre à jour le fichier Excel final
#     if data:
#         df = pd.DataFrame(data, columns=["Nom", "Entreprise", "Status", "ESN", "Stacks Techniques"])
#         print("📊 DataFrame généré avec succès !")
#         print(df.head())
#         upload_excel_to_drive(df, drive_service)
#         print("✅ Fichier Excel mis à jour dans Google Drive")
#     else:
#         print("❌ Aucune donnée à insérer dans l'Excel")

# if __name__ == "__main__":
#     process_pdf_files()


from PyPDF2 import PdfReader
from io import BytesIO
import os
import pickle
import time
from langchain_mistralai import ChatMistralAI
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaInMemoryUpload
from datetime import date
from datetime import datetime

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Configuration depuis .env
CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
TOKEN_PICKLE = os.getenv("TOKEN_PATH")
INPUT_FOLDER_ID = os.getenv("INPUT_FOLDER_ID")
OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_drive():
    """Authentifie avec OAuth et sauvegarde/restaure le token en format pickle"""
    creds = None
    
    # Charger le token depuis le pickle si disponible
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            try:
                creds = pickle.load(token)
            except Exception as e:
                print(f"⚠️ Échec du chargement du token pickle : {e}")
    
    # Rafraîchir ou générer un nouveau token si nécessaire
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ Token expiré et impossible à rafraîchir : {e}")
                os.remove(TOKEN_PICKLE)
                return authenticate_drive()
        else:
            # Démarrer le flux OAuth
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Sauvegarder le nouveau token en pickle
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)


# penser a enlever les fichiers en double
def get_pdf_files(drive_service):
    """Récupère les PDFs dans un dossier Drive"""
    query = f"'{INPUT_FOLDER_ID}' in parents and mimeType='application/pdf'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def get_pdf_text(file_id, drive_service):
    """Extrait le texte d'un PDF sur Google Drive"""
    request = drive_service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    fh.seek(0)
    text = ""
    pdf_reader = PdfReader(fh)
    
    for page in pdf_reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text + "\n"
    
    return text.strip()

def upload_processed_result(content, filename, drive_service):
    """Téléverse un fichier texte vers Google Drive (évite les doublons)"""
    output_folder_id = os.getenv("OUTPUT_FOLDER_ID")  # Récupère l'ID du dossier output
    
    # Vérifie si le fichier existe déjà (exclut les fichiers supprimés)
    query = f"name='{filename}' and '{output_folder_id}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])
    
    if files:
        # Mise à jour du fichier existant
        file_id = files[0]['id']
        print(f"🔄 Mise à jour du fichier {filename}")
        drive_service.files().update(
            fileId=file_id,
            media_body=MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/plain')
        ).execute()
    else:
        # Création d’un nouveau fichier
        print(f"🆕 Création du fichier {filename}")
        file_metadata = {
            'name': filename,
            'parents': [output_folder_id],
            'mimeType': 'text/plain'
        }
        drive_service.files().create(
            body=file_metadata,
            media_body=MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/plain'),
            fields='id'
        ).execute()        


def upload_excel_to_drive(df_new, drive_service, sheet_name="resultats.xlsx"):
    """Téléverse un fichier Excel mis à jour (append) sur Google Drive"""
    try:
        print("📊 Préparation du fichier Excel en mémoire...")
        excel_buffer = BytesIO()
        df_new.to_excel(excel_buffer, index=False)
        
        # Recherche du fichier existant (exclure les fichiers supprimés)
        query = f"name='{sheet_name}' and trashed=false and '{OUTPUT_FOLDER_ID}' in parents"
        print(f"🔍 Recherche du fichier : {sheet_name} dans le dossier output...")
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        # Initialiser le DataFrame final avec les nouvelles données
        df_final = df_new.copy()
        
        # Si le fichier existe, on lit son contenu et on fusionne
        if files:
            file_id = files[0]['id']
            print(f"🔄 Fichier existant trouvé (ID: {file_id}), téléchargement en cours...")

            # Télécharger le fichier Excel existant
            request = drive_service.files().get_media(fileId=file_id)
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # Charger le fichier Excel existant dans un DataFrame
            fh.seek(0)
            df_existing = pd.read_excel(fh)
            
            # Fusionner les données existantes avec les nouvelles (sans doublons)
            df_final = pd.concat([df_existing, df_new], ignore_index=True).drop_duplicates()
            print(f"✅ Données fusionnées : {len(df_existing)} lignes existantes + {len(df_new)} nouvelles")

        # Convertir le DataFrame fusionné en Excel en mémoire
        excel_buffer = BytesIO()
        df_final.to_excel(excel_buffer, index=False)

        # Préparer les métadonnées
        file_metadata = {
            'name': sheet_name,
            'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

        media_body = MediaInMemoryUpload(
            excel_buffer.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        if files:
            # Mise à jour du contenu du fichier existant
            file_id = files[0]['id']
            print(f"🔄 Mise à jour du fichier Excel (ID: {file_id})")
            drive_service.files().update(
                fileId=file_id,
                body=file_metadata,
                media_body=media_body
            ).execute()
        else:
            # Création du fichier dans le dossier output
            print(f"🆕 Création d’un nouveau fichier Excel : {sheet_name}")
            file_metadata['parents'] = [OUTPUT_FOLDER_ID]
            drive_service.files().create(
                body=file_metadata,
                media_body=media_body,
                fields='id'
            ).execute()

        print("🎉 Fichier Excel mis à jour/sauvegardé sur Google Drive")

    except Exception as e:
        print(f"❌ Erreur lors de l’upload de l’Excel : {e}")

def process_pdf_files():
    """Processus principal"""
    # Authentification
    drive_service = authenticate_drive()
    
    # Initialisation du modèle IA
    llm = ChatMistralAI(model='mistral-large-latest', temperature=0)
    
    # Récupérer tous les PDFs
    pdf_files = get_pdf_files(drive_service)
    
    if not pdf_files:
        print("❌ Aucun PDF trouvé dans le dossier d'entrée !")
        return
    
    # Liste pour stocker les données extraites
    data = []
    
    # Traiter chaque PDF
    for file in pdf_files:
        print(f"\n📄 Traitement de {file['name']}")
        
        try:
            # Extraire le texte
            text = get_pdf_text(file['id'], drive_service)
            
            if not text:
                print(f"⚠️ Texte vide pour {file['name']}")
                continue
            
            # Prompt système (identique au vôtre)
            system_prompt = """
            Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
            Ton objectif est d'extraire **de manière fidèle** les informations suivantes, **sans modifier ni interpréter** les données d'origine :

            ### **Informations à extraire :**
            1. **Nom du candidat**  
            2. **Les entreprises dans lesquelles la personne a travaillé** et leur classification :
               - Si c'est une **ESN**, indique-le clairement et liste ses clients.
               - Si c'est une **entreprise classique**, indique-le clairement également.

            3. **Les technologies utilisées** :
               - Associe chaque entreprise (ou client d'ESN) aux stacks techniques mentionnées dans le texte.
               - **Ne jamais inventer ou omettre une technologie** : si ce n’est pas précisé dans le texte, ne l'ajoute pas.

            4. **Si un client ESN est mentionné, précise à quelle ESN il est rattaché.**

            ### **Format de sortie attendu (exemple) :**
            
            ----
            **Nom du Candidat**  
            [Nom du candidat]  

            **Entreprise ESN**  
            [Nom de l'ESN]  

            **Client ESN : [Nom du client]** (ESN : [Nom de l'ESN])  
            - Technologie 1  
            - Technologie 2  

            **Client ESN : [Nom du client]** (ESN : [Nom de l'ESN])  
            - Technologie 3  
            - Technologie 4  

            ---
            **Entreprise classique**  
            [Nom de l'entreprise]  
            - Technologie 1  
            - Technologie 2  
            
            ----
            """
            
            message = [
                ("system", system_prompt),
                ("human", text)
            ]
            
            # Appel à Mistral
            ai_msg = llm.invoke(message)
            raw_output = ai_msg.content
            
            # Téléverser le résultat brut
            output_filename = f"output_{file['name'].replace('.pdf', '.txt')}"
            upload_processed_result(raw_output, output_filename, drive_service)
            print(f"✅ Résultat brut sauvegardé : {output_filename}")
            
            # Extraction structurée (code inchangé)
            lines = raw_output.split("\n")
            nom_candidat = ""
            entreprise = ""
            status = ""
            esn_nom = "-"
            stacks = []
            # date_ingestion = date.today().isoformat()  
            date_ingestion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for i, line in enumerate(lines):
                line = line.strip()
                
                if line.startswith("**Nom du Candidat**"):
                    nom_candidat = lines[i + 1].strip() if i + 1 < len(lines) else ""
                
                elif line.startswith("**Entreprise ESN**"):
                    entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
                    status = "ESN"
                    esn_nom = "-"
                
                elif line.startswith("**Client ESN :"):
                    parts = line.replace("**Client ESN :", "").replace("**", "").strip().split("(ESN :")
                    entreprise = parts[0].strip()
                    esn_nom = parts[1].replace(")", "").strip() if len(parts) > 1 else "-"
                    status = "Client ESN"
                
                elif line.startswith("**Entreprise classique**"):
                    entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
                    status = "Entreprise Classique"
                    esn_nom = "-"
                
                elif line.startswith("- "):  # Ligne contenant une stack technique
                    stacks.append(line.replace("- ", "").strip())

                # Sauvegarde lorsque l'on change d'entreprise
                elif entreprise and status and stacks:
                    data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks), date_ingestion]) ##
                    stacks = []

            # Sauvegarde de la dernière entreprise rencontrée
            if entreprise and status and stacks:
                data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks), date_ingestion]) ##
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {file['name']} : {str(e)}")
        
        time.sleep(1)  # Pour éviter les erreurs de quota API
    
    # Générer et mettre à jour le fichier Excel final
    if data:
        df = pd.DataFrame(data, columns=["Nom", "Entreprise", "Status", "ESN", "Stacks Techniques","date_ingestion"])
        # df["Date Ingestion"] = date.today().isoformat() ##
        print("📊 DataFrame généré avec succès !")
        print(df.head())
        upload_excel_to_drive(df, drive_service)
        print("✅ Fichier Excel mis à jour dans Google Drive")
    else:
        print("❌ Aucune donnée à insérer dans l'Excel")

if __name__ == "__main__":
    process_pdf_files()