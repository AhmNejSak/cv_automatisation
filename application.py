# import streamlit as st
# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from dotenv import load_dotenv
# # load_dotenv()

# # Import des fonctions personnalisées
# from auth_utils import get_drive_service, get_file_id_by_name, get_pdf_ids_in_folder, move_files_to_archive
# from process_pdf import process_pdf_files
# from clean_output import clean_excel_file
# from move_processed_files import move_processed_files_to_archive

# st.set_page_config(page_title="PDF Workflow App", page_icon="📄")
# st.title("📄 Application de traitement PDF (Google Drive)")

# ###
# st.sidebar.title("⚙️ Configuration")
# env_choice = st.sidebar.selectbox("Choisissez l'environnement :", ["lyon", "lille", "test"])
# env_file = f".env.{env_choice}"

# load_dotenv(dotenv_path=env_file, override=True)
# ###



# SCOPES = ['https://www.googleapis.com/auth/drive']
# TOKEN_PATH = os.getenv("TOKEN_PATH")
# CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# INPUT_FOLDER_ID = os.getenv("INPUT_FOLDER_ID")
# OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")
# ARCHIVE_FOLDER_ID = os.getenv("ARCHIVE_FOLDER_ID")

# # --- Étape 1 : Vérification / Génération du token ---
# def check_or_generate_token():
#     """Vérifie ou génère un token d'authentification Google Drive."""
#     if not os.path.exists(TOKEN_PATH):
#         return None

#     try:
#         with open(TOKEN_PATH, 'rb') as token:
#             creds = pickle.load(token)
#         if not creds or not creds.valid:
#             return None
#         return creds
#     except Exception as e:
#         return None

# def refresh_or_generate_token():
#     """Rafraîchit ou génère un nouveau token Google Drive."""
#     st.info("🔄 Génération ou rafraîchissement du token...")
#     try:
#         flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
#         creds = flow.run_local_server(port=0)
#         with open(TOKEN_PATH, 'wb') as token:
#             pickle.dump(creds, token)
#         st.success("✅ Token généré avec succès !")
#         return True
#     except Exception as e:
#         st.error(f"❌ Erreur lors de l'authentification : {e}")
#         return False

# # --- Étape 2 : Lancement du workflow ---
# def run_full_workflow(service):
#     try:
#         st.info("🔄 Lancement du workflow complet...")

#         # Étape 1 : Traitement des PDFs
#         st.info("⚙️ Étape 1 : Traitement des fichiers PDF...")
#         process_pdf_files()  # ✅ Aucun argument attendu

#         # Étape 2 : Archivage des fichiers traités
#         st.info("🗂️ Étape 2 : Archivage des fichiers traités...")
#         input_folder_id = INPUT_FOLDER_ID
#         archive_folder_id = ARCHIVE_FOLDER_ID

#         file_ids = get_pdf_ids_in_folder(service, input_folder_id)
#         if file_ids:
#             moved_count = move_processed_files_to_archive(service, input_folder_id, archive_folder_id)
#             st.success(f"✅ {moved_count} fichiers déplacés vers l'archive.")
#         else:
#             st.warning("⚠️ Aucun fichier à déplacer.")

#         # Étape 3 : Nettoyage du fichier Excel
#         st.info("🧼 Étape 3 : Nettoyage du fichier Excel...")
#         clean_excel_file(service)

#         st.success("🎉 Workflow terminé avec succès !")

#     except Exception as e:
#         st.error(f"❌ Une erreur est survenue : {e}")

# # --- Interface utilisateur ---
# st.markdown("### 🔐 Étape 1 : Authentification")
# if st.button("🔑 Vérifier ou générer le token Google Drive"):
#     if check_or_generate_token():
#         st.success("✅ Token valide. Vous pouvez lancer le workflow.")
#     else:
#         if refresh_or_generate_token():
#             st.success("✅ Token mis à jour.")
#         else:
#             st.error("❌ Échec de la génération du token.")

# st.markdown("### 🚀 Étape 2 : Lancer le workflow complet")

# if os.path.exists(TOKEN_PATH):
#     if st.button("▶️ Lancer le workflow complet"):
#         service = get_drive_service()
#         run_full_workflow(service)
# else:
#     st.warning("Veuillez d'abord générer un token valide avant de lancer le workflow.")




import streamlit as st
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Import des fonctions personnalisées
from auth_utils import get_drive_service, get_file_id_by_name, get_pdf_ids_in_folder, move_files_to_archive
from process_pdf import process_pdf_files
from clean_output import clean_excel_file
from move_processed_files import move_processed_files_to_archive

st.set_page_config(page_title="PDF Workflow App", page_icon="📄")
st.title("📄 Application de traitement PDF (Google Drive)")

# --- Gestion de l'environnement dans session_state ---
if "env_choice" not in st.session_state:
    st.session_state["env_choice"] = "lyon"

env_options = ["lyon", "lille", "test"]
st.session_state["env_choice"] = st.sidebar.selectbox(
    "Choisissez l'environnement :", env_options,
    index=env_options.index(st.session_state["env_choice"])
)

env_file = f".env.{st.session_state['env_choice']}"
load_dotenv(dotenv_path=env_file, override=True)

# Fonction utilitaire pour récupérer toutes les variables utiles
def get_env_vars():
    return {
        "TOKEN_PATH": os.getenv("TOKEN_PATH"),
        "CREDENTIALS_PATH": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "INPUT_FOLDER_ID": os.getenv("INPUT_FOLDER_ID"),
        "OUTPUT_FOLDER_ID": os.getenv("OUTPUT_FOLDER_ID"),
        "ARCHIVE_FOLDER_ID": os.getenv("ARCHIVE_FOLDER_ID"),
    }

SCOPES = ['https://www.googleapis.com/auth/drive']

# --- Étape 1 : Vérification / Génération du token ---
def check_or_generate_token(token_path):
    """Vérifie ou génère un token d'authentification Google Drive."""
    if not os.path.exists(token_path):
        return None

    try:
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        if not creds or not creds.valid:
            return None
        return creds
    except Exception:
        return None

def refresh_or_generate_token(credentials_path, token_path):
    """Rafraîchit ou génère un nouveau token Google Drive."""
    st.info("🔄 Génération ou rafraîchissement du token...")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        st.success("✅ Token généré avec succès !")
        return True
    except Exception as e:
        st.error(f"❌ Erreur lors de l'authentification : {e}")
        return False

# --- Étape 2 : Lancement du workflow ---
def run_full_workflow():
    # Recharger les variables d'environnement (au cas où)
    load_dotenv(dotenv_path=env_file, override=True)
    env = get_env_vars()

    # Vérifier que toutes les variables sont définies
    if not all(env.values()):
        st.error("❌ Certaines variables d'environnement sont manquantes. Vérifiez votre fichier .env.")
        return

    try:
        st.info("🔄 Lancement du workflow complet...")

        # Étape 1 : Traitement des PDFs
        st.info("⚙️ Étape 1 : Traitement des fichiers PDF...")
        # Si process_pdf_files a besoin d'arguments, les passer ici explicitement
        process_pdf_files()

        # Étape 2 : Archivage des fichiers traités
        st.info("🗂️ Étape 2 : Archivage des fichiers traités...")
        input_folder_id = env["INPUT_FOLDER_ID"]
        archive_folder_id = env["ARCHIVE_FOLDER_ID"]

        service = get_drive_service()

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

env_vars = get_env_vars()

if st.button("🔑 Vérifier ou générer le token Google Drive"):
    token_path = env_vars["TOKEN_PATH"]
    credentials_path = env_vars["CREDENTIALS_PATH"]

    if check_or_generate_token(token_path):
        st.success("✅ Token valide. Vous pouvez lancer le workflow.")
    else:
        if refresh_or_generate_token(credentials_path, token_path):
            st.success("✅ Token mis à jour.")
        else:
            st.error("❌ Échec de la génération du token.")

st.markdown("### 🚀 Étape 2 : Lancer le workflow complet")

if env_vars["TOKEN_PATH"] and os.path.exists(env_vars["TOKEN_PATH"]):
    if st.button("▶️ Lancer le workflow complet"):
        run_full_workflow()
else:
    st.warning("Veuillez d'abord générer un token valide avant de lancer le workflow.")
