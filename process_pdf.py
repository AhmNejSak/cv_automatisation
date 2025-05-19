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