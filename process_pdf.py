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


import os
import time
import shutil
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from PyPDF2 import PdfReader
import io
import pickle

load_dotenv()

# Charger les informations de l'environnement
google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
input_folder_id = os.getenv('INPUT_FOLDER_ID')
output_folder_id = os.getenv('OUTPUT_FOLDER_ID')
archive_folder_id = os.getenv('ARCHIVE_FOLDER_ID')

# Scopes pour l'accès Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Accès aux fichiers

# Authentification avec OAuth 2.0
def authenticate_google_drive():
    creds = None
    # Le fichier token.pickle stocke les credentials d'accès de l'utilisateur
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Si les credentials sont invalides, refaire le processus d'authentification
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(google_credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Sauvegarder les credentials dans token.pickle pour les prochaines exécutions
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Créer le service Google Drive
    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service

# Télécharger un fichier depuis Google Drive
def download_file_from_drive(drive_service, file_id, local_path):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(local_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    print(f"Fichier téléchargé: {local_path}")

# Upload du fichier vers Google Drive
def upload_file_to_drive(drive_service, local_file_path, folder_id, mime_type="application/vnd.ms-excel"):
    file_metadata = {
        'name': os.path.basename(local_file_path),
        'parents': [folder_id]
    }
    media = MediaIoBaseUpload(io.FileIO(local_file_path, 'rb'), mimetype=mime_type)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Fichier téléchargé sur Drive : {file['id']}")
    return file['id']

# Extraire le texte d'un fichier PDF
def get_pdf_text(pdf_path):
    """Extrait le texte d'un fichier PDF."""
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text + "\n"
    return text.strip()

# Processus principal pour traiter les fichiers PDF et extraire les données
def process_pdf_files():
    # Initialisation du modèle IA
    llm = ChatMistralAI(model='mistral-large-latest', temperature=0)

    # Authentification Google Drive
    drive_service = authenticate_google_drive()

    # Récupérer la liste des fichiers PDF dans le dossier d'entrée sur Drive
    results = drive_service.files().list(q=f"'{input_folder_id}' in parents and mimeType='application/pdf' and trashed=false", 
                                         fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("Aucun fichier PDF trouvé dans le dossier d'entrée.")
        return

    # Liste pour stocker les résultats extraits des fichiers
    data = []

    # Pour chaque fichier PDF dans le dossier d'entrée
    for file in files:
        file_id = file['id']
        file_name = file['name']
        local_pdf_path = f'/tmp/{file_name}'

        print(f"📄 Traitement du fichier : {file_name}")

        # Télécharger le PDF depuis Google Drive vers un dossier temporaire local
        download_file_from_drive(drive_service, file_id, local_pdf_path)

        # Extraire le texte du fichier PDF
        text = get_pdf_text(local_pdf_path)

        if not text:
            print(f"⚠️ Aucun texte extrait du fichier {file_name}.")
            continue

        # Construction du message pour l'IA
        message = [
            ("system", """Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
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
            """),
            ("human", text)
        ]

        try:
            # Appel à l'API Mistral pour obtenir la réponse
            ai_msg = llm.invoke(message)
            extracted_text = ai_msg.content

            # Sauvegarder le texte brut dans un fichier .txt
            local_txt_path = f'/tmp/{file_name.replace(".pdf", ".txt")}'
            with open(local_txt_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)

            # Sauvegarder les fichiers traités (txt et xlsx) dans le dossier output
            upload_file_to_drive(drive_service, local_txt_path, output_folder_id, mime_type="text/plain")

            # Génération ou mise à jour du fichier Excel (si nécessaire)
            excel_path = '/tmp/resultats.xlsx'
            df = pd.DataFrame([["Nom", "Entreprise", "Status", "ESN", "Stacks"]])  # Simuler un traitement pour excel
            df.to_excel(excel_path, index=False)

            upload_file_to_drive(drive_service, excel_path, output_folder_id)

            # Déplacer le PDF traité vers le dossier d'archive sur Drive
            drive_service.files().update(fileId=file_id, addParents=archive_folder_id, removeParents=input_folder_id).execute()
            print(f"📦 PDF déplacé vers l'archive: {file_name}")

        except Exception as e:
            print(f"❌ Erreur lors du traitement de {file_name}: {e}")

        # Supprimer les fichiers locaux temporaires
        os.remove(local_pdf_path)
        os.remove(local_txt_path)

if __name__ == "__main__":
    process_pdf_files()