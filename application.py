# # app.py
# import streamlit as st
# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build
# import subprocess

# # Constantes (ou mieux: récupérées avec dotenv si tu préfères)
# SCOPES = ['https://www.googleapis.com/auth/drive']
# TOKEN_PATH = os.getenv("TOKEN_PATH")
# CREDENTIALS_PATH = os.getenv("CREDENTIALS_OAUTH_PATH")

# st.set_page_config(page_title="PDF Workflow App", page_icon="📄")

# st.title("📄 Application de traitement PDF (Google Drive)")

# # --- Étape 1 : Vérification / génération du token ---
# def check_or_generate_token():
#     creds = None

#     # Token existe ?
#     if os.path.exists(TOKEN_PATH):
#         with open(TOKEN_PATH, 'rb') as token:
#             creds = pickle.load(token)

#     # Token valide ?
#     if creds and creds.valid:
#         return True

#     # Token expiré mais renouvelable
#     if creds and creds.expired and creds.refresh_token:
#         try:
#             creds.refresh(Request())
#             with open(TOKEN_PATH, 'wb') as token:
#                 pickle.dump(creds, token)
#             return True
#         except Exception as e:
#             st.warning(f"Erreur lors du rafraîchissement : {e}")
#             os.remove(TOKEN_PATH)

#     # Aucun token valide → authentification manuelle
#     st.info("Veuillez autoriser l'accès à Google Drive via votre compte Google...")
#     try:
#         flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
#         creds = flow.run_local_server(port=0)
#         with open(TOKEN_PATH, 'wb') as token:
#             pickle.dump(creds, token)
#         return True
#     except Exception as e:
#         st.error(f"Erreur lors de l'authentification : {e}")
#         return False

# # Bouton pour vérifier le token
# if st.button("🔑 Vérifier ou générer le token Google Drive"):
#     if check_or_generate_token():
#         st.success("✅ Token valide. Vous pouvez maintenant lancer le workflow.")
#     else:
#         st.error("❌ Impossible de valider ou de générer le token.")

# # --- Étape 2 : Exécution du workflow complet ---
# if os.path.exists(TOKEN_PATH):
#     st.divider()
#     st.subheader("🚀 Lancement du workflow")

#     if st.button("▶️ Lancer le workflow complet"):
#         try:
#             st.info("📥 Étape 1 : Téléchargement des fichiers PDF...")
#             subprocess.run(["python3", "download_from_drive.py"], check=True)

#             st.info("⚙️ Étape 2 : Traitement des fichiers...")
#             subprocess.run(["bash", "wrapper_script.sh"], check=True)

#             st.info("📦 Étape 3 : Archivage des fichiers...")
#             subprocess.run(["python3", "move_processed_files.py"], check=True)

#             st.info("🧹 Étape 4 : Nettoyage du fichier Excel...")
#             subprocess.run(["python3", "clean_output.py"], check=True)

#             st.success("✅ Workflow exécuté avec succès !")

#         except subprocess.CalledProcessError as e:
#             st.error(f"❌ Une erreur est survenue pendant le workflow : {e}")
# else:
#     st.warning("Veuillez d'abord générer un token valide avant de lancer le workflow.")


# import streamlit as st
# import os
# import pickle
# import subprocess
# from auth_utils import get_drive_service, download_pdf_files, upload_excel_file, move_files_to_archive
# import time

# # Constantes (ou mieux: récupérées avec dotenv si tu préfères)
# SCOPES = ['https://www.googleapis.com/auth/drive']
# TOKEN_PATH = os.getenv("TOKEN_PATH")
# CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# st.set_page_config(page_title="PDF Workflow App", page_icon="📄")

# st.title("📄 Application de traitement PDF (Google Drive)")

# # --- Étape 1 : Vérification / génération du token ---
# def check_or_generate_token():
#     creds = None

#     # Token existe ?
#     if os.path.exists(TOKEN_PATH):
#         with open(TOKEN_PATH, 'rb') as token:
#             creds = pickle.load(token)

#     # Token valide ?
#     if creds and creds.valid:
#         return True

#     # Token expiré mais renouvelable
#     if creds and creds.expired and creds.refresh_token:
#         try:
#             creds.refresh(Request())
#             with open(TOKEN_PATH, 'wb') as token:
#                 pickle.dump(creds, token)
#             return True
#         except Exception as e:
#             st.warning(f"Erreur lors du rafraîchissement : {e}")
#             os.remove(TOKEN_PATH)

#     # Aucun token valide → authentification manuelle
#     st.info("Veuillez autoriser l'accès à Google Drive via votre compte Google...")
#     try:
#         flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
#         creds = flow.run_local_server(port=0)
#         with open(TOKEN_PATH, 'wb') as token:
#             pickle.dump(creds, token)
#         return True
#     except Exception as e:
#         st.error(f"Erreur lors de l'authentification : {e}")
#         return False

# # Bouton pour vérifier le token
# if st.button("🔑 Vérifier ou générer le token Google Drive"):
#     if check_or_generate_token():
#         st.success("✅ Token valide. Vous pouvez maintenant lancer le workflow.")
#     else:
#         st.error("❌ Impossible de valider ou de générer le token.")

# # --- Étape 2 : Exécution du workflow complet ---
# if os.path.exists(TOKEN_PATH):
#     st.divider()
#     st.subheader("🚀 Lancement du workflow")

#     if st.button("▶️ Lancer le workflow complet"):
#         try:
#             st.info("📥 Étape 1 : Téléchargement des fichiers PDF depuis Google Drive...")
#             service = get_drive_service()
#             pdf_files = download_pdf_files(service)

#             if pdf_files:
#                 st.success(f"✅ {len(pdf_files)} fichiers PDF téléchargés.")
#             else:
#                 st.warning("❌ Aucun fichier PDF trouvé dans Google Drive.")

#             st.info("⚙️ Étape 2 : Traitement des fichiers PDF...")
#             # Appeler ta fonction de traitement PDF ici, en local ou dans ton code Streamlit
#             # Exemple: process_pdf_files(pdf_files)
#             # ...

#             st.info("📦 Étape 3 : Téléversement du fichier Excel sur Google Drive...")
#             excel_path = os.path.join(os.getenv("PROJECT_PATH"), "output", "resultats.xlsx")
#             if os.path.exists(excel_path):
#                 upload_excel_file(service, excel_path)
#                 st.success("✅ Fichier Excel téléversé sur Google Drive.")
#             else:
#                 st.warning("❌ Fichier Excel non trouvé, assurez-vous que le traitement PDF a généré le fichier.")

#             st.info("🗂️ Étape 4 : Archivage des fichiers traités sur Google Drive...")
#             file_ids = [file.split('/')[-1] for file in pdf_files]  # Tu peux ajuster la logique ici
#             move_files_to_archive(service, file_ids)

#             st.success("✅ Workflow exécuté avec succès !")

#         except Exception as e:
#             st.error(f"❌ Une erreur est survenue pendant le workflow : {e}")
# else:
#     st.warning("Veuillez d'abord générer un token valide avant de lancer le workflow.")



# import streamlit as st
# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from auth_utils import get_drive_service, download_file, upload_file_to_drive, move_files_to_archive
# import time

# # Constantes (ou mieux: récupérées avec dotenv si tu préfères)
# SCOPES = ['https://www.googleapis.com/auth/drive']
# TOKEN_PATH = os.getenv("TOKEN_PATH")
# CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# st.set_page_config(page_title="PDF Workflow App", page_icon="📄")

# st.title("📄 Application de traitement PDF (Google Drive)")

# # --- Étape 1 : Vérification / génération du token ---
# def check_or_generate_token():
#     creds = None

#     # Token existe ?
#     if os.path.exists(TOKEN_PATH):
#         with open(TOKEN_PATH, 'rb') as token:
#             creds = pickle.load(token)

#     # Token valide ?
#     if creds and creds.valid:
#         return creds

#     # Token expiré mais renouvelable
#     if creds and creds.expired and creds.refresh_token:
#         try:
#             creds.refresh(Request())
#             with open(TOKEN_PATH, 'wb') as token:
#                 pickle.dump(creds, token)
#             return creds
#         except Exception as e:
#             st.warning(f"Erreur lors du rafraîchissement : {e}")
#             os.remove(TOKEN_PATH)

#     # Aucun token valide → authentification manuelle
#     st.info("Veuillez autoriser l'accès à Google Drive via votre compte Google...")
#     try:
#         flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
#         creds = flow.run_local_server(port=0)
#         with open(TOKEN_PATH, 'wb') as token:
#             pickle.dump(creds, token)
#         return creds
#     except Exception as e:
#         st.error(f"Erreur lors de l'authentification : {e}")
#         return None

# # Bouton pour vérifier le token
# if st.button("🔑 Vérifier ou générer le token Google Drive"):
#     creds = check_or_generate_token()
#     if creds:
#         st.success("✅ Token valide. Vous pouvez maintenant lancer le workflow.")
#     else:
#         st.error("❌ Impossible de valider ou de générer le token.")

# # --- Étape 2 : Exécution du workflow complet ---
# if os.path.exists(TOKEN_PATH):
#     st.divider()
#     st.subheader("🚀 Lancement du workflow")

#     if st.button("▶️ Lancer le workflow complet"):
#         try:
#             # Etape 1 : Récupérer le service Google Drive
#             st.info("📥 Étape 1 : Téléchargement des fichiers PDF depuis Google Drive...")
#             service = get_drive_service()
#             pdf_files = download_file(service)

#             if pdf_files:
#                 st.success(f"✅ {len(pdf_files)} fichiers PDF téléchargés.")
#             else:
#                 st.warning("❌ Aucun fichier PDF trouvé dans Google Drive.")

#             # Étape 2 : Traitement des fichiers PDF
#             st.info("⚙️ Étape 2 : Traitement des fichiers PDF...")
#             # Appel de la fonction de traitement des fichiers PDF ici, selon ton code de traitement
#             # Par exemple : process_pdf_files(pdf_files)

#             # Étape 3 : Téléversement du fichier Excel sur Google Drive
#             st.info("📦 Étape 3 : Téléversement du fichier Excel sur Google Drive...")
#             excel_path = os.path.join(os.getenv("PROJECT_PATH"), "output", "resultats.xlsx")
#             if os.path.exists(excel_path):
#                 upload_file_to_drive(service, excel_path)
#                 st.success("✅ Fichier Excel téléversé sur Google Drive.")
#             else:
#                 st.warning("❌ Fichier Excel non trouvé, assurez-vous que le traitement PDF a généré le fichier.")

#             # Étape 4 : Archivage des fichiers traités sur Google Drive
#             st.info("🗂️ Étape 4 : Archivage des fichiers traités sur Google Drive...")
#             file_ids = [file.split('/')[-1] for file in pdf_files]  # Ajuste cette logique si nécessaire
#             move_files_to_archive(service, file_ids)

#             st.success("✅ Workflow exécuté avec succès !")

#         except Exception as e:
#             st.error(f"❌ Une erreur est survenue pendant le workflow : {e}")
# else:
#     st.warning("Veuillez d'abord générer un token valide avant de lancer le workflow.")


# import streamlit as st
# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from auth_utils import get_drive_service, download_pdf_files, upload_file_to_drive, move_files_to_archive
# from process_pdf import process_pdf_files
# import time

# # Constantes (ou mieux: récupérées avec dotenv si tu préfères)
# SCOPES = ['https://www.googleapis.com/auth/drive']
# TOKEN_PATH = os.getenv("TOKEN_PATH")
# CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# st.set_page_config(page_title="PDF Workflow App", page_icon="📄")

# st.title("📄 Application de traitement PDF (Google Drive)")

# # --- Étape 1 : Vérification / génération du token ---
# def check_or_generate_token():
#     creds = None

#     # Token existe ?
#     if os.path.exists(TOKEN_PATH):
#         with open(TOKEN_PATH, 'rb') as token:
#             creds = pickle.load(token)

#     # Token valide ?
#     if creds and creds.valid:
#         return creds

#     # Token expiré mais renouvelable
#     if creds and creds.expired and creds.refresh_token:
#         try:
#             creds.refresh(Request())
#             with open(TOKEN_PATH, 'wb') as token:
#                 pickle.dump(creds, token)
#             return creds
#         except Exception as e:
#             st.warning(f"Erreur lors du rafraîchissement : {e}")
#             os.remove(TOKEN_PATH)

#     # Aucun token valide → authentification manuelle
#     st.info("Veuillez autoriser l'accès à Google Drive via votre compte Google...")
#     try:
#         flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
#         creds = flow.run_local_server(port=0)
#         with open(TOKEN_PATH, 'wb') as token:
#             pickle.dump(creds, token)
#         return creds
#     except Exception as e:
#         st.error(f"Erreur lors de l'authentification : {e}")
#         return None

# # Bouton pour vérifier le token
# if st.button("🔑 Vérifier ou générer le token Google Drive"):
#     creds = check_or_generate_token()
#     if creds:
#         st.success("✅ Token valide. Vous pouvez maintenant lancer le workflow.")
#     else:
#         st.error("❌ Impossible de valider ou de générer le token.")

# # --- Étape 2 : Exécution du workflow complet ---
# if os.path.exists(TOKEN_PATH):
#     st.divider()
#     st.subheader("🚀 Lancement du workflow")

#     if st.button("▶️ Lancer le workflow complet"):
#         try:
#             # Etape 1 : Récupérer le service Google Drive
#             st.info("📥 Étape 1 : Téléchargement des fichiers PDF depuis Google Drive...")
#             service = get_drive_service()
#             folder_id = os.getenv("INPUT_FOLDER_ID")  # Récupère l'ID du dossier d'entrée
#             pdf_files = download_pdf_files(service, folder_id)

#             if pdf_files:
#                 st.success(f"✅ {len(pdf_files)} fichiers PDF téléchargés.")
#             else:
#                 st.warning("❌ Aucun fichier PDF trouvé dans Google Drive.")

#             # Étape 2 : Traitement des fichiers PDF
#             st.info("⚙️ Étape 2 : Traitement des fichiers PDF...")
#             process_pdf_files(pdf_files)

#             # Étape 3 : Téléversement du fichier Excel sur Google Drive
#             st.info("📦 Étape 3 : Téléversement du fichier Excel sur Google Drive...")
#             excel_path = os.path.join(os.getenv("PROJECT_PATH"), "output", "resultats.xlsx")
#             if os.path.exists(excel_path):
#                 upload_file_to_drive(service, excel_path)
#                 st.success("✅ Fichier Excel téléversé sur Google Drive.")
#             else:
#                 st.warning("❌ Fichier Excel non trouvé, assurez-vous que le traitement PDF a généré le fichier.")

#             # Étape 4 : Archivage des fichiers traités sur Google Drive
#             st.info("🗂️ Étape 4 : Archivage des fichiers traités sur Google Drive...")
#             file_ids = [file.split('/')[-1] for file in pdf_files]  # Ajuste cette logique si nécessaire
#             move_files_to_archive(service, file_ids)

#             st.success("✅ Workflow exécuté avec succès !")

#         except Exception as e:
#             st.error(f"❌ Une erreur est survenue pendant le workflow : {e}")
# else:
#     st.warning("Veuillez d'abord générer un token valide avant de lancer le workflow.")

import streamlit as st
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
load_dotenv()

# Import des fonctions personnalisées
from auth_utils import get_drive_service, get_file_id_by_name, get_pdf_ids_in_folder, move_files_to_archive
from process_pdf import process_pdf_files
from clean_output import clean_excel_file
from move_processed_files import move_processed_files_to_archive

st.set_page_config(page_title="PDF Workflow App", page_icon="📄")
st.title("📄 Application de traitement PDF (Google Drive)")

# Constantes
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = os.getenv("TOKEN_PATH")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
INPUT_FOLDER_ID = os.getenv("INPUT_FOLDER_ID")
OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")
ARCHIVE_FOLDER_ID = os.getenv("ARCHIVE_FOLDER_ID")

# --- Étape 1 : Vérification / Génération du token ---
def check_or_generate_token():
    """Vérifie ou génère un token d'authentification Google Drive."""
    if not os.path.exists(TOKEN_PATH):
        return None

    try:
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
        if not creds or not creds.valid:
            return None
        return creds
    except Exception as e:
        return None

def refresh_or_generate_token():
    """Rafraîchit ou génère un nouveau token Google Drive."""
    st.info("🔄 Génération ou rafraîchissement du token...")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
        st.success("✅ Token généré avec succès !")
        return True
    except Exception as e:
        st.error(f"❌ Erreur lors de l'authentification : {e}")
        return False

# --- Étape 2 : Lancement du workflow ---
def run_full_workflow(service):
    try:
        st.info("🔄 Lancement du workflow complet...")

        # Étape 1 : Traitement des PDFs
        st.info("⚙️ Étape 1 : Traitement des fichiers PDF...")
        process_pdf_files()  # ✅ Aucun argument attendu

        # Étape 2 : Archivage des fichiers traités
        st.info("🗂️ Étape 2 : Archivage des fichiers traités...")
        input_folder_id = INPUT_FOLDER_ID
        archive_folder_id = ARCHIVE_FOLDER_ID

        file_ids = get_pdf_ids_in_folder(service, input_folder_id)
        if file_ids:
            moved_count = move_processed_files_to_archive(service, input_folder_id, archive_folder_id)
            st.success(f"✅ {moved_count} fichiers déplacés vers l'archive.")
        else:
            st.warning("⚠️ Aucun fichier à déplacer.")

        # Étape 3 : Nettoyage du fichier Excel
        st.info("🧼 Étape 3 : Nettoyage du fichier Excel...")
        clean_excel_file(service)

        st.success("🎉 Workflow terminé avec succès !")

    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {e}")

# --- Interface utilisateur ---
st.markdown("### 🔐 Étape 1 : Authentification")
if st.button("🔑 Vérifier ou générer le token Google Drive"):
    if check_or_generate_token():
        st.success("✅ Token valide. Vous pouvez lancer le workflow.")
    else:
        if refresh_or_generate_token():
            st.success("✅ Token mis à jour.")
        else:
            st.error("❌ Échec de la génération du token.")

st.markdown("### 🚀 Étape 2 : Lancer le workflow complet")

if os.path.exists(TOKEN_PATH):
    if st.button("▶️ Lancer le workflow complet"):
        service = get_drive_service()
        run_full_workflow(service)
else:
    st.warning("Veuillez d'abord générer un token valide avant de lancer le workflow.")